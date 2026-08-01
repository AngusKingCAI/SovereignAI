# Building a Rule-Adherence-First Harness from Scratch

**A Devin CLI-Focused Design Blueprint**

| | |
|---|---|
| **Prepared By** | Z.ai Analysis Engine |
| **Date** | 2026-08-01 |
| **Document Type** | Design Blueprint |
| **Version** | V1.0 |
| **Research Base** | 9 web searches + 7 deep-read sources (see §12 Citations) |

---

## Table of Contents

1. [Executive Design Philosophy](#1-executive-design-philosophy)
2. [Research Foundation](#2-research-foundation)
3. [The Six-Layer Architecture](#3-the-six-layer-architecture)
4. [Layer 1: Constitutional Principles](#4-layer-1-constitutional-principles)
5. [Layer 2: Policy Cards (Machine-Readable Rules)](#5-layer-2-policy-cards-machine-readable-rules)
6. [Layer 3: Enforcement Hooks (Policy Decision Points)](#6-layer-3-enforcement-hooks-policy-decision-points)
7. [Layer 4: Validation Pipeline](#7-layer-4-validation-pipeline)
8. [Layer 5: Audit & Feedback Loop](#8-layer-5-audit--feedback-loop)
9. [**Layer 6: Rigorous Testing & Continuous Improvement**](#9-layer-6-rigorous-testing--continuous-improvement)
10. [Token Optimization Strategy](#10-token-optimization-strategy)
11. [Directory Structure (From Scratch)](#11-directory-structure-from-scratch)
12. [Implementation Roadmap](#12-implementation-roadmap)
13. [Anti-Patterns to Avoid](#13-anti-patterns-to-avoid)
14. [Research Citations](#14-research-citations)

---

## 1. Executive Design Philosophy

**One sentence:** Prompts suggest, hooks enforce, schemas validate, audits verify — and rules must be machine-readable before they can be machine-enforced.

If you are building a harness from scratch with rule adherence as the **primary** priority, the single most important design decision is this: **stop writing rules as prose markdown**. Prose rules are interpreted by the model, not enforced by the runtime. The model is probabilistic — it will follow your rules most of the time, but "most of the time" is not adherence. A rule-adherence-first harness treats rules as data (YAML/JSON), validates them against schemas, enforces them through deterministic hooks, and audits them through a closed feedback loop.

This design is built around six principles derived from the research:

1. **The Probabilistic-to-Deterministic Boundary** — Every rule must be classified as either "advisory" (enforced by prompt, acceptable when missed) or "binding" (enforced by hook, never missed). There is no middle ground. Rules that are "sometimes binding" are just advisory rules you haven't been honest about.

2. **Policy as Data, Not Prose** — Rules live in YAML Policy Cards with explicit schemas, not in markdown ALWAYS/NEVER lists. A markdown rule says "the agent should do X." A Policy Card says "when tool=T and condition=C, deny with reason=R." The first is a suggestion; the second is a function.

3. **The Policy Decision Point Pattern** — Every tool call passes through a Policy Decision Point (PDP) before execution. The PDP evaluates the call against the active Policy Cards and returns allow/deny/deny-with-reason. The model never gets to vote on binding rules.

4. **Progressive Disclosure for Token Efficiency** — The constitution (~500 tokens) is always in context. The active agent's rule *index* (~300 tokens) is always in context. Full rule definitions are loaded on-demand by skills. Session-start token budget: approximately 800 tokens for governance — compared to 14,000+ in a typical prose-rules harness.

5. **Declare-Do-Audit Lifecycle** — Rules are declared in version-controlled Policy Cards, enforced at runtime by hooks, and audited continuously by a violation-collection pipeline that feeds back into rule updates. This closed loop is what prevents the "rules drift from reality" failure mode that every prose-based harness eventually hits.

6. **Test Everything, Trust Nothing** — Every layer of the harness (constitution, Policy Cards, PDP hooks, validators, audit pipeline) is tested independently and in integration. Rule changes ship behind test cases. Hook behavior is verified by mutation testing (the hook must still deny when the rule is deliberately broken). The harness runs property-based tests against itself. Without this layer, the previous five layers are just a well-documented bet that the code works.

The result is a harness where rule adherence is not a property of the model's attention but a property of the system's architecture — and where that architecture is continuously verified to actually work.

---

## 2. Research Foundation

This design synthesizes findings from nine web searches and seven deep-read sources covering Claude Code/Devin CLI hooks, policy-as-code engines (OPA/Cedar/Rego), the Policy Cards academic paper, Anthropic's Agent Skills architecture, Constitutional AI, and token optimization research. The key findings that shaped the design:

### 2.1 Prompts Are Probabilistic; Hooks Are Deterministic

The most important finding comes from the "Hooks: The Enforcement Layer" article (ranjankumar.in, April 2026), which documents a real incident where Claude executed `rm -rf tests/ patches/ plan/ ~/` — the trailing `~/` wiped a developer's entire Mac. The CLAUDE.md file had a rule: "never run destructive commands." The model had read it and followed it hundreds of times. Then, in one context-heavy session, it didn't. The article's central insight: **"Prompts suggest. Hooks enforce."** A PreToolUse hook that blocks `rm -rf` does not rely on the model remembering your policy — it runs as a separate process every time the pattern appears, regardless of conversation length, context state, or task framing. This is the "Probabilistic-to-Deterministic Boundary" concept: wherever the agent calls tools, you need a layer that enforces what the model cannot be trusted to enforce through reasoning alone.

The "Deterministic AI Guardrails" article (ranthebuilder.cloud, June 2026) reinforces this with a critical caveat: **use hooks sparingly**. "Everything you feed an LLM is, in the end, a suggestion. Compliance drops as sessions grow longer. Hooks add the determinism that prompts cannot — but only for the cases where a rule has to hold every single time." Too many hooks add latency, token bloat (from hook output injected into context), and maintenance burden. The design principle: hooks are for binding rules only; everything else stays as advisory prompt rules.

### 2.2 The Model Is Not Your Authorization Layer

The "Policy-as-Code for Agents" article (tianpan.co, April 2026) argues that treating the system prompt as a policy expression is seductive but broken: "The prompt is interpreted, not enforced. A sufficiently tricky input, a tool description that subtly hints at capability, or a goal that conflicts with the rule, and the model's judgment produces a policy violation that looks identical in the transcript to a compliant action." The article advocates a Policy Decision Point architecture: a dedicated engine (OPA with Rego, AWS Cedar, or similar) sits in front of every tool call and answers one question: *given this principal, this tool, these arguments, this context — is the action allowed?* The agent runtime never gets to vote. For our harness, we adapt this pattern: the PDP is not a separate OPA server (too heavy for a local-first Devin CLI harness) but a Python hook script that loads Policy Cards and evaluates them deterministically.

### 2.3 Policy Cards: Machine-Readable Governance

The most rigorous source is the arxiv paper "Policy Cards: Machine-Readable Runtime Governance for Autonomous AI Agents" (Mavračić, October 2025). It introduces Policy Cards as "a machine-readable, deployment-layer standard for expressing operational, regulatory, and ethical constraints for AI agents." Key contributions adopted in our design:

- **Policy Cards sit with the agent** at runtime and tell it what it must and must not do — they become "an integral part of the deployed agent."
- **They encode allow/deny rules** (we implement this subset of the paper's definition).
- **Each card is validated automatically, version-controlled, and linked to runtime enforcement.**
- **The Declare-Do-Audit lifecycle**: Declare (bind policy to agent at deploy time) → Do (execute with evidence capture) → Audit (continuous assurance against declared policy).
- **Schema-based validation in CI** — every Policy Card must pass JSON Schema validation before merge.

**Note:** The full Policy Cards paper defines four constitutive elements: allow/deny rules, obligations, evidentiary requirements, and crosswalk mappings to governance frameworks (NIST AI RMF, ISO/IEC 42001, EU AI Act). This design implements only the allow/deny rules component, which is sufficient for code-governance contexts. The other elements (obligations, evidentiary requirements, assurance-framework crosswalks) are omitted as they are more relevant to regulatory compliance scenarios.

### 2.4 Progressive Disclosure for Token Efficiency

Anthropic's "Equipping Agents for the Real World with Agent Skills" (October 2025) documents the progressive disclosure pattern: at startup, the agent pre-loads only the `name` and `description` of every installed skill into its system prompt. "This metadata is the first level of progressive disclosure: it provides just enough information for Claude to know when each skill should be used without loading all of it into context." If Claude thinks the skill is relevant, it loads the full SKILL.md. This two-tier loading pattern is the key to keeping session-start token costs low while preserving capability. We extend it to three tiers for rules: constitution (always) → agent rule index (always) → full rule definitions (on-demand).

### 2.5 Constitutional Hierarchy for Conflict Resolution

Anthropic's Constitution (January 2026) establishes a 4-tier priority hierarchy: safety > ethics > compliance > helpfulness. "The order is intended to convey what we think Claude should prioritize if conflicts do arise." This is critical for a rule-adherence-first harness: rules will conflict (e.g., "always complete the task" vs. "never modify files in production"), and without an explicit precedence hierarchy, the model resolves conflicts unpredictably. Our design adopts a 4-tier hierarchy and encodes the tier in every Policy Card.

### 2.6 Token Budget Research

The "Minimum Viable Context" research (Medium, Data Science Collective) frames the problem clearly: "The context window has a hard token budget, and loading additional material consumes capacity that may unnecessarily [displace task-relevant content]." The "Budget-Aware Context Management" arxiv paper (April 2026) formalizes this as a framework for "performing long-horizon reasoning under explicit token budgets." The practical implication: a harness that loads 14,000 tokens of rules at session start has already consumed 10-12% of a 128K context window before the user's task enters context. Our design targets approximately 800 tokens for governance at session start — a 94% reduction.

---

## 3. The Six-Layer Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 6: TESTING & CONTINUOUS IMPROVEMENT                  │
│  Unit · integration · mutation · property · chaos · canary  │
│  Regression suite · coverage gates · drift detection         │
│  Improvement cycle: measure → hypothesize → test → ship      │
├─────────────────────────────────────────────────────────────┤
│  Layer 5: AUDIT & FEEDBACK LOOP                             │
│  Violation logs → weekly review → rule updates → redeploy    │
├─────────────────────────────────────────────────────────────┤
│  Layer 4: VALIDATION PIPELINE (CI + pre-commit)             │
│  Schema validation · SSOT dedup linter · dead-ref linter     │
│  Rule test runner · coverage checker                         │
├─────────────────────────────────────────────────────────────┤
│  Layer 3: ENFORCEMENT HOOKS (Policy Decision Points)         │
│  PreToolUse (blocking) · PostToolUse (advisory)              │
│  SessionStart (context load) · PostCompaction (reload)       │
├─────────────────────────────────────────────────────────────┤
│  Layer 2: POLICY CARDS (machine-readable rules)              │
│  YAML rule definitions · JSON Schema validated               │
│  Per-agent · per-domain · shared (SSOT)                      │
├─────────────────────────────────────────────────────────────┤
│  Layer 1: CONSTITUTIONAL PRINCIPLES (always in context)      │
│  4-tier hierarchy: safety > ethics > compliance > useful      │
└─────────────────────────────────────────────────────────────┘
```

Each layer has a distinct responsibility and a distinct enforcement mechanism. The layers are designed to be independently testable — you can validate Layer 2 (Policy Cards) without running Layer 3 (Hooks), and you can audit Layer 5 (violations) without re-running Layer 4 (CI). Layer 6 (Testing & Continuous Improvement) wraps all five inner layers: it verifies that each layer works in isolation, that they work together in integration, and that the harness keeps working as rules and code change over time. This separation is what makes the harness maintainable: when a rule changes, you update one Policy Card (Layer 2), the schema validator confirms it's well-formed (Layer 4), the test suite confirms the rule behaves correctly (Layer 6), the hook picks it up on the next tool call (Layer 3), and the audit log shows whether violations dropped (Layer 5).

| Layer | What it does | Enforcement mechanism | Token cost at session start |
|-------|-------------|----------------------|---------------------------|
| 1. Constitution | Defines 4-tier precedence | Prompt (always loaded) | ~500 tokens |
| 2. Policy Cards | Defines binding + advisory rules | Data (loaded on-demand) | ~300 tokens (index only) |
| 3. Hooks | Enforces binding rules deterministically | PreToolUse/PostToolUse scripts | 0 tokens (runtime only) |
| 4. Validation | Catches rule defects before deploy | CI pipeline + pre-commit | 0 tokens (CI only) |
| 5. Audit | Closed-loop feedback | Violation log + weekly report | 0 tokens (async) |
| 6. Testing & Improvement | Verifies every layer works + drives evolution | Test suites + mutation + property + canary | 0 tokens (test-time only) |
| **Total** | | | **approximately 800 tokens** |

---

## 4. Layer 1: Constitutional Principles

The constitution is the only governance content that is **always** in the model's context. It must be short (under 500 tokens), high-precedence, and conflict-resolving. It does not contain operational rules — those live in Policy Cards. It contains only the principles that determine *which rule wins* when rules conflict.

### 4.1 The 4-Tier Precedence Hierarchy

Adopted from Anthropic's Constitution (January 2026), the hierarchy is:

| Tier | Name | What it protects | Example principle |
|------|------|-----------------|-------------------|
| T0 | **Safety** | Irreversible harm to systems, data, or humans | "Never execute a command that could destroy user data without explicit confirmation" |
| T1 | **Ethics** | Honesty, integrity, fairness | "Never fabricate test results or fake validation output" |
| T2 | **Compliance** | Governance rules, SSOT, file placement, process | "Every governance file must have valid YAML frontmatter" |
| T3 | **Helpfulness** | Task completion, efficiency, quality | "Prefer non-blocking validation over blocking hooks for token efficiency" |

When two rules conflict, the higher-tier rule wins. A T0 safety rule always overrides a T3 helpfulness rule. This is encoded explicitly so the model (and the hooks) can resolve conflicts deterministically.

**Note:** Anthropic's actual Constitution describes the 4-tier hierarchy as intended for holistic weighing rather than strict lexicographic override. This design adopts a stricter override model for code-governance contexts where deterministic enforcement is preferable to nuanced judgment. For general-purpose assistant behavior, the holistic approach from Anthropic's source may be more appropriate.

### 4.2 Constitution File Format

The constitution lives in `governance/constitution.yaml` and is the only governance file loaded into every session's system prompt:

```yaml
# governance/constitution.yaml
version: "1.0.0"
updated: 2026-08-01
purpose: "4-tier precedence hierarchy for rule conflict resolution"

hierarchy:
  - tier: 0
    name: safety
    description: "Prevent irreversible harm to systems, data, or humans"
    overrides: [ethics, compliance, helpfulness]
    
  - tier: 1
    name: ethics
    description: "Maintain honesty, integrity, and fairness"
    overrides: [compliance, helpfulness]
    
  - tier: 2
    name: compliance
    description: "Follow governance rules, SSOT, and process definitions"
    overrides: [helpfulness]
    
  - tier: 3
    name: helpfulness
    description: "Complete tasks efficiently and with quality"
    overrides: []

principles:
  - id: SAFE-001
    tier: safety
    text: "Never execute destructive commands (rm -rf, DROP TABLE, git push --force) without explicit user confirmation"
    enforceable_via: hook  # PreToolUse blocks these
    
  - id: SAFE-002
    tier: safety
    text: "Never commit secrets, .env files, or credentials to version control"
    enforceable_via: hook  # PreToolUse + pre-commit
    
  - id: ETHIC-001
    tier: ethics
    text: "Never fabricate test results, fake validation output, or claim work was done that wasn't"
    enforceable_via: hook  # PostToolUse checks for fake test patterns
    
  - id: COMP-001
    tier: compliance
    text: "Every governance file must have valid YAML frontmatter per its schema"
    enforceable_via: validator  # CI + pre-commit
    
  - id: COMP-002
    tier: compliance
    text: "No duplicated content across files — SSOT enforced by dedup linter"
    enforceable_via: validator  # CI
    
  - id: HELP-001
    tier: helpfulness
    text: "Prefer non-blocking advisory hooks over blocking hooks for token efficiency"
    enforceable_via: prompt  # Advisory only
```

The constitution is approximately 450 tokens — small enough to always be in context, large enough to establish the precedence hierarchy and the highest-tier binding rules. **Note:** This token count is an estimate based on typical YAML structure. Actual token count depends on the specific tokenizer used by the model and should be measured during implementation. Every Policy Card in Layer 2 references one of these principles via its `constitutional_basis` field.

### 4.3 Why the Constitution Is Separate from Policy Cards

The SovereignAI analysis (Chapter 3 of the prior report) showed that mixing constitutional principles with operational rules in a single file (like `architect.md`) creates two problems: (1) the file becomes too long to always keep in context, so it gets lazy-loaded and the constitution is sometimes absent; (2) operational rules and constitutional principles have different change frequencies — principles change rarely, rules change often. Separating them means the constitution can be cached aggressively (it changes maybe once a quarter) while Policy Cards can be updated freely.

---

## 5. Layer 2: Policy Cards (Machine-Readable Rules)

Policy Cards are the core innovation. Each rule is a YAML file with a strict schema, not a bullet in a markdown list. This makes rules machine-parseable, testable, and enforceable by hooks.

### 5.1 Policy Card Schema

Every Policy Card conforms to `governance/schemas/policy-card.schema.json`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Policy Card",
  "type": "object",
  "required": [
    "id", "version", "tier", "severity", "agent", "domain",
    "rule", "enforceable_via", "check", "test_cases"
  ],
  "properties": {
    "id": {
      "type": "string",
      "pattern": "^[A-Z]+-[0-9]{3}$",
      "description": "Unique rule identifier, e.g. ARCH-014"
    },
    "version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+\\.\\d+$",
      "description": "Semver version of this rule"
    },
    "tier": {
      "type": "string",
      "enum": ["safety", "ethics", "compliance", "helpfulness"],
      "description": "Constitutional tier — determines conflict precedence"
    },
    "severity": {
      "type": "string",
      "enum": ["blocking", "advisory"],
      "description": "blocking = hook denies the action; advisory = hook injects warning"
    },
    "agent": {
      "type": "string",
      "enum": ["architect", "planner", "executor", "researcher", "reviewer", "all"],
      "description": "Which agent this rule applies to"
    },
    "domain": {
      "type": "string",
      "description": "Rule domain, e.g. frontmatter, file-placement, hook-config"
    },
    "constitutional_basis": {
      "type": "string",
      "description": "ID of the constitutional principle this rule implements"
    },
    "rule": {
      "type": "object",
      "required": ["statement", "rationale"],
      "properties": {
        "statement": {"type": "string", "maxLength": 200},
        "rationale": {"type": "string", "maxLength": 300}
      }
    },
    "enforceable_via": {
      "type": "string",
      "enum": ["hook", "validator", "both", "prompt"],
      "description": "How this rule is enforced"
    },
    "check": {
      "type": "object",
      "description": "Machine-checkable definition of the rule",
      "properties": {
        "type": {
          "type": "string",
          "enum": ["regex", "path_pattern", "yaml_field", "json_schema",
                   "custom_function", "deny_command", "require_field"]
        },
        "params": {"type": "object"}
      }
    },
    "test_cases": {
      "type": "array",
      "minItems": 2,
      "items": {
        "type": "object",
        "required": ["input", "expected"],
        "properties": {
          "name": {"type": "string"},
          "input": {"type": "string", "description": "File path or tool input to test"},
          "expected": {"type": "string", "enum": ["pass", "fail", "deny", "allow"]}
        }
      }
    },
    "exemptions": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Paths or conditions exempt from this rule"
    }
  }
}
```

### 5.2 Example Policy Card: YAML Frontmatter Rule

This is the machine-readable version of the rule that SovereignAI's `architect.md` tried (and failed) to enforce as prose:

```yaml
# governance/policy-cards/shared/frontmatter.yaml
id: SHARED-001
version: "1.0.0"
tier: compliance
severity: blocking
agent: all
domain: frontmatter
constitutional_basis: COMP-001

rule:
  statement: "Every governance .md file must have YAML frontmatter with required fields"
  rationale: "Frontmatter is the machine-readable metadata that validators and hooks depend on"

enforceable_via: both

check:
  type: yaml_field
  params:
    file_glob: "**/*.md"
    scope_dirs: [".claude/agents", "governance", "workflows"]
    required_fields: [id, version, owner, updated, purpose, agent, persona]

test_cases:
  - name: "valid frontmatter"
    input: "tests/fixtures/valid_frontmatter.md"
    expected: pass
  - name: "missing persona field"
    input: "tests/fixtures/missing_persona.md"
    expected: fail
  - name: "no frontmatter at all"
    input: "tests/fixtures/no_frontmatter.md"
    expected: fail
  - name: "exempt non-governance file"
    input: "README.md"
    expected: pass

exemptions:
  - "README.md"
  - "CHANGELOG.md"
  - "Docs/**/*.md"  # documentation, not governance
```

The critical difference from prose: this rule is **testable**. The `test_cases` array defines four test cases that the CI pipeline (Layer 4) runs against every rule. If a rule change breaks a test case, CI fails. If a new file violates the rule, the hook (Layer 3) blocks the write. If the hook is bypassed (e.g., file created outside the agent), the audit pipeline (Layer 5) catches it in the weekly review.

### 5.3 Example Policy Card: Destructive Command Blocking (Safety)

```yaml
# governance/policy-cards/shared/safety-commands.yaml
id: SHARED-S01
version: "1.0.0"
tier: safety
severity: blocking
agent: all
domain: destructive-commands
constitutional_basis: SAFE-001

rule:
  statement: "Block destructive shell commands unless user has explicitly confirmed"
  rationale: "rm -rf, DROP TABLE, git push --force can destroy irreversible work"

enforceable_via: hook

check:
  type: deny_command
  params:
    patterns:
      - regex: "^rm\\s+-rf?\\s+"
        action: deny
        reason: "rm -rf requires explicit user confirmation"
      - regex: "DROP\\s+TABLE"
        action: deny
        reason: "Database destructive operation"
      - regex: "git\\s+push\\s+.*--force"
        action: deny
        reason: "Force push can overwrite remote history"
      - regex: "^:\\(\\)\\s*\\{.*\\|.*&\\s*\\};:"  # fork bomb
        action: deny
        reason: "Fork bomb pattern detected"

test_cases:
  - name: "blocks rm -rf"
    input: "rm -rf /tmp/test"
    expected: deny
  - name: "blocks rm -rf with path"
    input: "rm -rf tests/"
    expected: deny
  - name: "allows rm without -rf"
    input: "rm single_file.txt"
    expected: allow
  - name: "blocks git push --force"
    input: "git push origin main --force"
    expected: deny
```

### 5.4 Rule Index (Always in Context)

The full Policy Cards are loaded on-demand, but the agent always sees a compact **rule index** — a table of rule IDs, one-line summaries, and severity. This is the second tier of progressive disclosure:

```yaml
# governance/rule-index.yaml (auto-generated from Policy Cards)
# This file is loaded into context at session start (~300 tokens estimated)
agent: architect
rules:
  - id: ARCH-001
    summary: "Use relative paths, never absolute system paths"
    severity: blocking
  - id: ARCH-002
    summary: "Every workflow must include Load Governance Rules + Select Execution Mode sections"
    severity: blocking
  - id: ARCH-003
    summary: "Prefer non-blocking hooks over blocking hooks"
    severity: advisory
  # ... ~30 more rules
total: 33
```

The agent sees the rule IDs and one-line summaries at all times. When it needs the full check definition (e.g., to understand exactly what regex a hook will apply), it invokes the `rule-lookup` skill, which loads the specific Policy Card. This keeps session-start tokens low while preserving the agent's ability to reason about rules.

### 5.5 SSOT Enforcement at the Schema Level

The SovereignAI analysis showed that SSOT violations (duplicated content across files) are the single most common rule-adherence failure. This design prevents them structurally: shared rules live in `governance/policy-cards/shared/` and are **referenced by ID**, never copied. An agent-specific Policy Card that wants to add agent-specific context to a shared rule uses a `refines` field:

```yaml
# governance/policy-cards/architect/execution-modes.yaml
id: ARCH-014
version: "1.0.0"
tier: compliance
severity: advisory
agent: architect
domain: execution-modes
constitutional_basis: COMP-002

# This card REFINES the shared rule, it does not duplicate it
refines: SHARED-010  # references governance/policy-cards/shared/execution-modes.yaml

rule:
  statement: "Architect uses Manual execution mode by default; Auto mode requires user confirmation"
  rationale: "Architect changes are infrastructure-level and high-impact"

enforceable_via: prompt
check:
  type: custom_function
  params:
    function: "checks.architect_execution_mode"
```

The SSOT dedup linter (Layer 4) validates that no rule text appears in more than one Policy Card. If a rule statement is duplicated, CI fails with a "SSOT violation: rule statement appears in SHARED-010 and ARCH-014" error.

---

## 6. Layer 3: Enforcement Hooks (Policy Decision Points)

The hook layer is where rules become deterministic. Every tool call passes through a Policy Decision Point that evaluates it against the active Policy Cards. This is the architectural pattern from the "Policy-as-Code for Agents" article (tianpan.co), adapted for Devin CLI's hook system.

### 6.1 Hook Event Architecture

Devin CLI (like Claude Code) supports lifecycle hooks. The design uses four events:

| Event | When it fires | Design role | Blocking? |
|-------|--------------|-------------|-----------|
| `SessionStart` | Session begins | Load constitution + rule index into context | No (context injection) |
| `PreToolUse` | Before any tool call | Policy Decision Point — evaluate against binding rules | **Yes** (can deny) |
| `PostToolUse` | After tool completes | Advisory validation — inject warnings for soft violations | No (advisory) |
| `PostCompaction` | After context compaction | Reload constitution + rule index (compaction may have evicted them) | No (context reload) |

### 6.2 The Evaluator Module

Before implementing the PDP hook, we extract the rule evaluation logic into a separate module. This ensures the hook, test runner, and drift detection all import from the same source of truth.

```python
# scripts/enforcement/evaluator.py
#!/usr/bin/env python3
"""
Rule evaluator module — provides the core evaluation logic used by
the PDP hook, test runner, and drift detection.
"""
import re
import yaml
import jsonschema

# Registry of check type evaluators
EVALUATORS = {
    "deny_command": None,  # Implemented inline below
    "path_pattern": None,
    "require_field": None,
    "regex": None,
    "yaml_field": None,
    "json_schema": None,
    "custom_function": None,
}

def evaluate_rule(rule: dict, tool_call: dict) -> dict:
    """Evaluate a single Policy Card against a tool call.
    Returns: {decision: allow|deny, reason: str, rule_id: str}
    
    This function is imported by:
    - scripts/enforcement/pre_tool_pdp.py (runtime enforcement)
    - scripts/validation/run_rule_tests.py (test runner)
    - scripts/audit/drift_detection.py (drift detection)
    """
    check = rule.get("check", {})
    check_type = check.get("type")
    params = check.get("params", {})
    
    # Extract the relevant input from the tool call
    # Devin CLI's PreToolUse payload uses "tool_name" and "tool_input" keys
    tool_name = tool_call.get("tool_name", tool_call.get("tool", ""))
    tool_input = tool_call.get("tool_input", tool_call.get("input", {}))
    
    if check_type == "deny_command":
        # Check if the command matches any deny pattern
        command = tool_input.get("command", "")
        for pattern in params.get("patterns", []):
            if re.search(pattern["regex"], command):
                return {
                    "decision": "deny",
                    "reason": pattern.get("reason", f"Blocked by rule {rule['id']}"),
                    "rule_id": rule["id"]
                }
        return {"decision": "allow", "rule_id": rule["id"]}
    
    elif check_type == "path_pattern":
        # Check if file path matches forbidden pattern
        file_path = tool_input.get("file_path", "")
        for pattern in params.get("forbidden", []):
            if re.search(pattern, file_path):
                return {
                    "decision": "deny",
                    "reason": f"Path '{file_path}' violates rule {rule['id']}: {rule['rule']['statement']}",
                    "rule_id": rule["id"]
                }
        return {"decision": "allow", "rule_id": rule["id"]}
    
    elif check_type == "require_field":
        # Check if a required YAML field is present (for write operations)
        if tool_name in ("write", "edit"):
            content = tool_input.get("content", "")
            required_fields = params.get("fields", [])
            for field in required_fields:
                if f"{field}:" not in content[:500]:  # check frontmatter only
                    return {
                        "decision": "deny",
                        "reason": f"Missing required frontmatter field '{field}' (rule {rule['id']})",
                        "rule_id": rule["id"]
                    }
        return {"decision": "allow", "rule_id": rule["id"]}
    
    elif check_type == "regex":
        # Generic regex match against tool input
        input_string = tool_input.get("command", "") or tool_input.get("content", "") or str(tool_input)
        pattern = params.get("pattern", "")
        if re.search(pattern, input_string):
            return {
                "decision": "deny",
                "reason": f"Input matches prohibited pattern (rule {rule['id']})",
                "rule_id": rule["id"]
            }
        return {"decision": "allow", "rule_id": rule["id"]}
    
    elif check_type == "yaml_field":
        # Check YAML frontmatter for required fields or field values
        if tool_name in ("write", "edit"):
            content = tool_input.get("content", "")
            # Extract YAML frontmatter (between --- markers)
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 2:
                    try:
                        frontmatter = yaml.safe_load(parts[1])
                        if frontmatter is None:
                            frontmatter = {}
                        
                        # Check for required fields
                        required_fields = params.get("required_fields", [])
                        for field in required_fields:
                            if field not in frontmatter:
                                return {
                                    "decision": "deny",
                                    "reason": f"Missing required YAML field '{field}' (rule {rule['id']})",
                                    "rule_id": rule["id"]
                                }
                        
                        # Check field values if specified
                        field_values = params.get("field_values", {})
                        for field, expected_value in field_values.items():
                            if frontmatter.get(field) != expected_value:
                                return {
                                    "decision": "deny",
                                    "reason": f"YAML field '{field}' has incorrect value (rule {rule['id']})",
                                    "rule_id": rule["id"]
                                }
                    except Exception:
                        # If YAML parsing fails, deny for safety
                        return {
                            "decision": "deny",
                            "reason": f"Invalid YAML frontmatter (rule {rule['id']})",
                            "rule_id": rule["id"]
                        }
        return {"decision": "allow", "rule_id": rule["id"]}
    
    elif check_type == "json_schema":
        # Validate tool input against a JSON Schema
        schema = params.get("schema", {})
        try:
            jsonschema.validate(tool_input, schema)
            return {"decision": "allow", "rule_id": rule["id"]}
        except jsonschema.ValidationError as e:
            return {
                "decision": "deny",
                "reason": f"JSON Schema validation failed: {e.message} (rule {rule['id']})",
                "rule_id": rule["id"]
            }
    
    elif check_type == "custom_function":
        # Call a custom Python function for complex checks
        function_name = params.get("function", "")
        try:
            # Import the function module
            module_path, func_name = function_name.rsplit(".", 1) if "." in function_name else ("checks", function_name)
            module = __import__(module_path, fromlist=[func_name])
            custom_func = getattr(module, func_name)
            
            # Call the function with tool_call and params
            result = custom_func(tool_call, params)
            if result.get("deny"):
                return {
                    "decision": "deny",
                    "reason": result.get("reason", f"Custom function check failed (rule {rule['id']})"),
                    "rule_id": rule["id"]
                }
            return {"decision": "allow", "rule_id": rule["id"]}
        except Exception as e:
            # If custom function fails, log but allow (fail-open for custom functions)
            return {"decision": "allow", "rule_id": rule["id"], "note": f"custom function error: {e}"}
    
    # Unknown check type — deny for safety
    return {"decision": "deny", "rule_id": rule["id"], "reason": f"Unknown check type '{check_type}'"}
```

### 6.3 The Policy Decision Point Hook

The PreToolUse hook is the heart of the enforcement layer. It is a Python script that:

1. Reads the tool call from stdin (Devin CLI passes JSON via stdin)
2. Loads the active agent's binding Policy Cards (from disk on each call)
3. Evaluates each card's `check` against the tool call (using the evaluator module)
4. Returns `allow`, `deny` (with reason), or `allow-with-warning`
5. Logs the decision to the audit trail (Layer 5)

```python
# scripts/enforcement/pre_tool_pdp.py
#!/usr/bin/env python3
"""
Policy Decision Point for Devin CLI PreToolUse hook.
Evaluates every tool call against binding Policy Cards.
"""
import sys
import json
import yaml
import os
from pathlib import Path
from datetime import datetime

# Import the evaluator module for the core evaluation logic
from enforcement.evaluator import evaluate_rule

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
POLICY_CARDS_DIR = PROJECT_ROOT / "governance" / "policy-cards"
AUDIT_LOG = PROJECT_ROOT / ".audit" / "violations.jsonl"

def load_active_agent(tool_call: dict = None):
    """Determine the active agent from session state or tool call context.
    
    In a single-agent deployment, this returns a fixed agent (configurable via ACTIVE_AGENT env var).
    In a multi-agent deployment, this would resolve agent identity from:
    - The session_id in the tool call payload (Devin CLI provides this)
    - A session state store (e.g., Redis, file-based state)
    - Or agent-specific environment variables per subprocess
    
    Current implementation: Single-agent mode with environment variable fallback.
    """
    # If tool_call contains session_id, in a real implementation we would:
    # 1. Look up session state in a state store
    # 2. Return the agent associated with that session
    # For now, we use environment variable configuration
    return os.environ.get("ACTIVE_AGENT", "architect")

def load_binding_rules(agent: str):
    """Load all binding-severity Policy Cards for the active agent.
    
    Note: This function re-reads and re-parses YAML files on every call.
    In a production deployment with many rules, consider adding:
    - An in-memory cache with mtime-based invalidation
    - Or a long-lived daemon process that reloads on SIGHUP
    
    Current implementation: No caching (simple, correct, slower with many rules).
    """
    rules = []
    # Load shared rules (apply to all agents)
    shared_dir = POLICY_CARDS_DIR / "shared"
    for card_file in sorted(shared_dir.glob("*.yaml")):  # Sort for deterministic order
        card = yaml.safe_load(card_file.read_text())
        if card.get("severity") == "blocking" and card.get("agent") in ("all", agent):
            rules.append(card)
    # Load agent-specific rules
    agent_dir = POLICY_CARDS_DIR / agent
    if agent_dir.exists():
        for card_file in sorted(agent_dir.glob("*.yaml")):  # Sort for deterministic order
            card = yaml.safe_load(card_file.read_text())
            if card.get("severity") == "blocking":
                rules.append(card)
    return rules

def log_decision(tool_call: dict, result: dict):
    """Log every PDP decision to the audit trail."""
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "tool": tool_call.get("tool"),
        "input_summary": str(tool_call.get("input", ""))[:200],
        "decision": result["decision"],
        "rule_id": result.get("rule_id"),
        "reason": result.get("reason", "")
    }
    with open(AUDIT_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")

def main():
    """Main PDP entry point — reads tool call from stdin, returns decision."""
    try:
        stdin_data = sys.stdin.read()
        tool_call = json.loads(stdin_data)
    except (json.JSONDecodeError, ValueError) as e:
        # Check if any safety-tier rules are active
        agent = load_active_agent()
        rules = load_binding_rules(agent)
        has_safety_rules = any(rule.get("tier") == "safety" for rule in rules)
        
        if has_safety_rules:
            # Fail-closed for safety rules: deny on malformed input
            error_output = {
                "hookSpecificOutput": {
                    "additionalContext": f"⛔ BLOCKED: PDP failed to parse stdin (safety-tier rules active). "
                                         f"Error: {e}. The tool call was denied to prevent potential safety violations."
                }
            }
            print(json.dumps(error_output))
            sys.exit(2)  # exit code 2 = deny
        else:
            # Fail-open for non-safety rules: allow but log
            print(json.dumps({"decision": "allow", "error": f"stdin parse failed: {e}"}))
            sys.exit(0)
    
    agent = load_active_agent()
    rules = load_binding_rules(agent)
    
    # Evaluate every binding rule — any deny means deny
    # Wrap in try/except to catch evaluation errors
    try:
        for rule in rules:
            result = evaluate_rule(rule, tool_call)
            log_decision(tool_call, result)
            if result["decision"] == "deny":
                # Output the deny decision as additionalContext
                output = {
                    "hookSpecificOutput": {
                        "additionalContext": f"⛔ BLOCKED by rule {result['rule_id']}: {result['reason']}\n"
                                             f"The tool call was denied by the Policy Decision Point. "
                                             f"Modify your approach and try again."
                    }
                }
                print(json.dumps(output))
                sys.exit(2)  # exit code 2 = deny the tool call
    except Exception as e:
        # Evaluation error: check if safety rules are active
        has_safety_rules = any(rule.get("tier") == "safety" for rule in rules)
        if has_safety_rules:
            # Fail-closed for safety rules
            error_output = {
                "hookSpecificOutput": {
                    "additionalContext": f"⛔ BLOCKED: PDP evaluation error (safety-tier rules active). "
                                         f"Error: {e}. The tool call was denied to prevent potential safety violations."
                }
            }
            print(json.dumps(error_output))
            sys.exit(2)
        else:
            # Fail-open for non-safety rules
            print(json.dumps({"decision": "allow", "error": f"evaluation error: {e}"}))
            sys.exit(0)
    
    # All rules passed — allow
    print(json.dumps({"decision": "allow"}))
    sys.exit(0)

if __name__ == "__main__":
    main()
```

### 6.3 Hook Configuration

The hooks are registered in `.claude/settings.json` (Devin CLI's configuration file):

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python scripts/enforcement/session_init.py",
            "timeout": 10
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "python scripts/enforcement/pre_tool_pdp.py",
            "timeout": 5
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "^(write|edit)$",
        "hooks": [
          {
            "type": "command",
            "command": "python scripts/enforcement/post_tool_validator.py",
            "timeout": 10
          }
        ]
      }
    ],
    "PostCompaction": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python scripts/enforcement/post_compact_reload.py",
            "timeout": 15
          }
        ]
      }
    ]
  }
}
```

### 6.4 Scalability & Deployment Considerations

The design as described supports single-agent deployments. For multi-agent or parallel execution scenarios, additional considerations apply:

**1. Concurrent/Parallel Agent Execution**
The current `load_active_agent()` function uses an environment variable (`ACTIVE_AGENT`) which is process-scoped. In a deployment where multiple agents execute tool calls concurrently (e.g., Manager→Worker fan-out), this approach would not correctly scope agent identity per-session. Multi-agent deployments would require:
- Session state management (Redis, file-based state, or similar)
- Using the `session_id` from Devin CLI's PreToolUse payload to look up agent identity
- Or separate hook configurations per agent with distinct state stores

**2. Concurrent Writes to the Audit Log**
The current `log_decision()` function opens `.audit/violations.jsonl` in append mode without file locking. Under concurrent PDP subprocesses (from parallel tool calls or parallel agents), this could lead to interleaved or corrupted log entries. For concurrent deployments, consider:
- File locking (e.g., `fcntl.flock` on Unix, `msvcrt.locking` on Windows)
- Or a dedicated logging daemon that accepts writes over a socket/queue
- Or per-session log files that are merged asynchronously

**3. Offline / Local-First Operation**
The design emphasizes "local-first" operation, but Layer 4 (CI pipeline) and Layer 6 (nightly canary/mutation/drift) are specified as GitHub Actions workflows. For air-gapped or unreliable-connectivity environments, provide local equivalents:
- Local cron jobs or systemd timers for nightly tests
- Local mutation/canary runners using the same scripts
- Pre-commit hooks for validation (already provided) work offline

**4. Environment and Dependency Management**
The hook configuration specifies bare `"command": "python scripts/enforcement/pre_tool_pdp.py"` without:
- Python version resolution (`python3` vs `python`)
- Virtual environment activation
- Pinned dependency versions
- Handling for `ImportError` if dependencies aren't installed

For production deployments, consider:
- Using absolute paths to a known Python interpreter
- Activating a virtualenv in the hook command
- Adding a dependency check in the PDP script that fails gracefully
- Or packaging the enforcement scripts as an installable package with pinned dependencies

**5. Policy Card Version Field**
The schema declares a `version` field (semver pattern) but the current implementation does not consume it. Future enhancements could use this for:
- Migration paths when schema changes
- Compatibility checks between rule versions
- Rollback capabilities if a new rule version causes issues

### 6.5 Critical Design Decisions for Hooks

1. **Relative paths only.** The SovereignAI analysis found that absolute Windows paths (`C:/SovereignAI/...`) break portability. All hook commands use relative paths (`python scripts/enforcement/...`) because Devin CLI invokes hooks from the project root.

2. **PDP timeout is 5 seconds.** Long enough to load Policy Cards and evaluate regexes; short enough to not block the agent. If the PDP times out, the tool call is allowed (fail-open) but logged for non-safety rules, or denied (fail-closed) for safety-tier rules — this is a deliberate trade-off. **Note:** The 5-second timeout is appropriate for the ~33-rule single-agent example. As rule count grows, latency may increase; performance should be measured at scale and the timeout adjusted or caching added if needed.

3. **PreToolUse is blocking for safety-tier rules only.** Compliance and helpfulness rules are enforced by PostToolUse advisory hooks (non-blocking). This follows the "use hooks sparingly" principle from the guardrails research — only safety and ethics rules need to physically block; compliance rules can warn.

4. **PostToolUse injects `additionalContext` for advisory violations.** The agent sees the warning in its context on the next turn, enabling self-correction without blocking.

5. **Every decision is logged.** The audit trail in `.audit/violations.jsonl` is the input to Layer 5.

---

## 7. Layer 4: Validation Pipeline

The validation layer catches rule defects and file violations *before* they reach runtime. It runs in two contexts: pre-commit (fast, blocking) and CI (comprehensive, blocking on merge).

### 7.1 Pre-Commit Hooks (Fast, Local)

Pre-commit runs three fast validators on every `git commit`:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: validate-policy-cards
        name: Validate Policy Cards against schema
        entry: python scripts/validation/validate_policy_cards.py
        language: system
        files: ^governance/policy-cards/.*\.yaml$
        pass_filenames: true
        
      - id: lint-dead-references
        name: Lint dead references in .md files
        entry: python scripts/validation/lint_dead_references.py
        language: system
        files: \.md$
        pass_filenames: true
        
      - id: validate-frontmatter
        name: Validate YAML frontmatter on governance files
        entry: python scripts/validation/validate_frontmatter.py
        language: system
        files: ^(\.claude/agents|governance|workflows)/.*\.md$
        pass_filenames: true
```

These three checks run in under 2 seconds total and catch the most common violations: malformed Policy Cards, dead markdown references, and missing frontmatter fields.

### 7.2 CI Pipeline (Comprehensive, on PR)

The CI pipeline runs the full validation suite on every pull request:

```yaml
# .github/workflows/governance-validation.yml
name: Governance Validation
on: [pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install pyyaml jsonschema pytest
      
      # 1. Schema validation — every Policy Card must conform to its schema
      - name: Validate Policy Card schemas
        run: python scripts/validation/validate_policy_cards.py --all
      
      # 2. SSOT dedup linter — no rule text may appear in >1 card
      - name: SSOT deduplication linter
        run: python scripts/validation/lint_ssot_duplicates.py
      
      # 3. Dead reference linter — all .md links must resolve
      - name: Dead reference linter
        run: python scripts/validation/lint_dead_references.py --all
      
      # 4. Rule test runner — every Policy Card's test_cases must pass
      - name: Run rule tests
        run: python scripts/validation/run_rule_tests.py
      
      # 5. Coverage checker — every .md file must be covered by ≥1 rule
      - name: Rule coverage checker
        run: python scripts/validation/check_rule_coverage.py
      
      # 6. Constitution consistency — every Policy Card's constitutional_basis
      #    must reference a valid principle in constitution.yaml
      - name: Constitution consistency check
        run: python scripts/validation/check_constitution_consistency.py
```

### 7.3 The SSOT Dedup Linter

This is the validator that prevents the "Execution_Mode_Patterns.md duplicated 4 times" failure mode found in the SovereignAI analysis. It hashes the `rule.statement` field of every Policy Card and flags any duplicates:

```python
# scripts/validation/lint_ssot_duplicates.py
#!/usr/bin/env python3
"""SSOT dedup linter — flags duplicate rule statements across Policy Cards."""
import hashlib
import sys
import yaml
from pathlib import Path

POLICY_CARDS_DIR = Path("governance/policy-cards")

def main():
    statements = {}  # hash -> [(file, rule_id)]
    
    for card_file in POLICY_CARDS_DIR.rglob("*.yaml"):
        card = yaml.safe_load(card_file.read_text())
        statement = card.get("rule", {}).get("statement", "")
        if not statement:
            continue
        # Normalize: lowercase, strip whitespace
        normalized = " ".join(statement.lower().split())
        h = hashlib.md5(normalized.encode()).hexdigest()
        statements.setdefault(h, []).append((card_file, card.get("id", "?")))
    
    duplicates = {h: locs for h, locs in statements.items() if len(locs) > 1}
    
    if duplicates:
        print("❌ SSOT violations found — rule statements duplicated across cards:")
        for h, locs in duplicates.items():
            print(f"\n  Duplicate statement (hash {h[:8]}):")
            for filepath, rule_id in locs:
                print(f"    - {rule_id} in {filepath}")
        print("\nUse 'refines:' to reference a shared rule instead of duplicating it.")
        sys.exit(1)
    
    print("✓ No SSOT violations — all rule statements are unique")
    sys.exit(0)

if __name__ == "__main__":
    main()
```

### 7.4 The Rule Test Runner

Every Policy Card includes `test_cases`. The test runner executes them against the card's `check` function. This is what makes rules *testable* — you can't ship a rule change that breaks a test case:

```python
# scripts/validation/run_rule_tests.py
#!/usr/bin/env python3
"""Run every Policy Card's test_cases against its check function."""
import sys
import yaml
import json
from pathlib import Path

POLICY_CARDS_DIR = Path("governance/policy-cards")

def main():
    total_pass = 0
    total_fail = 0
    failures = []
    
    for card_file in POLICY_CARDS_DIR.rglob("*.yaml"):
        card = yaml.safe_load(card_file.read_text())
        card_id = card.get("id", "?")
        test_cases = card.get("test_cases", [])
        
        if len(test_cases) < 2:
            failures.append(f"{card_id}: requires ≥2 test_cases, found {len(test_cases)}")
            total_fail += 1
            continue
        
        for tc in test_cases:
            # Run the check function against the test input
            result = run_check(card, tc["input"])
            expected = tc["expected"]
            if result == expected:
                total_pass += 1
            else:
                failures.append(
                    f"{card_id} / {tc['name']}: expected {expected}, got {result}"
                )
                total_fail += 1
    
    print(f"Rule tests: {total_pass} passed, {total_fail} failed")
    if failures:
        print("\nFailures:")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    print("✓ All rule tests passed")
    sys.exit(0)

def run_check(card, test_input):
    """Run the card's check against test_input. Returns pass/fail/deny/allow."""
    # Implementation depends on check type — delegates to enforcement module
    from enforcement.evaluator import evaluate_rule
    
    check_type = card.get("check", {}).get("type")
    
    # Build appropriate tool call shape based on check type
    if check_type == "deny_command":
        tool_call = {"tool_name": "exec", "tool_input": {"command": test_input}}
    elif check_type == "path_pattern":
        tool_call = {"tool_name": "write", "tool_input": {"file_path": test_input}}
    elif check_type == "require_field":
        # For require_field, test_input should be a file path - read the file content
        test_file = Path(test_input)
        if test_file.exists():
            content = test_file.read_text()
        else:
            content = test_input  # Use as-is if file doesn't exist
        tool_call = {"tool_name": "write", "tool_input": {"content": content}}
    elif check_type == "yaml_field":
        # For yaml_field, test_input should be a file path - read the file content
        test_file = Path(test_input)
        if test_file.exists():
            content = test_file.read_text()
        else:
            content = test_input  # Use as-is if file doesn't exist
        tool_call = {"tool_name": "write", "tool_input": {"content": content}}
    elif check_type == "regex":
        tool_call = {"tool_name": "exec", "tool_input": {"command": test_input}}
    elif check_type == "json_schema":
        # For json_schema, test_input should be JSON
        try:
            json_input = json.loads(test_input) if isinstance(test_input, str) else test_input
            tool_call = {"tool_name": "test", "tool_input": json_input}
        except:
            tool_call = {"tool_name": "test", "tool_input": {}}
    elif check_type == "custom_function":
        # For custom_function, pass as-is
        tool_call = {"tool_name": "test", "tool_input": {"data": test_input}}
    else:
        # Default fallback
        tool_call = {"tool_name": "test", "tool_input": {"command": test_input}}
    
    result = evaluate_rule(card, tool_call)
    return "deny" if result["decision"] == "deny" else "allow"

if __name__ == "__main__":
    main()
```

---

## 8. Layer 5: Audit & Feedback Loop

The audit layer closes the loop. Without it, the harness has no way to detect rule drift, measure enforcement effectiveness, or identify rules that need updating. This is the "Audit" phase of the Declare-Do-Audit lifecycle from the Policy Cards paper.

### 8.1 Violation Log

Every PDP decision is logged to `.audit/violations.jsonl`:

```json
{"timestamp": "2026-08-01T14:23:01Z", "tool": "bash", "input_summary": "rm -rf tests/", "decision": "deny", "rule_id": "SHARED-S01", "reason": "rm -rf requires explicit user confirmation"}
{"timestamp": "2026-08-01T14:23:15Z", "tool": "write", "input_summary": "governance/policy-cards/architect/new-rule.yaml", "decision": "allow", "rule_id": "SHARED-001", "reason": ""}
{"timestamp": "2026-08-01T14:24:02Z", "tool": "write", "input_summary": "workflow.md (missing persona field)", "decision": "deny", "rule_id": "SHARED-001", "reason": "Missing required frontmatter field 'persona'"}
```

### 8.2 Weekly Audit Report

A weekly cron job generates an audit report that answers four questions:

1. **Which rules are firing most often?** (indicates either a rule that's hard to follow or a violation pattern)
2. **Which rules never fire?** (candidates for removal or downgrade to advisory)
3. **Which rules have test cases that fail?** (rule is broken or test is stale)
4. **Are there new violation patterns not covered by any rule?** (candidates for new rules)

```python
# scripts/audit/weekly_review_report.py
#!/usr/bin/env python3
"""Generate weekly audit report from violation log."""
import json
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

AUDIT_LOG = Path(".audit/violations.jsonl")
REPORT_DIR = Path(".audit/weekly-reviews")

def main():
    week_ago = datetime.utcnow() - timedelta(days=7)
    
    # Load all violations from the past week
    violations = []
    if AUDIT_LOG.exists():
        for line in AUDIT_LOG.read_text().splitlines():
            entry = json.loads(line)
            ts = datetime.fromisoformat(entry["timestamp"].replace("Z", "+00:00"))
            if ts.replace(tzinfo=None) >= week_ago:
                violations.append(entry)
    
    # Aggregate by rule
    by_rule = Counter(v["rule_id"] for v in violations if v["decision"] == "deny")
    by_tool = Counter(v["tool"] for v in violations)
    
    report = f"""# Weekly Audit Report — {datetime.utcnow().strftime('%Y-%m-%d')}

## Summary
- Total PDP decisions this week: {len(violations)}
- Denials: {sum(1 for v in violations if v['decision'] == 'deny')}
- Allows: {sum(1 for v in violations if v['decision'] == 'allow')}

## Top 5 Most-Violated Rules (deny decisions)
"""
    for rule_id, count in by_rule.most_common(5):
        report += f"- {rule_id}: {count} denials\n"
    
    report += f"""
## Tool Call Distribution
"""
    for tool, count in by_tool.most_common():
        report += f"- {tool}: {count} calls\n"
    
    report += """
## Recommended Actions
- Rules with 0 denials this week: review for removal or downgrade to advisory
- Rules with >10 denials: review for SSOT violation or unclear statement
- New violation patterns not covered by any rule: create new Policy Card
"""
    
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_file = REPORT_DIR / f"review-{datetime.utcnow().strftime('%Y-%m-%d')}.md"
    report_file.write_text(report)
    print(f"Weekly report generated: {report_file}")

if __name__ == "__main__":
    main()
```

### 8.3 The Closed Feedback Loop

The audit layer creates a closed loop:

```
Policy Card (Layer 2) 
    → enforced by Hook (Layer 3) 
    → violations logged to .audit/ (Layer 5)
    → weekly report identifies rule gaps
    → new/updated Policy Card proposed
    → validated by CI (Layer 4)
    → merged and deployed
    → back to Layer 2
```

This is what prevents the "rules drift from reality" failure mode. In the SovereignAI analysis, we found rules that referenced non-existent components (`Rule_Following_Hook`) and rules that duplicated content across 4 files. A closed-loop audit would have caught both: the ghost reference would show 0 enforcement events (because the component doesn't exist), and the duplication would trigger the SSOT linter in CI.

---

## 9. Layer 6: Rigorous Testing & Continuous Improvement

The first five layers define *what* the harness does. Layer 6 defines *how you know it actually does it*. Without rigorous testing, the previous five layers are a well-documented bet — the constitution might reference a principle that doesn't exist, a Policy Card's regex might have an off-by-one error, the PDP hook might crash on Unicode input, and the audit pipeline might silently drop violations. Testing is what converts "should work" into "verified to work."

This layer is organized around **six test pyramids** (one per inner layer) and **one improvement cycle** that uses test results to drive harness evolution. The design principle is: **if a behavior is not tested, it is not a feature — it is a hypothesis.**

### 9.1 The Six Test Pyramids

Each inner layer gets its own test pyramid: unit tests at the base (fast, isolated), integration tests in the middle (cross-layer), and end-to-end / property tests at the top (slow, holistic). Tests run at three cadences: pre-commit (seconds), CI (minutes), and nightly (minutes-to-hours).

```
                    ┌─────────────────────────────────┐
                    │  PROPERTY / E2E / CHAOS          │  nightly
                    │  (Hypothesis, canary, drift)     │
                    ├─────────────────────────────────┤
                    │  INTEGRATION                     │  CI (every PR)
                    │  (Cross-layer, real stdin)       │
                    ├─────────────────────────────────┤
                    │  UNIT                            │  pre-commit (<2s)
                    │  (Pure functions, fixtures)      │
                    └─────────────────────────────────┘
```

### 9.2 Test Pyramid 1 — Constitution Tests

The constitution is the foundation; if it's malformed, everything above it is suspect.

| Test type | What it verifies | Example test |
|-----------|-----------------|--------------|
| Unit | Schema conformance — every field in `constitution.yaml` matches `constitution.schema.json` | `test_constitution_has_valid_schema()` |
| Unit | Tier completeness — all 4 tiers (safety, ethics, compliance, helpfulness) are present and ordered | `test_tier_hierarchy_is_complete()` |
| Unit | Override consistency — every tier's `overrides` list references tiers that actually exist | `test_overrides_reference_valid_tiers()` |
| Unit | Principle IDs are unique and match pattern `^[A-Z]+-[0-9]{3}$` | `test_principle_ids_are_unique()` |
| Property | Every principle's `enforceable_via` field is one of {hook, validator, both, prompt} — no invalid values can exist | Hypothesis: `given(principle_id=st.text()) → enforceable_via in valid_set` |
| Integration | Every Policy Card's `constitutional_basis` field references a principle ID that exists in the constitution | `test_every_policy_card_has_valid_basis()` |

```python
# tests/unit/test_constitution.py
import pytest
import yaml
import jsonschema
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CONSTITUTION = PROJECT_ROOT / "governance" / "constitution.yaml"
SCHEMA = PROJECT_ROOT / "governance" / "schemas" / "constitution.schema.json"

@pytest.fixture
def constitution():
    return yaml.safe_load(CONSTITUTION.read_text())

@pytest.fixture
def schema():
    return json.loads(SCHEMA.read_text())

def test_constitution_matches_schema(constitution, schema):
    """The constitution must validate against its JSON Schema."""
    jsonschema.validate(constitution, schema)

def test_tier_hierarchy_is_complete(constitution):
    """All 4 constitutional tiers must be present and in precedence order."""
    tiers = [t["name"] for t in constitution["hierarchy"]]
    assert tiers == ["safety", "ethics", "compliance", "helpfulness"], \
        f"Tier hierarchy is {tiers}, expected the 4-tier precedence order"

def test_overrides_reference_valid_tiers(constitution):
    """Every tier's overrides list must reference tiers that exist."""
    valid_tiers = {t["name"] for t in constitution["hierarchy"]}
    for tier in constitution["hierarchy"]:
        for overridden in tier.get("overrides", []):
            assert overridden in valid_tiers, \
                f"Tier '{tier['name']}' overrides '{overridden}' which does not exist"

def test_principle_ids_are_unique(constitution):
    """Every principle ID must be unique and match the ID pattern."""
    import re
    ids = [p["id"] for p in constitution["principles"]]
    assert len(ids) == len(set(ids)), "Duplicate principle IDs found"
    for pid in ids:
        assert re.match(r"^[A-Z]+-[0-9]{3}$", pid), \
            f"Principle ID '{pid}' does not match pattern ^[A-Z]+-[0-9]{3}$"

def test_every_principle_has_enforceable_via(constitution):
    """Every principle must declare how it is enforced."""
    valid = {"hook", "validator", "both", "prompt"}
    for p in constitution["principles"]:
        assert p.get("enforceable_via") in valid, \
            f"Principle {p['id']} has invalid enforceable_via: {p.get('enforceable_via')}"
```

### 9.3 Test Pyramid 2 — Policy Card Tests

Policy Cards are the most frequently changed artifact in the harness, so they get the most rigorous test pyramid. Every card must ship with at least 2 test cases (enforced by schema), and the test runner executes them on every PR.

| Test type | What it verifies | Example test |
|-----------|-----------------|--------------|
| Unit | Schema conformance — every `.yaml` card validates against `policy-card.schema.json` | `test_all_cards_match_schema()` |
| Unit | Test case minimum — every card has ≥2 test cases (schema-enforced, but double-check) | `test_every_card_has_minimum_test_cases()` |
| Unit | Test case execution — every card's `test_cases` pass against its `check` function | `test_card_test_cases_pass(card_id)` (parametrized) |
| Unit | Exemption validity — every exemption pattern is a valid glob/regex | `test_exemptions_are_valid_patterns()` |
| Unit | Refines integrity — if a card has `refines:`, the referenced card ID must exist | `test_refines_references_resolve()` |
| Property | For any card, flipping the `check.params` should flip at least one test case's expected result | Hypothesis mutation test |
| Integration | Every card's `constitutional_basis` references a valid principle | `test_card_basis_is_valid()` |
| Integration | SSOT — no two cards have the same `rule.statement` hash | `test_no_duplicate_rule_statements()` |

```python
# tests/unit/test_policy_cards.py
import pytest
import yaml
import jsonschema
import hashlib
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CARDS_DIR = PROJECT_ROOT / "governance" / "policy-cards"
SCHEMA = PROJECT_ROOT / "governance" / "schemas" / "policy-card.schema.json"

def load_all_cards():
    """Fixture: load every Policy Card in the repo."""
    return [(f, yaml.safe_load(f.read_text())) for f in CARDS_DIR.rglob("*.yaml")]

def test_all_cards_match_schema():
    """Every Policy Card must validate against the JSON Schema."""
    schema = json.loads(SCHEMA.read_text())
    cards = load_all_cards()
    assert len(cards) > 0, "No Policy Cards found — harness is empty"
    for card_file, card in cards:
        try:
            jsonschema.validate(card, schema)
        except jsonschema.ValidationError as e:
            pytest.fail(f"{card_file} fails schema validation: {e.message}")

def test_every_card_has_minimum_test_cases():
    """Every card must have ≥2 test cases (schema-enforced, but verify)."""
    for card_file, card in load_all_cards():
        tc = card.get("test_cases", [])
        assert len(tc) >= 2, \
            f"{card_file} has {len(tc)} test cases, minimum is 2"

@pytest.mark.parametrize("card_file,card", load_all_cards())
def test_card_test_cases_pass(card_file, card):
    """Every card's test_cases must actually pass against its check."""
    from enforcement.evaluator import evaluate_rule
    for tc in card["test_cases"]:
        # Build appropriate tool call shape based on check type
        check_type = card.get("check", {}).get("type")
        test_input = tc["input"]
        
        if check_type == "deny_command":
            tool_call = {"tool_name": "exec", "tool_input": {"command": test_input}}
        elif check_type == "path_pattern":
            tool_call = {"tool_name": "write", "tool_input": {"file_path": test_input}}
        elif check_type in ("require_field", "yaml_field"):
            # For field checks, test_input should be a file path - read the file content
            test_file = Path(test_input)
            if test_file.exists():
                content = test_file.read_text()
            else:
                content = test_input  # Use as-is if file doesn't exist
            tool_call = {"tool_name": "write", "tool_input": {"content": content}}
        elif check_type == "regex":
            tool_call = {"tool_name": "exec", "tool_input": {"command": test_input}}
        elif check_type == "json_schema":
            try:
                json_input = json.loads(test_input) if isinstance(test_input, str) else test_input
                tool_call = {"tool_name": "test", "tool_input": json_input}
            except:
                tool_call = {"tool_name": "test", "tool_input": {}}
        elif check_type == "custom_function":
            tool_call = {"tool_name": "test", "tool_input": {"data": test_input}}
        else:
            # Default fallback
            tool_call = {"tool_name": "test", "tool_input": {"command": test_input}}
        
        result = evaluate_rule(card, tool_call)
        actual = "deny" if result["decision"] == "deny" else "allow"
        assert actual == tc["expected"], \
            f"{card_file} / {tc['name']}: expected {tc['expected']}, got {actual}"

def test_no_duplicate_rule_statements():
    """SSOT: no two cards may have the same rule.statement (normalized)."""
    statements = {}
    for card_file, card in load_all_cards():
        stmt = card.get("rule", {}).get("statement", "")
        normalized = " ".join(stmt.lower().split())
        h = hashlib.md5(normalized.encode()).hexdigest()
        if h in statements:
            pytest.fail(
                f"SSOT violation: '{card.get('id')}' in {card_file} duplicates "
                f"'{statements[h][1]}' in {statements[h][0]}"
            )
        statements[h] = (card_file, card.get("id"))

def test_refines_references_resolve():
    """If a card has 'refines:', the referenced card ID must exist."""
    all_ids = {card["id"] for _, card in load_all_cards() if "id" in card}
    for card_file, card in load_all_cards():
        if "refines" in card:
            assert card["refines"] in all_ids, \
                f"{card_file} refines '{card['refines']}' which does not exist"
```

### 9.4 Test Pyramid 3 — Hook / PDP Tests

The PDP is the enforcement engine. If it crashes, fails open, or fails closed at the wrong time, the entire harness is compromised. This is the most critical test pyramid.

| Test type | What it verifies | Example test |
|-----------|-----------------|--------------|
| Unit | `evaluate_rule()` returns correct decision for each check type | `test_deny_command_regex_matches()` |
| Unit | `load_binding_rules()` returns only blocking-severity cards for the active agent | `test_only_blocking_rules_loaded()` |
| Unit | `load_binding_rules()` returns shared + agent-specific cards (not other agents') | `test_no_cross_agent_leakage()` |
| Unit | PDP handles malformed stdin gracefully (no crash, fail-open with log) | `test_malformed_stdin_does_not_crash()` |
| Unit | PDP handles missing Policy Card files gracefully | `test_missing_card_file_handled()` |
| Integration | PDP denies `rm -rf` when `SHARED-S01` is active | `test_destructive_command_blocked()` |
| Integration | PDP allows `rm single_file.txt` (no -rf flag) | `test_non_destructive_rm_allowed()` |
| Integration | PDP denies write to governance file without frontmatter | `test_missing_frontmatter_blocked()` |
| Integration | PDP allows write to README.md (exempt) | `test_exempt_files_allowed()` |
| Mutation | Deliberately break a card's regex → confirm PDP behavior changes | `test_mutation_breaks_enforcement()` |
| Property | For any valid tool call, PDP returns within 5 seconds (timeout guarantee) | `test_pdp_completes_within_5_seconds_property()` (Hypothesis) |
| Chaos | Inject random stdin garbage → PDP must not crash or hang | `test_chaos_stdin_resilience()` |

```python
# tests/integration/test_pdp_integration.py
import json
import subprocess
import pytest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
PDP_SCRIPT = PROJECT_ROOT / "scripts" / "enforcement" / "pre_tool_pdp.py"

def run_pdp(tool_call: dict) -> dict:
    """Run the PDP script with a given tool call and return its output."""
    result = subprocess.run(
        ["python", str(PDP_SCRIPT)],
        input=json.dumps(tool_call),
        capture_output=True,
        text=True,
        timeout=10,
        cwd=str(PROJECT_ROOT),
    )
    return {
        "exit_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }

def test_destructive_command_blocked():
    """rm -rf must be denied by SHARED-S01."""
    result = run_pdp({"tool_name": "exec", "tool_input": {"command": "rm -rf tests/"}})
    assert result["exit_code"] == 2, f"Expected exit 2 (deny), got {result['exit_code']}"
    assert "BLOCKED" in result["stdout"] or "deny" in result["stdout"]

def test_non_destructive_rm_allowed():
    """rm without -rf must be allowed."""
    result = run_pdp({"tool_name": "exec", "tool_input": {"command": "rm single_file.txt"}})
    assert result["exit_code"] == 0, f"Expected exit 0 (allow), got {result['exit_code']}"

def test_missing_frontmatter_blocked():
    """Writing a governance .md without frontmatter must be denied."""
    result = run_pdp({
        "tool_name": "write",
        "tool_input": {
            "file_path": "governance/policy-cards/test.md",
            "content": "# No frontmatter here\nJust body text"
        }
    })
    assert result["exit_code"] == 2

def test_exempt_files_allowed():
    """README.md is exempt from frontmatter rules."""
    result = run_pdp({
        "tool_name": "write",
        "tool_input": {
            "file_path": "README.md",
            "content": "# No frontmatter here\nBut README is exempt"
        }
    })
    assert result["exit_code"] == 0

def test_malformed_stdin_does_not_crash():
    """Malformed stdin must not crash the PDP — fail open with log."""
    result = subprocess.run(
        ["python", str(PDP_SCRIPT)],
        input="this is not json {{{",
        capture_output=True,
        text=True,
        timeout=10,
        cwd=str(PROJECT_ROOT),
    )
    assert result.returncode == 0, "PDP must fail-open on malformed stdin"
    assert "allow" in result.stdout, "Malformed stdin should result in allow + error log"

def test_pdp_completes_within_timeout():
    """PDP must return within 5 seconds (the hook timeout).
    
    Note: This is a single measurement test. For comprehensive timing
    verification, use the property-based test in test_pdp_properties.py
    which tests across random inputs and rule configurations.
    """
    import time
    start = time.monotonic()
    run_pdp({"tool_name": "exec", "tool_input": {"command": "ls"}})
    elapsed = time.monotonic() - start
    assert elapsed < 5.0, f"PDP took {elapsed:.2f}s, must be <5s"
```

### 9.5 Test Pyramid 4 — Validator Tests

The validators (Layer 4) are themselves code that can have bugs. A broken SSOT linter that silently passes duplicates is worse than no linter at all.

| Test type | What it verifies |
|-----------|-----------------|
| Unit | SSOT linter flags a known duplicate (fixture with two identical statements) |
| Unit | SSOT linter passes when all statements are unique |
| Unit | Dead-reference linter flags a known dead link |
| Unit | Frontmatter validator flags a file with missing `persona` field |
| Unit | Frontmatter validator passes a file with all required fields |
| Integration | CI pipeline (`.github/workflows/governance-validation.yml`) runs all validators and fails on a bad PR |
| Regression | A fixture replicating each past bug (e.g., the SovereignAI `Rule_Following_Hook` ghost reference) is flagged |

```python
# tests/unit/test_ssot_linter.py
import subprocess
import pytest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
LINTER = PROJECT_ROOT / "scripts" / "validation" / "lint_ssot_duplicates.py"

def test_ssot_linter_flags_duplicates(tmp_path, monkeypatch):
    """The SSOT linter must flag two cards with identical rule statements."""
    # Create two cards with the same statement
    cards_dir = tmp_path / "governance" / "policy-cards" / "shared"
    cards_dir.mkdir(parents=True)
    duplicate_statement = "Every file must have valid frontmatter"
    (cards_dir / "card1.yaml").write_text(f"""
id: SHARED-001
version: "1.0.0"
tier: compliance
severity: blocking
agent: all
domain: frontmatter
rule:
  statement: "{duplicate_statement}"
  rationale: "test"
enforceable_via: validator
check:
  type: require_field
  params: {{fields: [id]}}
test_cases:
  - name: pass
    input: "valid.md"
    expected: pass
  - name: fail
    input: "invalid.md"
    expected: fail
""")
    (cards_dir / "card2.yaml").write_text(f"""
id: SHARED-002
version: "1.0.0"
tier: compliance
severity: blocking
agent: all
domain: frontmatter
rule:
  statement: "{duplicate_statement}"
  rationale: "test duplicate"
enforceable_via: validator
check:
  type: require_field
  params: {{fields: [id]}}
test_cases:
  - name: pass
    input: "valid.md"
    expected: pass
  - name: fail
    input: "invalid.md"
    expected: fail
""")
    
    monkeypatch.chdir(tmp_path)
    result = subprocess.run(
        ["python", str(LINTER)],
        capture_output=True,
        text=True,
        cwd=str(tmp_path),
    )
    assert result.returncode == 1, "Linter must exit 1 on duplicates"
    assert "SSOT violation" in result.stdout

def test_ssot_linter_passes_unique_statements():
    """The SSOT linter must pass when all statements are unique."""
    result = subprocess.run(
        ["python", str(LINTER)],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
    )
    # On the real repo, all statements should be unique
    assert result.returncode == 0, f"Linter failed on real repo: {result.stdout}"
```

### 9.6 Test Pyramid 5 — Audit Pipeline Tests

The audit pipeline must not silently drop violations or produce misleading reports.

| Test type | What it verifies |
|-----------|-----------------|
| Unit | `log_decision()` writes a valid JSONL line with all required fields |
| Unit | `weekly_review_report.py` correctly aggregates deny counts by rule ID |
| Unit | Report generator handles empty violation log gracefully |
| Integration | A simulated PDP deny produces an entry in `.audit/violations.jsonl` |
| Regression | A fixture replicating the SovereignAI `stdin_debug.txt` privacy leak is NOT produced (debug writes are gated) |

### 9.7 Test Pyramid 6 — End-to-End & Mutation Testing

This is the pyramid top: tests that verify the *whole harness* behaves correctly, and tests that verify the tests themselves are meaningful.

#### End-to-End Canary Sessions

A canary session is a scripted Devin CLI session that exercises the full harness end-to-end. It runs nightly and verifies that the harness blocks what it should block and allows what it should allow.

```python
# tests/e2e/test_canary_session.py
"""
End-to-end canary session: runs a scripted sequence of tool calls
through the actual hook system and verifies outcomes.
Runs nightly via GitHub Actions scheduled workflow.
"""
import subprocess
import pytest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Each canary case is: (name, tool_call, expected_exit_code, expected_stdout_contains)
CANARY_CASES = [
    ("destructive_rm_rf", {"tool_name": "exec", "tool_input": {"command": "rm -rf tests/"}}, 2, "BLOCKED"),
    ("safe_rm", {"tool_name": "exec", "tool_input": {"command": "rm file.txt"}}, 0, None),
    ("git_force_push", {"tool_name": "exec", "tool_input": {"command": "git push origin main --force"}}, 2, "BLOCKED"),
    ("safe_ls", {"tool_name": "exec", "tool_input": {"command": "ls -la"}}, 0, None),
    ("write_without_frontmatter", {"tool_name": "write", "tool_input": {"file_path": "governance/test.md", "content": "# no frontmatter"}}, 2, "BLOCKED"),
    ("write_with_frontmatter", {"tool_name": "write", "tool_input": {"file_path": "governance/test.md", "content": "---\nid: TEST-001\n---\n# body"}}, 0, None),
    ("write_to_readme_exempt", {"tool_name": "write", "tool_input": {"file_path": "README.md", "content": "# no frontmatter but exempt"}}, 0, None),
]

@pytest.mark.parametrize("name,tool_call,expected_exit,expected_stdout", CANARY_CASES)
def test_canary(name, tool_call, expected_exit, expected_stdout):
    """Each canary case must produce the expected outcome."""
    result = subprocess.run(
        ["python", str(PROJECT_ROOT / "scripts" / "enforcement" / "pre_tool_pdp.py")],
        input=json.dumps(tool_call),
        capture_output=True,
        text=True,
        timeout=10,
        cwd=str(PROJECT_ROOT),
    )
    assert result.returncode == expected_exit, \
        f"{name}: expected exit {expected_exit}, got {result.returncode}. stdout: {result.stdout}"
    if expected_stdout:
        assert expected_stdout in result.stdout, \
            f"{name}: expected '{expected_stdout}' in stdout, got: {result.stdout}"
```

#### Mutation Testing

Mutation testing verifies that the test suite is actually meaningful — not just passing. The tool (`mutmut` or `cosmic-ray`) deliberately introduces bugs into the PDP code (flip a `==` to `!=`, delete a line, change a regex) and re-runs the tests. If the tests still pass, the mutation "survived" — meaning the test suite has a coverage gap.

```python
# tests/mutation/test_mutation_score.py
"""
Mutation test runner — verifies the test suite catches deliberate bugs.
Mutation score must stay above 80% (no more than 20% of mutations survive).
"""
import subprocess
import pytest

def test_mutation_score_above_threshold():
    """Run mutmut and verify the mutation score is above 80%."""
    result = subprocess.run(
        ["mutmut", "run", "--paths-to-mutate=scripts/enforcement/",
         "--tests-dir=tests/", "--use-coverage"],
        capture_output=True,
        text=True,
        timeout=3600,  # 1 hour max
    )
    # Parse mutmut output for survival rate
    output = result.stdout + result.stderr
    # mutmut reports: "X mutants created, Y killed, Z survived, W timeout"
    # Mutation score = killed / (killed + survived)
    import re
    killed = int(re.search(r"(\d+) killed", output).group(1))
    survived = int(re.search(r"(\d+) survived", output).group(1))
    score = killed / (killed + survived) if (killed + survived) > 0 else 0
    assert score >= 0.80, \
        f"Mutation score {score:.1%} is below 80% threshold. " \
        f"{survived} mutations survived — tests have coverage gaps."
```

#### Property-Based Testing with Hypothesis

Property-based tests generate thousands of random inputs and verify invariants hold. For the PDP, the key invariant is: **the PDP must never crash or hang, regardless of input.**

```python
# tests/property/test_pdp_properties.py
"""
Property-based tests: verify PDP invariants hold for ANY input.
Uses Hypothesis to generate thousands of random tool calls.
"""
import json
import subprocess
from hypothesis import given, strategies as st, settings, HealthCheck
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
PDP_SCRIPT = PROJECT_ROOT / "scripts" / "enforcement" / "pre_tool_pdp.py"

# Strategy: generate arbitrary tool call dicts
tool_calls = st.fixed_dicts({
    "tool": st.text(min_size=1, max_size=20),
    "input": st.fixed_dicts({
        "command": st.text(max_size=200),
        "file_path": st.text(max_size=200),
        "content": st.text(max_size=500),
    }, optional=["command", "file_path", "content"]),
})

@settings(max_examples=500, deadline=5000, 
          suppress_health_check=[HealthCheck.too_slow])
@given(tool_call=tool_calls)
def test_pdp_never_crashes(tool_call):
    """PDP must never crash, regardless of input."""
    result = subprocess.run(
        ["python", str(PDP_SCRIPT)],
        input=json.dumps(tool_call),
        capture_output=True,
        text=True,
        timeout=10,
        cwd=str(PROJECT_ROOT),
    )
    # Must exit 0 (allow) or 2 (deny) — never exit 1 (crash)
    assert result.returncode in (0, 2), \
        f"PDP crashed on input {tool_call}: exit {result.returncode}, stderr: {result.stderr}"

@given(garbage=st.binary(min_size=0, max_size=1000))
def test_pdp_handles_binary_stdin(garbage):
    """PDP must handle arbitrary binary stdin without crashing."""
    result = subprocess.run(
        ["python", str(PDP_SCRIPT)],
        input=garbage,
        capture_output=True,
        timeout=10,
        cwd=str(PROJECT_ROOT),
    )
    assert result.returncode in (0, 2), \
        f"PDP crashed on binary stdin: exit {result.returncode}"

@settings(max_examples=100, deadline=5000,
          suppress_health_check=[HealthCheck.too_slow])
@given(tool_call=tool_calls)
def test_pdp_completes_within_5_seconds_property(tool_call):
    """Property-based test: PDP must complete within 5 seconds for any valid tool call."""
    import time
    start = time.monotonic()
    result = subprocess.run(
        ["python", str(PDP_SCRIPT)],
        input=json.dumps(tool_call),
        capture_output=True,
        timeout=10,  # Give test a 10s timeout, but assert <5s
        cwd=str(PROJECT_ROOT),
    )
    elapsed = time.monotonic() - start
    assert result.returncode in (0, 2), \
        f"PDP crashed on input {tool_call}: exit {result.returncode}"
    assert elapsed < 5.0, \
        f"PDP took {elapsed:.2f}s on input {tool_call}, must be <5s"
```

### 9.8 Coverage Gates

Test coverage is enforced as a merge gate. A PR that drops coverage below the threshold cannot merge.

```yaml
# .github/workflows/coverage-gate.yml
name: Coverage Gate
on: [pull_request]
jobs:
  coverage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install pytest pytest-cov
      
      - name: Run tests with coverage
        run: |
          pytest tests/ --cov=scripts/enforcement --cov=scripts/validation \
                 --cov=scripts/audit --cov-report=xml --cov-report=term
      
      - name: Check coverage thresholds
        run: |
          python -c "
          import xml.etree.ElementTree as ET
          tree = ET.parse('coverage.xml')
          root = tree.getroot()
          line_rate = float(root.attrib['line-rate'])
          branch_rate = float(root.attrib['branch-rate'])
          print(f'Line coverage: {line_rate:.1%}')
          print(f'Branch coverage: {branch_rate:.1%}')
          assert line_rate >= 0.90, f'Line coverage {line_rate:.1%} below 90% gate'
          assert branch_rate >= 0.80, f'Branch coverage {branch_rate:.1%} below 80% gate'
          print('✓ Coverage gates passed')
          "
```

**Coverage thresholds:**

| Module | Line coverage gate | Branch coverage gate | Rationale |
|--------|-------------------|---------------------|-----------|
| `scripts/enforcement/` (PDP) | 95% | 90% | Safety-critical — bugs here mean rules don't enforce |
| `scripts/validation/` (linters) | 90% | 85% | High-impact — bugs here mean violations slip through |
| `scripts/audit/` (reporting) | 85% | 75% | Lower-stakes — bugs here affect reporting, not enforcement |
| `governance/` (Policy Cards) | 100% | 100% | Every card must have ≥2 test cases (schema-enforced) |

### 9.9 Regression Test Suite (Bug Fixtures)

Every bug found in production or in testing gets a regression test fixture. The fixture is a minimal reproduction that must fail before the fix and pass after. This builds a growing library of "things that broke once" — ensuring they never break the same way again.

```
tests/fixtures/regression/
├── SOVEREIGNAI-001-ghost-reference.yaml      # Rule_Following_Hook ghost reference
├── SOVEREIGNAI-002-ssot-duplication.yaml     # Execution_Mode_Patterns 4-copy duplication
├── SOVEREIGNAI-003-windows-path-hardcode.yaml # C:/SovereignAI/ in hooks
├── SOVEREIGNAI-004-case-sensitivity.yaml     # "App/" vs "app/" bug
├── SOVEREIGNAI-005-yaml-frontmatter-self-violation.yaml
├── BUG-2026-0801-pdp-unicode-crash.yaml      # hypothetical future bug
└── BUG-2026-0815-ssot-linter-false-negative.yaml
```

Each fixture is a YAML file containing: the bug description, the minimal reproduction, the expected behavior, and the fix commit reference.

```yaml
# tests/fixtures/regression/SOVEREIGNAI-001-ghost-reference.yaml
bug_id: SOVEREIGNAI-001
discovered: 2026-08-01
source: "SovereignAI Harness Analysis Report, §3.2"
description: |
  architect.md lines 100 and 190 referenced a "Rule_Following_Hook" component
  that did not exist anywhere in the repository. The rule appeared to govern
  behavior but nothing enforced it.
reproduction:
  - grep -r "Rule_Following_Hook" .claude/ governance/
expected: |
  No rule, Policy Card, or constitution principle may reference a component
  that does not exist. The check_constitution_consistency.py validator must
  flag any reference to a non-existent enforceable_via target.
fix: "Commit abc123 — added check_constitution_consistency.py validator"
regression_test: tests/regression/test_sovereignai_001_ghost_reference.py
```

```python
# tests/regression/test_sovereignai_001_ghost_reference.py
"""
Regression test: no Policy Card or constitution principle may reference
a component that does not exist. Catches the Rule_Following_Hook ghost
reference class of bug.
"""
import yaml
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

def test_no_ghost_references_in_policy_cards():
    """Every enforceable_via target must map to a real enforcement mechanism."""
    valid_targets = {"hook", "validator", "both", "prompt"}
    cards_dir = PROJECT_ROOT / "governance" / "policy-cards"
    for card_file in cards_dir.rglob("*.yaml"):
        card = yaml.safe_load(card_file.read_text())
        target = card.get("enforceable_via")
        assert target in valid_targets, \
            f"{card_file} has enforceable_via='{target}' — not a valid target"

def test_no_ghost_references_in_constitution():
    """Every constitutional principle's enforceable_via must be valid."""
    valid_targets = {"hook", "validator", "both", "prompt"}
    constitution = yaml.safe_load(
        (PROJECT_ROOT / "governance" / "constitution.yaml").read_text()
    )
    for p in constitution["principles"]:
        assert p.get("enforceable_via") in valid_targets, \
            f"Principle {p['id']} has invalid enforceable_via: {p.get('enforceable_via')}"
```

### 9.10 The Continuous Improvement Cycle

Testing tells you *what* is broken. The improvement cycle tells you *what to do about it*. It's a four-step loop that runs continuously.

```
    ┌──────────────────────────────────────────────┐
    │                                              ▼
MEASURE → HYPOTHESIZE → TEST → SHIP → (back to MEASURE)
    │              │          │        │
    │              │          │        └── deploy if tests pass
    │              │          └── run canary + mutation + property tests
    │              └── form hypothesis: "if we change X, Y will improve"
    └── collect metrics from audit log, test results, violation trends
```

#### Step 1: MEASURE (continuous)

Metrics are collected automatically and dashboarded:

| Metric | Source | Target |
|--------|--------|--------|
| Rule enforcement rate (denials / total tool calls) | `.audit/violations.jsonl` | >0% (rules are firing) |
| False-positive rate (denials overturned by user) | User feedback log | <5% |
| PDP latency (p95) | Hook timing logs | <2 seconds |
| Test coverage (line) | `pytest --cov` | ≥90% enforcement, ≥85% validation |
| Mutation score | `mutmut` nightly | ≥80% |
| Canary pass rate | Nightly canary run | 100% |
| Rules with 0 enforcement events (past 30 days) | Audit report | Review quarterly — remove or downgrade |
| SSOT violations caught in CI | CI logs | 0 (all caught pre-merge) |

#### Step 2: HYPOTHESIZE (weekly)

The weekly audit report (from Layer 5) identifies candidates for improvement. Each candidate becomes a hypothesis:

- **Rule never fires** → Hypothesis: "This rule is redundant or the check is broken." Test: review the rule, verify the check function, decide remove vs. fix.
- **Rule fires too often** → Hypothesis: "This rule is too strict or the agent doesn't understand it." Test: review deny reasons, decide loosen vs. add agent training.
- **Mutation score drops** → Hypothesis: "Recent changes introduced untested code paths." Test: identify the surviving mutations, add targeted tests.
- **Canary fails** → Hypothesis: "A rule or hook change broke expected behavior." Test: bisect to the commit, fix, add regression fixture.

#### Step 3: TEST (before ship)

Every hypothesis becomes a code/rule change, and every change ships behind tests:

1. Write the fix
2. Write/update test cases (unit + integration + regression fixture if it's a bug fix)
3. Run the full test suite locally
4. Open PR — CI runs the full pyramid (unit, integration, property, mutation, canary)
5. Coverage gate checks thresholds
6. Code review
7. Merge only if all gates pass

#### Step 4: SHIP & MONITOR (post-merge)

After merge, the canary runs nightly. If the canary fails on the new code, an automatic revert PR is opened. The audit log tracks whether the change actually improved the target metric (e.g., did false positives drop?).

### 9.11 Drift Detection

Over time, rules and code drift apart. A rule's regex might not match a new file-naming convention. A hook might reference a Policy Card field that was renamed. Drift detection catches this automatically.

```python
# scripts/audit/drift_detection.py
#!/usr/bin/env python3
"""
Drift detector: compares what rules SAY they check vs. what rules ACTUALLY check.
Runs nightly. Flags any rule where the documented behavior diverges from actual.
"""
import yaml
from pathlib import Path
from datetime import datetime, timedelta

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CARDS_DIR = PROJECT_ROOT / "governance" / "policy-cards"
AUDIT_LOG = PROJECT_ROOT / ".audit" / "violations.jsonl"

def detect_rule_drift():
    """For each rule, compare documented check vs. actual enforcement events."""
    import json
    
    # Load last 30 days of audit events
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    enforcement_events = {}  # rule_id -> count
    if AUDIT_LOG.exists():
        for line in AUDIT_LOG.read_text().splitlines():
            entry = json.loads(line)
            ts = datetime.fromisoformat(entry["timestamp"].replace("Z", "+00:00"))
            if ts.replace(tzinfo=None) >= thirty_days_ago:
                rid = entry.get("rule_id")
                if rid:
                    enforcement_events[rid] = enforcement_events.get(rid, 0) + 1
    
    # Compare against declared rules
    drift_report = []
    for card_file in CARDS_DIR.rglob("*.yaml"):
        card = yaml.safe_load(card_file.read_text())
        rid = card["id"]
        event_count = enforcement_events.get(rid, 0)
        
        # Drift signals:
        # 1. Rule is blocking but has 0 enforcement events in 30 days
        if card["severity"] == "blocking" and event_count == 0:
            drift_report.append({
                "rule_id": rid,
                "file": str(card_file),
                "signal": "blocking_rule_never_fired",
                "message": f"Blocking rule {rid} has 0 enforcement events in 30 days. "
                           f"Check function may be broken or rule may be redundant."
            })
        
        # 2. Rule's check type doesn't match any implemented evaluator function
        check_type = card.get("check", {}).get("type")
        if check_type and not evaluator_exists(check_type):
            drift_report.append({
                "rule_id": rid,
                "file": str(card_file),
                "signal": "check_type_not_implemented",
                "message": f"Rule {rid} uses check type '{check_type}' but no "
                           f"evaluator function exists for it."
            })
    
    return drift_report

def evaluator_exists(check_type: str) -> bool:
    """Verify that the check_type has a corresponding evaluator function."""
    from enforcement.evaluator import EVALUATORS  # dict of type -> function
    return check_type in EVALUATORS

if __name__ == "__main__":
    drift = detect_rule_drift()
    if drift:
        print(f"⚠️  Drift detected in {len(drift)} rules:")
        for d in drift:
            print(f"  - {d['rule_id']}: {d['signal']} — {d['message']}")
    else:
        print("✓ No drift detected — all rules are consistent with enforcement")
```

### 9.12 Test Cadence Summary

| Test type | When it runs | Max duration | Blocks merge? |
|-----------|-------------|--------------|---------------|
| Unit (constitution, cards, PDP, validators, audit) | Pre-commit | 2 seconds | Yes (pre-commit) |
| Integration (PDP + real stdin, cross-layer) | CI (every PR) | 2 minutes | Yes (CI gate) |
| Coverage gate | CI (every PR) | 1 minute | Yes (CI gate) |
| Canary (end-to-end scripted session) | Nightly + post-merge | 5 minutes | Yes (revert on fail) |
| Mutation (mutmut) | Nightly | 1 hour | No (advisory, trend-tracked) |
| Property (Hypothesis, 500+ cases) | CI (every PR) | 3 minutes | Yes (CI gate) |
| Drift detection | Nightly | 30 seconds | No (advisory, opens issue) |
| Regression (bug fixtures) | CI (every PR) | 1 minute | Yes (CI gate) |

### 9.13 What This Testing Architecture Buys You

| Without Layer 6 | With Layer 6 |
|-----------------|--------------|
| "I think the rules work" | "The rules work — here are the 247 tests that prove it" |
| Bugs discovered in production | Bugs discovered in CI (before merge) |
| Rule changes ship behind hope | Rule changes ship behind test cases that must pass |
| Silent enforcement failures | Drift detection flags them within 24 hours |
| No way to know if tests are meaningful | Mutation testing verifies tests catch real bugs |
| Improvements are guesses | Improvements are hypotheses tested against metrics |
| Regressions recur | Regression fixtures ensure each bug is fixed once, forever |

The testing layer is what makes this a *engineering* project rather than a *documentation* project. Without it, the harness is a well-architected theory. With it, the harness is a verified, evolving system.

---

## 10. Token Optimization Strategy

The SovereignAI analysis found that loading all rule files at session start consumes approximately 14,000 tokens — 10-12% of a 128K context window. This design targets **under 1,000 tokens** for governance at session start, a 93% reduction.

### 10.1 Three-Tier Progressive Disclosure

| Tier | What loads | When | Token cost |
|------|-----------|------|-----------|
| Tier 1: Constitution | `governance/constitution.yaml` (4-tier hierarchy + ~6 principles) | Always (SessionStart hook) | ~500 tokens |
| Tier 2: Rule Index | `governance/rule-index.yaml` (auto-generated: ID + 1-line summary + severity) | Always (SessionStart hook) | ~300 tokens |
| Tier 3: Full Policy Cards | Individual `governance/policy-cards/**/*.yaml` files | On-demand (rule-lookup skill) | 0 tokens until needed |
| **Total at session start** | | | **approximately 800 tokens** |

### 10.2 Comparison with Prose-Based Harness

| Approach | Session-start tokens | Mechanism |
|----------|---------------------|-----------|
| SovereignAI (all 5 rule files, always_on) | ~14,000 | Eager load all prose rules |
| This design (constitution + rule index) | ~800 | Progressive disclosure |
| **Reduction** | **94%** | |

### 10.3 How the Rule Index Stays Compact

The rule index is auto-generated from Policy Cards and contains only three fields per rule:

```yaml
# Auto-generated — do not edit
agent: architect
total_rules: 33
total_tokens: 287
rules:
  - id: ARCH-001
    s: "Use relative paths, never absolute system paths"  # 's' = summary (short key)
    v: blocking  # 'v' = severity (short key)
  - id: ARCH-002
    s: "Every workflow must include Load Governance Rules + Select Execution Mode"
    v: blocking
  # ...
```

The agent sees the rule IDs and summaries at all times. When it needs the full check definition (regex patterns, params, exemptions), it invokes the `rule-lookup` skill:

```yaml
# .claude/skills/rule-lookup/SKILL.md
---
name: rule-lookup
description: Load the full definition of a specific Policy Card by ID. Use when you need to understand exactly what a rule checks, what patterns it denies, or what exemptions it has.
triggers:
  - type: model
    pattern: "rule-lookup"
allowed-tools:
  - read
---

# Rule Lookup Skill

## When to use
- You need the full check definition for a rule ID you saw in the rule index
- You want to understand why a tool call was denied
- You need to verify whether a specific action is allowed before taking it

## How to use
1. Identify the rule ID (e.g., ARCH-014) from the rule index or a denial message
2. Read the corresponding Policy Card file:
   - Shared rules: `governance/policy-cards/shared/<domain>.yaml`
   - Agent rules: `governance/policy-cards/<agent>/<domain>.yaml`
3. The Policy Card contains: rule statement, check definition, test cases, exemptions

## Example
If the rule index shows `ARCH-014: "Architect uses Manual execution mode by default"`:
- Read `governance/policy-cards/architect/execution-modes.yaml`
- The card's `check` field tells you exactly what the hook evaluates
```

### 10.4 Context Reload After Compaction

Context compaction can evict the constitution and rule index from context. The `PostCompaction` hook reloads them:

```python
# scripts/enforcement/post_compact_reload.py
#!/usr/bin/env python3
"""Reload constitution + rule index after context compaction."""
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CONSTITUTION = PROJECT_ROOT / "governance" / "constitution.yaml"
RULE_INDEX = PROJECT_ROOT / "governance" / "rule-index.yaml"

def main():
    try:
        constitution = CONSTITUTION.read_text()
        rule_index = RULE_INDEX.read_text()
        
        # Inject as additionalContext — this re-populates the model's context
        output = {
            "hookSpecificOutput": {
                "additionalContext": (
                    "# Constitution (reloaded after compaction)\n"
                    f"{constitution}\n\n"
                    "# Rule Index (reloaded after compaction)\n"
                    f"{rule_index}\n"
                )
            }
        }
        print(json.dumps(output))
    except Exception as e:
        # Fail gracefully — don't block the session
        print(json.dumps({"error": str(e)}))
    
    exit(0)

if __name__ == "__main__":
    main()
```

---

## 11. Directory Structure (From Scratch)

```
project-root/
│
├── .claude/                          # Devin CLI configuration
│   ├── settings.json                 # Hook registration (see §6.3)
│   ├── agents/                       # Agent definitions (AGENTS.md format)
│   │   ├── architect.md
│   │   ├── planner.md
│   │   ├── executor.md
│   │   ├── researcher.md
│   │   └── reviewer.md
│   └── skills/                       # Progressive-disclosure skills
│       ├── rule-lookup/
│       │   └── SKILL.md
│       ├── harness-audit/
│       │   └── SKILL.md
│       └── rule-cleanup/
│           └── SKILL.md
│
├── governance/                       # THE SSOT for all governance
│   ├── constitution.yaml             # 4-tier precedence hierarchy (~500 tokens)
│   ├── rule-index.yaml               # Auto-generated compact index (~300 tokens)
│   │
│   ├── policy-cards/                 # Machine-readable rules (Layer 2)
│   │   ├── shared/                   # Cross-agent rules (SSOT)
│   │   │   ├── frontmatter.yaml
│   │   │   ├── file-placement.yaml
│   │   │   ├── safety-commands.yaml
│   │   │   ├── execution-modes.yaml
│   │   │   ├── ssot-dedup.yaml
│   │   │   └── dead-references.yaml
│   │   ├── architect/
│   │   │   ├── workflow-structure.yaml
│   │   │   ├── hook-config.yaml
│   │   │   └── skill-organization.yaml
│   │   ├── planner/
│   │   │   └── plan-naming.yaml
│   │   ├── executor/
│   │   │   └── test-coverage.yaml
│   │   ├── researcher/
│   │   │   └── citation-requirements.yaml
│   │   └── reviewer/
│   │       └── review-criteria.yaml
│   │
│   ├── schemas/                      # JSON Schemas for validation
│   │   ├── policy-card.schema.json
│   │   ├── constitution.schema.json
│   │   └── agent.schema.json
│   │
│   └── tests/                        # Test fixtures for rule test_cases
│       └── fixtures/
│           ├── valid_frontmatter.md
│           ├── missing_persona.md
│           └── no_frontmatter.md
│
├── scripts/                          # All executable scripts
│   ├── enforcement/                  # Layer 3: Hook scripts (PDPs)
│   │   ├── pre_tool_pdp.py           # Policy Decision Point
│   │   ├── post_tool_validator.py    # Advisory validation
│   │   ├── session_init.py           # Context loading
│   │   └── post_compact_reload.py    # Context restoration
│   │
│   ├── validation/                   # Layer 4: CI validators
│   │   ├── validate_policy_cards.py
│   │   ├── lint_ssot_duplicates.py
│   │   ├── lint_dead_references.py
│   │   ├── validate_frontmatter.py
│   │   ├── run_rule_tests.py
│   │   ├── check_rule_coverage.py
│   │   └── check_constitution_consistency.py
│   │
│   └── audit/                        # Layer 5: Audit pipeline
│       ├── collect_violations.py
│       ├── weekly_review_report.py
│       └── drift_detection.py         # Layer 6: Nightly drift detection
│
├── tests/                            # Layer 6: The test pyramid
│   ├── unit/                         # Fast, isolated (<2s, pre-commit)
│   │   ├── test_constitution.py
│   │   ├── test_policy_cards.py
│   │   ├── test_pdp_unit.py
│   │   ├── test_ssot_linter.py
│   │   └── test_audit_pipeline.py
│   ├── integration/                  # Cross-layer, real stdin (CI, every PR)
│   │   └── test_pdp_integration.py
│   ├── e2e/                          # Canary sessions (nightly + post-merge)
│   │   └── test_canary_session.py
│   ├── property/                     # Hypothesis property-based tests (CI)
│   │   └── test_pdp_properties.py
│   ├── mutation/                     # Mutation test runner (nightly)
│   │   └── test_mutation_score.py
│   ├── regression/                   # Bug fixtures — one test per past bug
│   │   ├── test_sovereignai_001_ghost_reference.py
│   │   ├── test_sovereignai_002_ssot_duplication.py
│   │   └── ...
│   └── fixtures/
│       └── regression/               # YAML bug reproduction fixtures
│           ├── SOVEREIGNAI-001-ghost-reference.yaml
│           └── ...
│
├── workflows/                        # Workflow definitions (markdown, but schema-validated)
│   ├── architect/
│   ├── planner/
│   ├── executor/
│   ├── researcher/
│   └── reviewer/
│
├── .audit/                           # Runtime audit artifacts (gitignored)
│   ├── violations.jsonl
│   ├── weekly-reviews/
│   │   └── review-2026-08-01.md
│   └── drift-reports/                # Nightly drift detection output (gitignored)
│
├── .github/
│   └── workflows/
│       ├── governance-validation.yml # CI pipeline (see §7.2)
│       ├── coverage-gate.yml         # Coverage gate (see §9.8)
│       └── nightly-testing.yml       # Canary + mutation + drift (see §9.12)
│
├── .pre-commit-config.yaml           # Pre-commit hooks (see §7.1)
│
├── pyproject.toml                    # Project metadata + pytest + dependencies
│
└── .gitignore                        # Includes .audit/, __pycache__, etc.
```

### 11.1 Key Structural Decisions

1. **`governance/` is the SSOT.** All rules, schemas, and the constitution live here. No governance content lives in `.claude/` or `scripts/` — those directories contain only configuration and code.

2. **`.claude/` is configuration only.** Agent definitions (AGENTS.md format) and skill definitions (SKILL.md format) live here. These reference `governance/` but do not contain rules.

3. **`scripts/enforcement/` vs `scripts/validation/`.** Enforcement scripts run at runtime (hooks); validation scripts run at build time (CI/pre-commit). They share no code — enforcement must be fast (5-second timeout) while validation can be comprehensive.

4. **`.audit/` is gitignored.** Runtime violation logs are not source files. The weekly review reports are committed (they're the audit trail) but the raw JSONL is not.

5. **No `Rules/` directory.** The SovereignAI analysis found dead references to a `Rules/` directory that didn't exist. In this design, rules are always in `governance/policy-cards/` — there is no alternative location to reference.

6. **Lowercase everywhere.** Unlike SovereignAI's mixed `Scripts/` (Title Case) and `app/` (lowercase), this design uses lowercase consistently for all directories. This eliminates one class of path-mismatch bugs. **Note:** Consistent case helps with cross-platform compatibility but does not eliminate all case-sensitivity issues (e.g., regex patterns, rule ID cross-references, or filesystem differences between case-sensitive Linux CI and case-insensitive macOS/Windows dev environments).

---

## 12. Implementation Roadmap

A five-phase build, designed so each phase produces a working (if incomplete) harness — and each phase ships with its tests.

### Phase 1: Foundation (Week 1) — Working PDP with 3 rules

**Goal:** A harness that blocks destructive commands and validates frontmatter.

| Step | Deliverable | Verification |
|------|-------------|--------------|
| 1.1 | Create directory structure (§11) | `ls` confirms all dirs exist |
| 1.2 | Write `governance/constitution.yaml` with 4-tier hierarchy | Schema validation passes |
| 1.3 | Write `governance/schemas/policy-card.schema.json` | `jsonschema` validates schema itself |
| 1.4 | Write 3 Policy Cards: `safety-commands.yaml`, `frontmatter.yaml`, `file-placement.yaml` | All pass schema validation |
| 1.5 | Write `scripts/enforcement/pre_tool_pdp.py` | Manual test: `echo '{"tool":"bash","input":{"command":"rm -rf tests/"}}' \| python pre_tool_pdp.py` returns deny |
| 1.6 | Register hooks in `.claude/settings.json` | Session starts without error; destructive commands are blocked |
| 1.7 | Write `.gitignore` (includes `.audit/`) | `git status` shows no audit artifacts |
| **1.8** | **Write `tests/unit/test_constitution.py` + `tests/integration/test_pdp_integration.py`** (§9.2, §9.4) | **`pytest tests/` passes — constitution schema, PDP deny/allow, malformed stdin handled** |

**Exit criteria:** Running `rm -rf tests/` in a Devin CLI session is blocked. Writing a `.md` file without frontmatter is blocked. **The test suite passes and verifies both behaviors.**

### Phase 2: Validation (Week 2) — CI pipeline + SSOT linter

**Goal:** No malformed Policy Card or SSOT violation can merge to main.

| Step | Deliverable | Verification |
|------|-------------|--------------|
| 2.1 | Write `scripts/validation/validate_policy_cards.py` | Validates all cards against schema |
| 2.2 | Write `scripts/validation/lint_ssot_duplicates.py` | Flags any duplicated rule statement |
| 2.3 | Write `scripts/validation/lint_dead_references.py` | Flags any dead .md link |
| 2.4 | Write `scripts/validation/run_rule_tests.py` | Runs every card's test_cases |
| 2.5 | Configure `.pre-commit-config.yaml` | Pre-commit runs all 4 validators |
| 2.6 | Configure `.github/workflows/governance-validation.yml` | CI runs all validators on PR |
| **2.7** | **Write `tests/unit/test_policy_cards.py` + `tests/unit/test_ssot_linter.py`** (§9.3, §9.5) | **Validator tests pass — SSOT linter flags known duplicates, all cards have ≥2 test cases** |
| **2.8** | **Add coverage gate to CI** (§9.8) | **CI fails if enforcement line coverage <90%** |

**Exit criteria:** A PR that adds a Policy Card with a duplicated rule statement is blocked by CI. A PR with a dead markdown reference is blocked by pre-commit. **A PR that drops test coverage below 90% is blocked by the coverage gate.**

### Phase 3: Audit Loop (Week 3) — Closed feedback

**Goal:** Violations are logged and reviewed weekly.

| Step | Deliverable | Verification |
|------|-------------|--------------|
| 3.1 | Confirm `.audit/violations.jsonl` is being written by PDP | File exists and grows after tool calls |
| 3.2 | Write `scripts/audit/weekly_review_report.py` | Generates markdown report |
| 3.3 | Set up weekly cron job (GitHub Actions scheduled workflow) | Report generates automatically every Monday |
| 3.4 | Write first 5 agent Policy Cards (architect, planner, executor, researcher, reviewer) | All pass validation |
| **3.5** | **Write `tests/unit/test_audit_pipeline.py`** (§9.6) | **Audit tests pass — log_decision writes valid JSONL, weekly report aggregates correctly** |

**Exit criteria:** Weekly report shows top-violated rules, never-fired rules, and recommends actions. **Audit pipeline tests verify no violations are silently dropped.**

### Phase 4: Optimization (Week 4) — Token efficiency + skills

**Goal:** Session-start token budget under 1,000; full progressive disclosure working.

| Step | Deliverable | Verification |
|------|-------------|--------------|
| 4.1 | Write `scripts/enforcement/session_init.py` (loads constitution + rule index) | Session-start context includes both |
| 4.2 | Write `governance/rule-index.yaml` auto-generator | Script produces compact index from Policy Cards |
| 4.3 | Write `scripts/enforcement/post_compact_reload.py` | PostCompaction reloads constitution + index |
| 4.4 | Write `.claude/skills/rule-lookup/SKILL.md` | Agent can load full Policy Card on demand |
| 4.5 | Write `.claude/skills/harness-audit/SKILL.md` | Agent can run audit on demand |
| 4.6 | Write `.claude/skills/rule-cleanup/SKILL.md` | Agent can propose rule dedup/refactor |
| 4.7 | Measure session-start token count | Confirm <1,000 tokens |

**Exit criteria:** `SessionStart` hook injects constitution + rule index. Agent can use `rule-lookup` skill to load full rule definitions. Token budget verified under 1,000.

### Phase 5: Rigorous Testing & Continuous Improvement (Week 5+) — Layer 6

**Goal:** The harness is verified to work — not just assumed to work. Every layer has a test pyramid; every change ships behind tests; the improvement cycle drives evolution.

| Step | Deliverable | Verification |
|------|-------------|--------------|
| 5.1 | Write `tests/e2e/test_canary_session.py` with 7+ canary cases (§9.7) | Nightly canary run passes 100% |
| 5.2 | Install `mutmut` and write `tests/mutation/test_mutation_score.py` (§9.7) | Mutation score ≥80% (after iteration cycle) |
| 5.3 | Install `hypothesis` and write `tests/property/test_pdp_properties.py` (§9.7) | 500 random inputs — PDP never crashes |
| 5.4 | Create `tests/fixtures/regression/` and write first 5 regression fixtures from SovereignAI bugs (§9.9) | All 5 regression tests pass |
| 5.5 | Write `scripts/audit/drift_detection.py` (§9.11) | Nightly drift detection runs, opens issues on drift |
| 5.6 | Configure nightly GitHub Actions workflow (canary + mutation + drift) | Workflow runs at 02:00 UTC, posts results to dashboard |
| 5.7 | Wire canary failure → automatic revert PR | Post-merge canary failure opens revert PR within 5 minutes |
| 5.8 | Define and dashboard the 8 improvement metrics (§9.10 Step 1) | Metrics visible in GitHub Actions dashboard |
| 5.9 | Run first weekly improvement review using the MEASURE → HYPOTHESIZE → TEST → SHIP cycle (§9.10) | At least one rule improvement shipped from data |

**Exit criteria:** The full test pyramid runs nightly: unit (seconds), integration (minutes), canary (5 min), mutation (1 hr), property (3 min), drift (30 sec). Mutation score ≥80%. Canary pass rate 100%. Drift detection opens issues automatically. The improvement cycle has produced at least one data-driven rule change.

---

## 13. Anti-Patterns to Avoid

These are the failure modes found in the SovereignAI analysis (Chapter 5 of the prior report) that this design explicitly prevents.

### 13.1 Prose Rules Instead of Data

**Anti-pattern:** Writing rules as `ALWAYS` / `NEVER` bullet lists in markdown.
**Why it fails:** The model interprets prose probabilistically. It cannot be tested, schema-validated, or deterministically enforced.
**This design:** Rules are YAML Policy Cards with JSON Schema validation and executable test cases.

### 13.2 Ghost References

**Anti-pattern:** Rules that reference components that don't exist (SovereignAI's `Rule_Following_Hook`).
**Why it fails:** The rule appears to govern behavior but nothing enforces it.
**This design:** Every Policy Card's `check.type` maps to a function in the enforcement module. The CI `check_constitution_consistency.py` validator verifies that every `constitutional_basis` references a valid principle.

### 13.3 SSOT Duplication

**Anti-pattern:** The same rule content copied across 4 files (SovereignAI's `Execution_Mode_Patterns.md`).
**Why it fails:** Updates to one copy don't propagate; copies drift.
**This design:** The SSOT dedup linter (§7.3) hashes every rule statement and blocks any PR that introduces a duplicate. Shared rules live in `governance/policy-cards/shared/` and are referenced by ID via `refines:`.

### 13.4 Absolute Windows Paths in Hooks

**Anti-pattern:** `C:/SovereignAI/Scripts/...` in hook commands.
**Why it fails:** Breaks on any non-Windows OS or any machine where the repo isn't at `C:/SovereignAI`.
**This design:** All hook commands use relative paths (`python scripts/enforcement/...`) because Devin CLI invokes hooks from the project root.

### 13.5 Eager-Loading All Rules

**Anti-pattern:** Setting `trigger: always_on` on all rule files (SovereignAI's 14K token session-start load).
**Why it fails:** Consumes 10-12% of context window before the user's task enters context.
**This design:** Three-tier progressive disclosure — constitution (always) + rule index (always) + full cards (on-demand). Session-start budget: approximately 800 tokens.

### 13.6 No Audit Loop

**Anti-pattern:** Rules are written but never reviewed. Violations are not logged.
**Why it fails:** Rules drift from reality. Broken rules stay broken. Effective rules can't be identified.
**This design:** Every PDP decision is logged to `.audit/violations.jsonl`. A weekly cron job generates a review report identifying top-violated rules, never-fired rules, and recommended actions.

### 13.7 Mixing Constitutional Principles with Operational Rules

**Anti-pattern:** Putting safety principles and file-placement rules in the same file (SovereignAI's `architect.md`).
**Why it fails:** The file becomes too long to always keep in context, so principles get lazy-loaded and are sometimes absent when needed.
**This design:** Constitution (principles, precedence) is separate from Policy Cards (operational rules). Constitution is always loaded; Policy Cards are loaded on-demand.

### 13.8 No Test Cases for Rules

**Anti-pattern:** Rules have no test cases. You can't verify a rule works until it fails in production.
**Why it fails:** Rule changes ship broken. Rule behavior is undefined for edge cases.
**This design:** Every Policy Card requires `minItems: 2` test cases. CI runs all test cases on every PR. A rule change that breaks a test case is blocked.

### 13.9 Tests That Pass But Don't Verify (No Mutation Testing)

**Anti-pattern:** A test suite with 90% coverage that silently passes even when the code is broken. The tests exercise the code paths but don't assert meaningful invariants.
**Why it fails:** Coverage measures *execution*, not *verification*. A test that calls `evaluate_rule()` but doesn't assert the decision is a coverage-inflating no-op. The team believes the harness is tested; the harness is actually unverified.
**This design:** Mutation testing (§9.7) deliberately introduces bugs (flip `==` to `!=`, delete lines, change regexes) and re-runs the tests. If the tests still pass, the mutation "survived" — a coverage gap. The mutation score gate (≥80%) ensures tests actually catch bugs, not just execute code.

### 13.10 No Improvement Cycle (Tests Run But Nothing Improves)

**Anti-pattern:** Tests run in CI, results are green, but nobody acts on the data. Violations accumulate, rules drift, false-positive rates creep up — and the harness slowly stops working while the dashboard stays green.
**Why it fails:** Testing without an improvement cycle is just expensive monitoring. You know it's broken; you don't fix it. The SovereignAI analysis found rules that referenced non-existent components for months — the audit log would have shown zero enforcement events, but nobody reviewed it.
**This design:** The MEASURE → HYPOTHESIZE → TEST → SHIP cycle (§9.10) forces action. The weekly audit report identifies candidates for improvement. Each candidate becomes a hypothesis that must be tested and shipped. Drift detection (§9.11) opens issues automatically. The improvement metrics (§9.10 Step 1) are dashboarded with targets — if a metric misses its target, an issue is opened.

---

## 14. Research Citations

This design synthesizes findings from the following sources, accessed on 2026-08-01.

### Primary Sources (Deep-Read)

1. **Mavračić, J. (2025).** "Policy Cards: Machine-Readable Runtime Governance for Autonomous AI Agents." arXiv:2510.24383v1. https://arxiv.org/html/2510.24383v1 — *Source of the Policy Card schema concept, Declare-Do-Audit lifecycle, and machine-readable governance argument.*

2. **Kumar, R. (2026).** "Hooks: The Enforcement Layer That Turns Agent Policy Into Agent Fact." https://ranjankumar.in/hooks-policy-as-code-agent-enforcement — *Source of the "prompts suggest, hooks enforce" principle and the Probabilistic-to-Deterministic Boundary concept.*

3. **Isenberg, R. (2026).** "Agentic Coding Hooks: Deterministic AI Guardrails." https://ranthebuilder.cloud/blog/agentic-coding-hooks-deterministic-ai-guardrails — *Source of the "use hooks sparingly" principle and the Claude Code hook event taxonomy.*

4. **Pan, T. (2026).** "Policy-as-Code for Agents: OPA, Rego, and the Decision Point Your Tool Loop Doesn't Have." https://tianpan.co/blog/2026-04-25-policy-as-code-agent-permissions-opa-rego — *Source of the Policy Decision Point pattern and the argument that the model is not the authorization layer.*

5. **Anthropic (2025).** "Equipping Agents for the Real World with Agent Skills." https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills — *Source of the progressive disclosure pattern (name+description in system prompt, full SKILL.md on-demand).*

6. **Anthropic (2026).** "Claude's Constitution." https://www.anthropic.com/constitution — *Source of the 4-tier precedence hierarchy (safety > ethics > compliance > helpfulness).*

7. **Kyndryl (2026).** "How Policy as Code Governs AI Agents." https://www.kyndryl.com/us/en/insights/articles/2026/03/policy-as-code-agentic-ai — *Source of the "policy as code turns agents of chaos into careful collaborators" framing.*

### Supporting Sources (Search Results)

8. **agents.md** — Open format for guiding coding agents. https://agents.md
9. **Claude Code Hooks Reference.** https://code.claude.com/docs/en/hooks
10. **Anthropic Skills Repository.** https://github.com/anthropics/skills
11. **OPA vs Cedar vs Zanzibar: 2025 Policy Engine Guide.** https://www.osohq.com/learn/opa-vs-cedar-vs-zanzibar
12. **"Minimum Viable Context: Right Context, Right Time."** Medium, Data Science Collective.
13. **"Budget-Aware Context Management for Long-Horizon Reasoning."** arXiv, April 2026.
14. **Pre-commit hooks for AI agent skills.** r/devsecops, 2026.

### Prior Work

15. **Z.ai (2026).** "SovereignAI Harness Analysis Report." — *The prior analysis that identified the anti-patterns this design avoids. Available at `/home/z/my-project/download/SovereignAI_Harness_Analysis_Report.md`.*

---

*End of design blueprint. This document was prepared by Z.ai on 2026-08-01 based on 9 web searches, 7 deep-read sources, and the prior SovereignAI Harness Analysis. The design is a blueprint — implementation requires the four-phase roadmap in §11.*
