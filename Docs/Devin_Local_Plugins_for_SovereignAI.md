# Devin Local Plugins & Extensibility — Benefits for SovereignAI Workflows

**Based on**: Web research across 5 search queries + 5 deep-dive articles (Devin CLI beyond the defaults, Devin Skills docs, Devin Workflows docs, Zarar agent hooks, Ran the Builder agentic hooks)
**Date**: 2026-07-22
**Scope**: How Devin Local's plugin ecosystem (hooks, skills, MCP, subagents, plugins) can strengthen the SovereignAI Planner workflow

---

## Executive Summary

Devin Local has a **5-layer extensibility model** that SovereignAI is currently underutilizing. The repo has 8 Devin skills and an old-format hooks config, but it's missing the new `.devin/hooks.v1.json` format (Plan 35.1 was supposed to add this but hasn't shipped yet), has no MCP server integration, no subagent configuration, and no plugin-system usage.

Adopting the full Devin Local extensibility stack would address **3 of my earlier improvement recommendations** (runtime guardrails, durable execution, tool-design discipline) with native platform support instead of custom Python scripts. The biggest win: **hooks make hard gates unbypassable** — currently an agent can skip `python .Planner/scripts/hard_gates/run_phase_gates.py` and post a fake compliance line; with PreToolUse hooks, the gate runs automatically on every file write and the agent cannot proceed if it fails.

---

## Devin Local's 5 Extensibility Layers

### Layer 1: Skills (✅ partially used in SovereignAI)

**What they are**: Self-contained units of functionality — YAML frontmatter + markdown body. They bundle prompts, tool access, permissions, and workflows into a reusable slash command.

**Format** (`.devin/skills/{name}/SKILL.md`):
```yaml
---
name: review
description: Review staged changes for issues
allowed-tools: [read, grep, glob, exec]
permissions:
  allow: [Exec(git diff), Exec(git log)]
model: opus              # optional model override
subagent: true           # optional: run as independent worker
triggers: [user]         # optional: prevent autonomous invocation
---
Review the current changes: !`git diff --staged`
Check for: 1. Logic errors 2. Security issues 3. Style inconsistencies
```

**Key features**:
- `allowed-tools` restricts tool access per skill (security)
- `model` overrides the model per skill (cost optimization — use SWE for light tasks, Opus for deep reasoning)
- `subagent: true` runs the skill in its own context window (parallel work, context isolation)
- `triggers: [user]` prevents the agent from auto-invoking (manual only)
- Dynamic content: `$1`, `$ARGUMENTS`, `@file.md`, `` !`command` ``
- Invoked via `/{skill-name}` in the REPL

**Sources**: [Devin Skills Docs](https://docs.devin.ai/cli/extensibility/skills/overview), [Sulat article](https://ai.sulat.com/devin-cli-beyond-the-defaults-3487abea6596)

---

### Layer 2: Hooks (⚠️ old format only in SovereignAI)

**What they are**: The policy enforcement layer. Run shell commands or LLM prompts at specific lifecycle events. **Cannot be bypassed by the agent** — they execute deterministically on every matching tool call.

**Format** (`.devin/hooks.v1.json` — Claude Code compatible):
```json
{
  "PreToolUse": [
    {
      "matcher": "exec",
      "hooks": [
        { "type": "command", "command": "./scripts/check-command.sh" }
      ]
    }
  ]
}
```

**Hook events** (7 lifecycle points):
| Event | When it fires | Use case |
|-------|---------------|----------|
| `PreToolUse` | Before any tool call | Block destructive commands, validate inputs |
| `PostToolUse` | After any tool call | Run tests, format code, log actions |
| `SessionStart` | When session begins | Load context, resume state, inject project info |
| `SessionEnd` | When session ends | Generate attestation, archive traces, checkpoint |
| `Stop` | When agent wants to stop | Block stop until tests pass, gates verified |
| `PermissionRequest` | When agent requests permission | Auto-approve safe ops, prompt for risky ones |
| `UserPromptSubmit` | When user submits a prompt | Inject context, enforce scope |

**How blocking works**:
- Hook script receives JSON on stdin: `{"hook_event_name": "PreToolUse", "tool_name": "exec", "tool_input": {"command": "rm -rf /tmp"}}`
- **Exit code 0**: allow tool call
- **Exit code 2**: BLOCK tool call (reason from stderr is shown to agent)
- **Exit code 1**: log warning but allow
- Or output JSON to stdout: `{"decision": "block", "reason": "Destructive command blocked"}`

**Matcher is regex** (not glob):
- `"exec"` matches any tool containing "exec"
- `"^exec$"` matches exact `exec` tool
- `"^mcp__github__.*"` matches all GitHub MCP tools
- `"Write|Edit"` matches both Write and Edit tools

**Prompt-type hooks** (for contextual decisions):
```json
{
  "PreToolUse": [
    { "matcher": "exec", "hooks": [
      { "type": "prompt", "prompt": "The agent wants to run: {{tool_input.command}}. Is this safe? Respond with {\"decision\": \"approve\"} or {\"decision\": \"block\", \"reason\": \"...\"}." }
    ]}
  ]
}
```

**Sources**: [Sulat article](https://ai.sulat.com/devin-cli-beyond-the-defaults-3487abea6596), [Zarar blog](https://zarar.dev/agent-hooks-deterministic-guardrails-for-ai-generated-code), [Ran the Builder](https://ranthebuilder.cloud/blog/agentic-coding-hooks-deterministic-ai-guardrails)

---

### Layer 3: MCP Servers (❌ not used in SovereignAI)

**What they are**: Model Context Protocol servers — external tool servers that expose tools to the agent. Tools appear as `mcp__<server>__<tool>` (e.g., `mcp__github__create_issue`).

**Adding servers**:
```bash
# GitHub OAuth
devin mcp add github https://api.githubcopilot.com/mcp/

# HTTP server
devin mcp add notion https://mcp.notion.com/mcp

# Scoped to project (committed to repo for team sharing)
devin mcp add -s project sentry https://mcp.sentry.dev/mcp
```

**Scopes**:
- `local` (default): saved to `.devin/config.local.json` (gitignored)
- `project`: saved to `.devin/config.json` (committed — teammates share)
- `user`: global across all projects

**Sources**: [Devin MCP docs](https://docs.devin.ai/desktop/cascade/mcp), [Sulat article](https://ai.sulat.com/devin-cli-beyond-the-defaults-3487abea6596)

---

### Layer 4: Subagents (❌ not used in SovereignAI)

**What they are**: Skills with `subagent: true` run as independent workers with their own context windows instead of injecting inline. Enables parallel work and context isolation.

**Why it matters** (from Anthropic's multi-agent research): subagents with separate context windows outperform single agents by 90% on breadth-first queries. Token usage explains 80% of performance variance — distributing work across subagents scales token usage for tasks that exceed single-agent limits.

**SovereignAI application**: The Round Table's 6 panelists are conceptually subagents but currently run as separate manual chats. With `subagent: true` skills, the Planner could spawn 6 panelist subagents programmatically, each with its own context window, competency assignment, and web search access.

---

### Layer 5: Plugin System (❌ not used — new, in preview)

**What it is**: Devin Local's newest extensibility layer (released in preview, enterprise opt-in per the changelog). A plugin can:
- Require other plugins (auto-installed)
- Endorse optional plugins
- Forbid other plugins (curated, conflict-free stacks)

**Status**: Too early for production use, but worth monitoring. The "require/forbid" model is interesting for SovereignAI because it would let you ship a `sovereignai-planner` plugin that requires the hard-gate hooks and forbids conflicting hook configs.

**Source**: [Devin Changelog](https://docs.devin.ai/desktop/changelog)

---

## Current State in SovereignAI Repo

| Layer | Status | Files |
|-------|--------|-------|
| Skills | ✅ 8 skills exist | `.devin/skills/{open,close,executor,verify,scan,planner,reviewer,researcher}/SKILL.md` |
| Hooks (old format) | ⚠️ Basic config | `.devin/config.json` has `before_file_write`, `after_skill_invoke`, `session_end` |
| Hooks (new format) | ❌ Missing | `.devin/hooks.v1.json` does NOT exist (Plan 35.1 was supposed to add it) |
| MCP servers | ❌ None configured | No `devin mcp add` commands documented |
| Subagents | ❌ None configured | No skills have `subagent: true` |
| Plugin system | ❌ Not used | Too new, but worth tracking |

### Existing Hook Scripts (referenced but not wired to new format)

The repo references these hook scripts in `.devin/config.json` and skill files:
- `.agent/executor/hooks/check_manifest.py` — validates file writes against plan manifest
- `.agent/executor/hooks/append_trace.py` — appends to execution trace
- `.agent/executor/hooks/verify_attestation.py` — verifies attestation at session end
- `.agent/executor/hooks/preflight_check.py` — pre-flight validation

These exist conceptually but the paths point to `.agent/executor/hooks/` which doesn't exist in the current repo (it was removed in the redesign). The hooks are referenced but not implemented.

---

## Concrete Opportunities for SovereignAI

### Opportunity 1: Migrate to hooks.v1.json (HIGH PRIORITY)

**Current problem**: Hard gates are invoked manually (`python .Planner/scripts/hard_gates/run_phase_gates.py --phase 1`). An agent can skip the invocation and post a fake compliance line. The old `.devin/config.json` hooks use the deprecated format and point to non-existent scripts.

**Solution**: Create `.devin/hooks.v1.json` that auto-runs hard gates on every plan file write:

```json
{
  "PreToolUse": [
    {
      "matcher": "Write|Edit",
      "hooks": [
        {
          "type": "command",
          "command": "python3 .Planner/scripts/hooks/pretooluse_plan_write.py"
        }
      ]
    },
    {
      "matcher": "exec",
      "hooks": [
        {
          "type": "command",
          "command": "python3 .Planner/scripts/hooks/pretooluse_exec_block.py"
        }
      ]
    }
  ],
  "PostToolUse": [
    {
      "matcher": "Write|Edit",
      "hooks": [
        {
          "type": "command",
          "command": "python3 .Planner/scripts/hooks/posttooluse_plan_write.py"
        }
      ]
    }
  ],
  "SessionStart": [
    {
      "matcher": "",
      "hooks": [
        {
          "type": "command",
          "command": "python3 .Planner/scripts/hooks/session_start.py"
        }
      ]
    }
  ],
  "SessionEnd": [
    {
      "matcher": "",
      "hooks": [
        {
          "type": "command",
          "command": "python3 .Planner/scripts/hooks/session_end.py"
        }
      ]
    }
  ],
  "Stop": [
    {
      "matcher": "",
      "hooks": [
        {
          "type": "command",
          "command": "python3 .Planner/scripts/hooks/stop_gate_check.py"
        }
      ]
    }
  ]
}
```

**Hook script examples**:

`pretooluse_plan_write.py` (blocks writes to plans/ that fail hard gates):
```python
#!/usr/bin/env python3
import sys, json, subprocess

event = json.load(sys.stdin)
tool_name = event.get("tool_name", "")
tool_input = event.get("tool_input", {})
file_path = tool_input.get("file_path", "") or tool_input.get("path", "")

# Only validate writes to plan files
if not file_path.startswith("plans/") or not file_path.endswith(".md"):
    sys.exit(0)  # Allow non-plan writes

# Run hard gates for the current phase
result = subprocess.run(
    ["python3", ".Planner/scripts/hard_gates/run_phase_gates.py", "--phase", "5"],
    capture_output=True, text=True
)

if result.returncode != 0:
    # Exit 2 = BLOCK. Reason shown to agent.
    print(json.dumps({
        "decision": "block",
        "reason": f"Hard gates failed. Plan file write blocked.\n{result.stdout}\n{result.stderr}"
    }))
    sys.exit(2)

sys.exit(0)  # Allow
```

`stop_gate_check.py` (blocks agent stop until all gates pass):
```python
#!/usr/bin/env python3
import sys, json, subprocess

# Block Stop until all phase gates have passed
result = subprocess.run(
    ["python3", ".Planner/scripts/hard_gates/run_phase_gates.py", "--phase", "6"],
    capture_output=True, text=True
)

if result.returncode != 0:
    print(json.dumps({
        "decision": "block",
        "reason": f"Cannot stop — Phase 6 hard gates not passed:\n{result.stdout}"
    }))
    sys.exit(2)

sys.exit(0)
```

**Benefit**: Hard gates become **unbypassable**. The agent cannot write a plan file that fails HG-7/HG-8/HG-9, and cannot stop the session until HG-10 through HG-13 pass. This directly addresses my earlier "Runtime Guardrails" recommendation.

---

### Opportunity 2: MCP Server for Round Table Database (HIGH PRIORITY)

**Current problem**: The Round Table SQLite database is queried manually via Python scripts. The Planner/Reviewer agents can't directly query findings — they have to invoke a script and parse output.

**Solution**: Build a custom MCP server that exposes the Round Table database as tools:

```bash
# Add to project scope (committed for team sharing)
devin mcp add -s project roundtable python3 .Planner/roundtable/mcp_server.py
```

**Tools exposed**:
- `mcp__roundtable__get_findings(plan_id, severity?)` — query findings by plan and severity
- `mcp__roundtable__add_finding(review_id, category, severity, description)` — insert finding
- `mcp__roundtable__get_panelist_scores(plan_id)` — query panelist performance
- `mcp__roundtable__export_findings_json(batch_id)` — export findings
- `mcp__roundtable__get_unaddressed_critical()` — get all unaddressed CRITICAL findings

**Benefit**: Agents can query findings directly in conversation: "Show me all unaddressed CRITICAL findings for plan 35" becomes a single tool call instead of a script invocation + output parsing. This also enables the Reviewer's pattern analysis workflow to query findings programmatically.

---

### Opportunity 3: Subagent Skills for Round Table Panelists (MEDIUM PRIORITY)

**Current problem**: The Round Table's 6 panelists run as separate manual chats. The user copies prompts to each panelist, collects responses, and pastes them back. This is labor-intensive and doesn't scale.

**Solution**: Create 6 panelist skills with `subagent: true`:

`.devin/skills/panelist-technical/SKILL.md`:
```yaml
---
name: panelist-technical
description: Round Table panelist for Technical Architecture competency
subagent: true
allowed-tools: [read, grep, glob, exec, web_search]
model: opus
triggers: [user]
---
You are a Round Table panelist assigned the Technical Architecture competency.

Plan to review: $ARGUMENTS

## Your Assignment
- Competency: Technical Architecture (COMP-001)
- Use the 4-point rubric from .Planner/roundtable/templates/SCORING_RUBRIC_TEMPLATE.md
- Use web search to validate technical assumptions and best practices
- Score independently before seeing other panelists' feedback

## Output Format
Return findings as JSON:
{
  "findings": [...],
  "verdict": "Pass|Conditional|Block",
  "rubric_score": 1-4,
  "panelist_score": 1-100,
  "web_search_used": true,
  "citations": [...]
}
```

**Invocation**: Planner runs `/panelist-technical plans/plan-35-Rev1.md` — Devin spawns a subagent with its own context window that reads the plan, does web research, and returns structured findings.

**Benefit**: 6 panelists can run in parallel, each with isolated context. This is exactly the pattern Anthropic's research found effective (90% improvement on breadth-first queries). It also makes the Round Table reproducible — same plan, same prompts, comparable results.

---

### Opportunity 4: SessionStart Hook for Workflow State Recovery (MEDIUM PRIORITY)

**Current problem**: If a session crashes mid-Phase-6, there's no mechanism to resume from where you left off. The old AI_HANDOFF.md had a "paste transcript between sessions" rule — the new workflow dropped it.

**Solution**: `SessionStart` hook queries the `workflow_state` table (from my earlier durable-execution recommendation) and prints resume instructions:

`session_start.py`:
```python
#!/usr/bin/env python3
import sys, json, sqlite3
from pathlib import Path

db_path = Path(".Planner/roundtable/database/roundtable.db")
if not db_path.exists():
    sys.exit(0)  # No DB, fresh start

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Find the most recent in-progress workflow
cursor.execute("""
    SELECT plan_id, phase, status, completed_at
    FROM workflow_state
    WHERE status = 'in_progress'
    ORDER BY started_at DESC LIMIT 1
""")
row = cursor.fetchone()
conn.close()

if row:
    plan_id, phase, status, completed_at = row
    # Inject context into the session via stdout
    print(json.dumps({
        "hookSpecificOutput": {
            "additionalContext": f"""
--- WORKFLOW RESUMPTION ---
Plan {plan_id} was in-progress at {phase} (status: {status}).
Resume from the last completed phase. Do NOT restart from Phase 1.
Query workflow_state table for full checkpoint details.
"""
        }
    }))
sys.exit(0)
```

**Benefit**: Sessions become resumable. An agent that crashes mid-Phase-6.2 (Panelist Evaluation) will, on restart, automatically know it was in Phase 6.2 and which panelists have already submitted reviews.

---

### Opportunity 5: Stop Hook for Gate Enforcement (HIGH PRIORITY)

**Current problem**: An agent can post "✅ Gate PLAN-6.10 PASS" and stop without actually running the gates. The compliance line is in the chat but no script verified it.

**Solution**: `Stop` hook runs all phase gates and blocks stop if any fail:

```json
{
  "Stop": [
    {
      "matcher": "",
      "hooks": [
        {
          "type": "command",
          "command": "python3 .Planner/scripts/hooks/stop_gate_check.py"
        }
      ]
    }
  ]
}
```

**Caveat from the research**: "Be careful with Stop hooks that always block. If the condition is never satisfied, the agent loops. This causes token wastage and unnecessary costs." Make sure the Stop hook has a clear pass condition and an escape hatch (e.g., user override via `--force` flag).

**Benefit**: The agent literally cannot stop until all hard gates pass. This is the strongest possible enforcement — stronger than manual invocation, stronger than PreToolUse hooks (which only fire on tool calls).

---

### Opportunity 6: PermissionRequest Hook for Auto-Approving Safe Operations (LOW PRIORITY)

**Current problem**: Devin's Normal mode prompts for every write/exec. This is tedious for repetitive operations like running hard gate scripts.

**Solution**: `PermissionRequest` hook auto-approves known-safe operations:

```json
{
  "PermissionRequest": [
    {
      "matcher": "exec",
      "hooks": [
        {
          "type": "command",
          "command": "python3 .Planner/scripts/hooks/auto_approve_safe.py"
        }
      ]
    }
  ]
}
```

`auto_approve_safe.py`:
```python
#!/usr/bin/env python3
import sys, json

event = json.load(sys.stdin)
cmd = event.get("tool_input", {}).get("command", "")

# Auto-approve hard gate scripts, linting, testing
safe_patterns = [
    "python3 .Planner/scripts/hard_gates/",
    "python3 .Planner/scripts/soft_gates/",
    "python3 .Planner/roundtable/",
    "ruff check", "mypy", "pytest", "git status", "git log", "git diff"
]

if any(cmd.startswith(p) for p in safe_patterns):
    print(json.dumps({"decision": "approve"}))
else:
    sys.exit(0)  # Fall through to normal permission flow
```

**Benefit**: Reduces approval fatigue. Agents can run gate scripts, linters, and tests without prompting. Risky commands (git push, rm, etc.) still prompt.

---

### Opportunity 7: Prompt-Type Hooks for Contextual Decisions (LOW PRIORITY)

**Current problem**: Some gate decisions are too contextual for scripts. For example, "is this brief section specific enough?" requires judgment, not regex matching.

**Solution**: Use `type: "prompt"` hooks that delegate to an LLM:

```json
{
  "PreToolUse": [
    {
      "matcher": "Write",
      "hooks": [
        {
          "type": "prompt",
          "prompt": "The agent wants to write to {{tool_input.file_path}}. Content preview: {{tool_input.content}}. Does this content meet the quality bar in .Planner/roundtable/templates/BRIEF_TEMPLATE.md? Respond with {\"decision\": \"approve\"} or {\"decision\": \"block\", \"reason\": \"...\"}."
        }
      ]
    }
  ]
}
```

**Benefit**: Catches qualitative issues that scripts can't. Use sparingly — prompt hooks cost tokens on every matching tool call.

---

### Opportunity 8: UserPromptSubmit Hook for Scope Enforcement (MEDIUM PRIORITY)

**Current problem**: An agent might accept a user request that's out of scope for its role (e.g., Planner accepting an execution task).

**Solution**: `UserPromptSubmit` hook injects scope reminders:

```json
{
  "UserPromptSubmit": [
    {
      "matcher": "",
      "hooks": [
        {
          "type": "command",
          "command": "python3 .Planner/scripts/hooks/scope_reminder.py"
        }
      ]
    }
  ]
}
```

`scope_reminder.py` reads the current agent's AGENTS.md and injects a scope reminder into the context before the agent processes the user's prompt.

**Benefit**: Enforces GR2 (Agent Scope) deterministically — the agent is reminded of its scope before every user prompt, not just when it remembers to check.

---

## Prioritized Implementation Roadmap

### Tier 1 — Ship First (Unbypassable Enforcement)

| # | Opportunity | Effort | Impact | Dependencies |
|---|-------------|--------|--------|--------------|
| 1 | Migrate to `.devin/hooks.v1.json` with PreToolUse, Stop, SessionEnd hooks | Medium (4 hook scripts + JSON config) | Very High (hard gates become unbypassable) | Fix existing hook script paths |
| 5 | Stop hook for gate enforcement | Low (1 script) | Very High (agent cannot stop until gates pass) | Part of #1 |
| 4 | SessionStart hook for workflow recovery | Medium (1 script + workflow_state table) | High (resumable sessions) | My durable-execution recommendation |

### Tier 2 — Ship Second (Better Tooling)

| # | Opportunity | Effort | Impact | Dependencies |
|---|-------------|--------|--------|--------------|
| 2 | MCP server for Round Table database | Medium (1 MCP server, ~6 tools) | High (agents query findings directly) | Fix database_manager.py indentation bug |
| 3 | Subagent skills for 6 panelists | Medium (6 skill files) | High (parallel, reproducible Round Table) | None |
| 8 | UserPromptSubmit hook for scope enforcement | Low (1 script) | Medium (deterministic GR2 enforcement) | None |

### Tier 3 — Ship Last (Polish)

| # | Opportunity | Effort | Impact | Dependencies |
|---|-------------|--------|--------|--------------|
| 6 | PermissionRequest hook for auto-approve | Low (1 script) | Medium (less approval fatigue) | None |
| 7 | Prompt-type hooks for qualitative checks | Low (JSON config) | Low-Medium (catches qualitative issues) | None — but use sparingly (token cost) |
| — | Plugin system adoption | N/A (too new) | Future (curated, conflict-free stacks) | Wait for stable release |

---

## How This Maps to My Earlier Improvement Recommendations

| Earlier Recommendation | Devin Local Native Solution |
|------------------------|----------------------------|
| Improvement #5: Tool-Description Discipline | Skills' `allowed-tools`, `model`, `subagent` frontmatter standardizes tool descriptions |
| Improvement #8: Runtime Guardrail Hooks | `.devin/hooks.v1.json` with PreToolUse + Stop hooks — **this is the native implementation** |
| Improvement #2: Durable Execution & Checkpointing | SessionStart hook + workflow_state table — **Devin provides the hook; you provide the table** |
| Improvement #6: Self-Check Phase 6.0 | Could be a `subagent: true` skill that runs the self-check in its own context |

**Key insight**: Devin Local's hooks layer is the platform-native way to achieve what I was recommending be built with custom Python scripts. The hooks are unbypassable, deterministic, and fire at exactly the right lifecycle points. SovereignAI should adopt hooks.v1.json as the primary enforcement mechanism and treat the Python gate scripts as the hook implementations (not as standalone tools the agent must remember to invoke).

---

## Risks and Considerations

### Risk 1: Stop Hook Infinite Loops
**Problem**: If a Stop hook's pass condition is never satisfied, the agent loops indefinitely, burning tokens.
**Mitigation**: Always provide an escape hatch. The Stop hook should check for a `--force-stop` flag or a user override mechanism. Also, log Stop hook failures to the audit database for debugging.

### Risk 2: Hook Script Failures Cascade
**Problem**: If a hook script itself crashes (e.g., database_manager.py has an IndentationError), the hook blocks all matching tool calls.
**Mitigation**: Hook scripts should fail-open (exit 0) on internal errors and log the failure. Only fail-closed (exit 2) on intentional gate failures. Example:
```python
try:
    # Run gate validation
    if gate_fails:
        sys.exit(2)
    sys.exit(0)
except Exception as e:
    # Internal error — fail open, log it
    print(f"⚠️  Hook internal error: {e}", file=sys.stderr)
    sys.exit(0)  # Don't block on hook bugs
```

### Risk 3: Token Cost of Prompt-Type Hooks
**Problem**: Prompt hooks invoke an LLM on every matching tool call. At scale, this doubles token usage.
**Mitigation**: Use prompt hooks sparingly — only for decisions that truly require judgment. Use command hooks (scripts) for everything else.

### Risk 4: MCP Server Security
**Problem**: An MCP server exposing database write access could be abused by a compromised agent.
**Mitigation**: Use Devin's permission system to restrict which MCP tools the agent can invoke. Add `permissions: deny` entries for dangerous MCP tools.

### Risk 5: Subagent Context Isolation
**Problem**: Subagents have their own context windows — they can't see the parent agent's context. This is a feature (isolation) but can cause subagents to miss important context.
**Mitigation**: Pass all necessary context in the subagent's prompt. Use `@file.md` includes to load governance docs into the subagent's context.

---

## Sources Cited

1. JP Caparas — "Devin CLI beyond the defaults" (Jun 2026) — https://ai.sulat.com/devin-cli-beyond-the-defaults-3487abea6596
2. Devin Docs — "Skills Overview" — https://docs.devin.ai/cli/extensibility/skills/overview
3. Devin Docs — "Workflows" — https://docs.devin.ai/desktop/cascade/workflows
4. Devin Docs — "Changelog" (plugin system announcement) — https://docs.devin.ai/desktop/changelog
5. Devin Docs — "MCP Integration" — https://docs.devin.ai/desktop/cascade/mcp
6. Zarar — "Don't rely on instructions, use Agent Hooks to enforce guardrails" (Jun 2026) — https://zarar.dev/agent-hooks-deterministic-guardrails-for-ai-generated-code
7. Ran the Builder — "Agentic Coding Hooks: Deterministic AI Guardrails" — https://ranthebuilder.cloud/blog/agentic-coding-hooks-deterministic-ai-guardrails
8. Anthropic Engineering — "How we built our multi-agent research system" (subagent pattern) — https://www.anthropic.com/engineering/multi-agent-research-system
9. AY Automate — "Devin vs Claude Code (2026): Autonomous Agents Compared" — https://www.ayautomate.com/blog/devin-vs-claude-code
10. Morph LLM — "Claude Code Hooks (2026)" (hook format reference) — https://www.morphllm.com/claude-code-hooks

---

## Bottom Line

Devin Local's extensibility stack is the **missing enforcement layer** SovereignAI needs. The current workflow relies on agents remembering to invoke gate scripts — which is bypassable. Hooks make those same gates fire automatically on every tool call, every session start, every stop attempt. This is the difference between "the agent should validate" and "the agent cannot avoid validating."

The highest-leverage move is to ship `.devin/hooks.v1.json` with PreToolUse (block bad writes), Stop (block premature stop), and SessionEnd (checkpoint state) hooks. That single file, plus 4 hook scripts, would make the entire hard gate system unbypassable — addressing the root cause of why my original review found that "no hard gate would actually block a malformed plan."

**Recommended next step**: Implement Tier 1 (hooks.v1.json + 4 hook scripts + SessionStart recovery). This is 1-2 days of work and converts the entire hard gate system from "manually invoked, bypassable" to "automatically enforced, unbypassable."

---

*End of recommendations.*
