# AI Handoff — SovereignAI

**Version:** v1.4
**Last Updated:** 2026-07-20

## Section 1: Repository Setup

**Source of truth**: https://github.com/AngusKingCAI/SovereignAI
**Default branch**: `main`
**Path convention**: All repo paths use forward slashes (`/`). No host-local paths in plans or prompts.

### Directory Structure

| Path | Purpose |
|------|---------|
| `plans/` | Active plan files |
| `plans/completed/` | Executed plan files (moved after `/close`) |
| `.agent/architect/` | Architect governance: `PRINCIPLES.md`, `AI_HANDOFF.md`, `ARCHITECT_PATTERNS.md` |
| `.agent/executor/` | Executor governance: `OR_RULES.md`, `ARCHITECTURE.md`, hooks, scripts, traces |
| `.agent/shared/` | Shared state: `CHANGELOG.md`, `PLANS.md`, `LANDMINES.md`, `DEBT.md` |
| `.devin/skills/` | Workflow skills: `open/`, `verify/`, `close/`, `scan/` |
| `AGENTS.md` | Universal invariants (Executor reads at S0.2) |

### Clone & Verify

```bash
# Safe clone with verification
cd /tmp && rm -rf SovereignAI
git clone --depth 1 https://github.com/AngusKingCAI/SovereignAI.git
cd SovereignAI

# Verify clone succeeded
git log --oneline -1 || { echo "Clone failed"; exit 1; }
git config --global --add safe.directory $(pwd)
```

**Post-clone checklist** — Architect verifies presence of:
- `.agent/architect/PRINCIPLES.md`
- `.agent/architect/ARCHITECT_PATTERNS.md`
- `.agent/shared/PLANS.md`
- `AGENTS.md`
- `plans/` directory

### Tag Convention

- Plan completion tags: `plan-{N}` (e.g., `plan-28`)
- Scan tags: `scan-{N}` (e.g., `scan-15`) — see Section 5 Scan Trigger for range-review procedure
- Plans in progress carry no tag until completion
- No other tags without explicit plan instruction

---


## Section 2: Document Authority & Relationships

| Document | Responsibility | Content Authority | File Writer |
|---|---|---|---|
| `.agent/architect/AI_HANDOFF.md` | Process guide | Architect | Architect (user request only) |
| `PRINCIPLES.md` | Living principles | User + Architect | Architect (user request only) |
| `.agent/architect/ARCHITECT_PATTERNS.md` | Architect authoring patterns (self-check reference, not execution-affecting) | Architect | Executor (per plan instruction) |
| `.agent/executor/OR_RULES.md` | Operational rules (UOR/VOR/OOR/COR) | Architect | Executor (per plan instruction) |
| `.agent/executor/ARCHITECTURE.md` | Architecture constraints | Architect | Executor (per plan instruction) |
| `PLANS.md` | Dynamic state, baselines, queue | Executor | Executor |
| `.agent/shared/LANDMINES.md` | Failure patterns | Architect | Executor (per plan instruction) |
| `.agent/shared/CHANGELOG.md` | Per-plan change log | Executor | Executor |
| `AGENTS.md` | Universal Invariants | Executor | Executor |
| `.agent/shared/DEBT.md` | Non-rule deferred items | Architect (identification), Executor (resolution) | Executor |
| `roundtable-scores-plan-{N}.md` | Round Table panelist performance tracking | Architect (compilation) | Executor (per plan instruction) |
| `.devin/skills/*/SKILL.md` | Workflow skills | Architect | Architect (user request only) |

**SSOT**: Each fact in one document only.

**Read order**:
- Architect (new chat, Round Table workflow): `.agent/architect/AI_HANDOFF.md` → PRINCIPLES → `.agent/architect/ARCHITECT_PATTERNS.md` (Active section) → `.agent/executor/OR_RULES.md` → `.agent/executor/ARCHITECTURE.md` → PLANS → `.agent/shared/LANDMINES.md` → `.agent/shared/DEBT.md`
- Architect (new chat, Log Reading workflow): `.agent/architect/AI_HANDOFF.md` → PRINCIPLES → `.agent/executor/OR_RULES.md` → `.agent/executor/ARCHITECTURE.md` → PLANS → `.agent/shared/LANDMINES.md` → `.agent/shared/DEBT.md`
- Executor (S0.2): AGENTS.md → plan header AR/OR list → `.agent/executor/ARCHITECTURE.md` (relevant AR only) → `.agent/executor/OR_RULES.md` (relevant OR only)

**Rule References in Plans**:
- Architect lists specific AR/OR rules in plan header for executor context
- Executor reads only listed rules, not full documents
- Reference format: "Use {RULE-ID}" or "Follow {RULE-ID}"

**Rule Creation Mechanism**:
- Architect drafts new AR/OR/M rules with status `Proposed` during Log Reading Workflow
- Rules identified in Log Reading go directly to Executor Manifest as write-tasks (valid review path per GR12)
- Executor writes accepted rules to SSOT files (`.agent/executor/OR_RULES.md`, `.agent/executor/ARCHITECTURE.md`, `.agent/shared/LANDMINES.md`) per plan instruction
- No rule is written to SSOT without explicit plan instruction
- **Status transitions**: `Proposed` → `Accepted` occurs when the Executor writes the rule to SSOT per plan instruction. The Architect does not change rule status.
- **ARCHITECT_PATTERNS.md**: Architect identifies patterns during Round Table Step 5 (finding review). Patterns go to Executor Manifest as write-tasks. Executor writes all ARCHITECT_PATTERNS.md updates per plan instruction.

---


## Section 3: GR Rules (Architect Governance Rules)

**GR1.** Plan header lists `Vision principles:`, `AR rules:`, `OR rules:`, and `Open questions resolved:`.

**GR2.** Panelist responses attributed: `**Panelist**: <name/model>`.

**GR3.** Architect accepts/rejects every finding with reasoning.

**GR4.** No host-local paths in plans, briefs, prompts. Bare filenames for uploads; repo-relative paths for repo files.

**GR5.** New OR/AR rules: rule + rejected alternative + consequence — one line each.

**GR6.** Rules get stable IDs (AR{n}, OR{n}, M{n}). Status: Proposed / Accepted / Rejected / Superseded. Never delete. Accepted → `.agent/executor/ARCHITECTURE.md` or `.agent/executor/OR_RULES.md` (SSOT). Rejected → needs new evidence to re-propose.

**GR7.** Briefs: 9 sections in order, ≤80 lines. Missing/reordered sections block delivery.

**GR8.** Screen plans against `.agent/shared/LANDMINES.md` before Round Table. BLOCKING landmines fixed before delivery.

**GR9.** Majority of panelists must return verdict before delivery. Majority = >50% of invited panelists, minimum 2 panelists for valid Round Table. Conditional/block needs GR3 reasoning.

**GR10.** First pass per rev: full prompt. Re-checks: diff summary only. Round Table questions get Q-IDs. Answers become rule IDs or stay open.

**GR11.** Clean pass: post panelist scorecard inline (1-100, weighted toward accepted findings).

**GR12.** All rule changes are reviewed before SSOT write. Valid review path: Log Reading Workflow (execution-driven rule identification) or Round Table Workflow (pattern identification). No silent edits to `.agent/executor/OR_RULES.md`, `.agent/executor/ARCHITECTURE.md`, `.agent/shared/LANDMINES.md`, or `.agent/architect/ARCHITECT_PATTERNS.md`. Architect-only documents (PRINCIPLES.md) are written directly by the Architect. ARCHITECT_PATTERNS.md is written by Executor per plan instruction.

**GR13.** Every plan file MUST include an `## Executor Manifest` section after the header. The manifest lists phases, deliverables per phase, gates per phase, coverage target, and forbidden actions. No plan is valid without this section.

**GR14.** All workflow sections MUST reference applicable GR rules at the top of the section.

**GR15.** Architect MUST re-read governance documents before each new workflow invocation. Do not rely on cached context.

---


## Section 4: Compliance Artifacts

**Applicable GR Rules**: GR3, GR11, GR14, GR15
This workflow produces artifacts to prevent scope drift and verify exact procedure compliance. The Architect is an AI web chat — it cannot create files, save state, or persist data between sessions. All Architect compliance evidence exists **only in the chat transcript**. The human verifies by reading the chat history.

**Terminology Note**: When this workflow says "Draft" or "Create" rules/patterns, it means "prepare the content specification in the chat" — not "write to file". The Executor writes the actual files per plan instruction.

### Core Principle: The Chat Transcript IS the Only Audit Log

Every compliance line posted by the Architect becomes part of the permanent chat record. The human verifies by scrolling through the transcript. Missing lines, out-of-order lines, or ❌ without explanation = STOP and fix.

The Architect MUST NOT:
- Claim to have "saved" or "logged" anything outside the chat
- Refer to files it created in previous messages
- Batch compliance lines — each action gets its own gate message

---

### Executor Artifacts (Machine-Produced, File-Based)

| Artifact | Producer | Verified By | Purpose |
|----------|----------|-------------|---------|
| `trace-plan-{N}.jsonl` | Executor | `verify_execution.py` | Step-by-step execution log |
| `execution-attestation-plan-{N}.md` | Executor | `verify_execution.py` | Proves executor followed plan manifest |

**Rule**: No plan execution is merged to `main` until the execution attestation is verified via `verify_execution.py` and returns PASS.

---

### Architect Compliance (Inline Chat Only)

**Responsibility**: The Architect MUST post a compliance line immediately after completing each action. The line IS the proof. There is no other record.

**Format**: Descriptive action statement with ✅/❌/⏭️ prefix.

**Human verification checklist**:
- [ ] All actions have compliance lines posted as separate messages
- [ ] Lines are in chronological order
- [ ] All marks are ✅ or ⏭️
- [ ] Any ❌ has an explanation in the same or next message
- [ ] No actions are skipped

**STOP conditions**:
- Missing compliance line for any action
- Out-of-order lines
- ❌ without explanation
- Actions skipped without ⏭️ justification

---

### Round Table Compliance (Inline Chat Only)

**Responsibility**: The Architect MUST post one compliance line per finding immediately after reading each panelist's review. Each line IS the proof of addressing that finding.

**Format, verification checklist, and STOP conditions**: See Section 6 Step 4 — Process Findings.

---

### Session Continuity Rule

Because the Architect is a web chat with no persistent state:

**If the session ends before completion**, the human MUST:
1. Copy the entire chat transcript from this point forward
2. Paste it into the next session
3. The next Architect instance reads the transcript to reconstruct context

**The Architect MUST NOT**:
- Claim to have "saved progress" in a file
- Refer to state from a previous session without the human pasting the transcript
- Assume continuity without explicit transcript paste

The human is the state keeper. The chat transcript is the only state.

---


## Section 5: Log Reading Workflow

**Applicable GR Rules**: GR1, GR4, GR6, GR8, GR12, GR13, GR14, GR15

Triggered when user says "Log Pushed" or provides execution log. This workflow is iterative — may produce plan fix iterations (25.1, 25.2, etc.) before proceeding to Round Table or stopping.

---

### Scan Trigger

Every 5th plan (5, 10, 15, 20, 25, 30…) is a scan plan. Before drafting a scan plan, the Architect runs this Log Reading Workflow once per plan in the range since the last scan, not just the most recent plan.

**Range rule**: `scan-{N}` covers all plans completed since `scan-{N-5}` (or since the start, for `scan-5`). Example: while creating Plan 30, the Architect reads the execution logs for Plans 26, 27, 28, and 29 — each gets its own full pass through Steps 1–5 below — before Plan 30 (the fix/new-rules plan) is drafted.

1. Identify range: plans covered = last scan tag (exclusive) through current plan number (exclusive)
2. Post: `✅ Scan Range Identified: scan-{N}, covers plans {first}-{last}`
3. For each plan in range, repeat Steps 1–5 below in order, posting each step's compliance line with the plan number included (e.g., `✅ Read Log: execution-log-plan-27.md, ...`)
4. Post per plan: `✅ Scan Complete: plan-{n} reviewed, {issues found / no issues}`
5. After all plans in range are reviewed, proceed to Step 6 (Fix Plan Creation) for the scan plan itself, folding in findings from every plan in the range

---

### Step 1 — Clone, Verify Repo & Diff-Check

1. Clone repo
2. Post: `✅ Repo cloned: commit {hash}, branch {branch}`
3. Verify repo state (check key files exist, commit hash)
4. Post: `✅ Verified Repo: commit {hash}, tag {tag}, key files present`
5. Diff-check against plan expectations (if applicable)
6. Post: `✅ Diff-Check: {findings}`

---

### Step 2 — Read Log, CHANGELOG & PLANS.md

1. Read execution log
2. Post: `✅ Read Log: execution-log-plan-{N}.md, {lines} lines, {tests} tests, {stops} STOPs`
3. Read CHANGELOG latest entry
4. Post: `✅ Read CHANGELOG: latest entry {plan}-{rev}, {date}, {tests} tests`
5. Read PLANS.md current baseline
6. Post: `✅ Read PLANS.md: baseline {plan}-{rev}, queue: {plans}`
7. Read `logs/execution-attestation-plan-{N}.md`. Confirm attestation phases match the plan's Executor Manifest phases and that `verify_execution.py --final` result is PASS.
8. Post: `✅ Read Attestation: plan-{N}, {phases} phases, verify_execution.py {PASS/FAIL}`
9. If the attestation shows FAIL, phase mismatch, or the log shows errors/anomalies, read `.agent/executor/traces/trace-plan-{N}.jsonl` to identify the exact step where drift occurred.
10. Post: `✅ Read Trace: plan-{N}, {entries} entries, {finding or "no drift found"}` — or `⏭️ Skipped Trace: attestation clean, no drift indicators`

---

### Step 2.5 — File Inspection (If Needed)

If the log or attestation shows errors, failures, or anomalies, the Architect MAY read specific source files to diagnose root cause. Each file read gets its own gate.

1. Read relevant source file(s)
2. Post: `✅ Inspected File: {file-path}, {finding}`

---

### Step 3 — Read Governance (Individual Gates)

1. Read PRINCIPLES.md
2. Post: `✅ Read PRINCIPLES.md: {N} principles, {N} workflow principles`
3. Read OR_RULES.md
4. Post: `✅ Read OR_RULES.md: {N} rules`
5. Read ARCHITECTURE.md
6. Post: `✅ Read ARCHITECTURE.md: {N} active, {N} reserved, {N} retired`
7. Read LANDMINES.md
8. Post: `✅ Read LANDMINES.md: {N} active landmines`
9. Read DEBT.md
10. Post: `✅ Read DEBT.md: {N} open items`

---

### Step 4 — Debt Action (Individual Gates)

1. **Identify** rules eligible for promotion (plan completed successfully). Status remains `Proposed`.
2. Post: `✅ Identified Rules for Promotion: {rule-ids}, status remains Proposed`
3. Resolve debts if trigger fired or target plan reached
4. Post: `✅ Resolved Debts: {debt-ids}`
5. Block debts with justification if needed
6. Post: `✅ Blocked Debts: {debt-ids}, reason: {justification}`
7. **Add to Executor Manifest**: Eligible rules are added as write-tasks in the next plan's Executor Manifest (valid review path per GR12).
8. Post: `✅ Added to Executor Manifest: {rule-ids}`

---

### Step 5 — Draft Rules (Individual Gates)

1. Identify rule gaps from execution log
2. Post: `✅ Identified Gaps: {gap descriptions}`
3. **Draft** new AR specifications with status `Proposed`
4. Post: `✅ Created AR Rules: {AR-ids}`
5. **Draft** new OR specifications with status `Proposed`
6. Post: `✅ Created OR Rules: {OR-ids}`
7. **Draft** new landmine specifications with status `Proposed`
8. Post: `✅ Created Landmines: {M-ids}`
9. **Add to Executor Manifest**: All drafted rules are added as write-tasks in the next plan's Executor Manifest (valid review path per GR12).
10. Post: `✅ Added to Executor Manifest: {AR-ids}, {OR-ids}, {M-ids}`

---

### Step 5 Gate — Proceed or Ask User

After Step 5, the Architect assesses: are there issues requiring a plan revision?

- **Yes** (issues found): Proceed to Step 6 (Fix Plan Creation)
- **No** (no issues): Ask user how to proceed — do not auto-loop

**Post**: `✅ Step 5 Complete: {issues found / no issues}. Proceeding to {Step 6 / asking user}.`

---

### Step 6 — Fix Plan Creation

Plan creation under the log workflow produces iterative fixes to address issues found in execution logs. Each iteration increments the sub-version.

#### Plan Iteration Rules

| Iteration | Trigger | Example |
|-----------|---------|---------|
| 25.1 | First fix after log analysis | `plan-25.1.md` |
| 25.2 | Second fix after re-analysis | `plan-25.2.md` |
| 25.3 | Third fix | `plan-25.3.md` |
| 25.N | Nth fix | `plan-25.N.md` |

**Naming**: `plan-{N}.{i}.md` where `{N}` is the base plan number and `{i}` is the fix iteration. No Rev number in fix iterations.

**Size Limit**: Plans MUST be ≤120 lines unless user explicitly specifies override.

#### Fix Plan Creation Steps (with Executor Gates)

Each fix plan MUST include an Executor Manifest with gated phases. The Executor MUST verify each gate before proceeding to the next phase.

**6.1 — Assess Scope of Changes**

1. Categorize the delta: bugfix, missing requirement, new feature, architectural adjustment
2. Post: `✅ Assessed Scope: {category}, {description}`

**6.2 — Route to Appropriate Rework Level**

| Level | Scope | Action |
|-------|-------|--------|
| Patch | Small fix, single-file change | 1-3 tasks appended to existing plan |
| Plan | New tasks, modified requirements | Update plan document, preserve completed tasks |
| Design | Architectural changes | Scoped re-brainstorm, then plan update |

1. Select rework level based on scope assessment
2. Post: `✅ Rework Level: {patch/plan/design}, reason: {justification}`

**6.3 — Preserve Context from Previous Cycle**

1. Reference existing design doc and plan
2. Acknowledge what was implemented successfully
3. Avoid re-implementing completed tasks
4. Post: `✅ Preserved Context: {completed tasks acknowledged}`

**6.4 — Draft Fix Plan with Executor Manifest**

The fix plan MUST include an Executor Manifest with phases and gates:

```
## Executor Manifest
Phases: S0, S1, S2, ... S_close
Deliverables:
  - S<n>: <file-path> (<description>)
Gates per phase:
  - S<n>: <check1>, <check2>, ...
Coverage target: <N>%
Forbidden actions: <list>
```

1. Draft plan iteration addressing log issues
2. Post: `✅ Drafted Plan: plan-{N}.{i}.md, {lines} lines (limit: 120)`

**6.5 — Verify Plan Quality Gates**

Before delivering the fix plan, verify:

- [ ] Plan ≤120 lines (or user override specified)
- [ ] Executor Manifest present with phases and gates
- [ ] All referenced AR/OR rules exist in governance docs
- [ ] Active landmines addressed or documented
- [ ] No host-local paths in plan body

1. Run quality verification
2. Post: `✅ Verified Plan Quality: {checks passed}`

**6.6 — Deliver Fix Plan**

1. Present plan to user for review
2. Post: `✅ Fix Plan Ready: plan-{N}.{i}.md, {lines} lines, awaiting user review`

**User Decision Gate**:
- **Approve**: Proceed to Executor
- **Request more fixes**: Increment iteration (25.{i+1}), loop to 6.1
- **Reject**: Discard iteration, ask user for direction

---


## Section 6: Round Table Workflow

**Applicable GR Rules**: GR1, GR2, GR3, GR4, GR6, GR7, GR8, GR9, GR10, GR11, GR13, GR14, GR15

Triggered independently — may run while Executor is executing plans in parallel. User may engage this track without ever running the Log Reading Workflow. Round Table reviews new plans.

---

### Batch Process (Integrated)

4 plans per batch. 1 shared brief (Rev 1 only). 1 Round Table prompt per rev. Scan every 5 plans (5, 10, 15…) — see Section 5 Scan Trigger for scan procedure.

**Batch workflow**:
1. Draft 4 individual plan files + 1 brief (Rev 1) + 1 prompt per rev
2. Round Table reviews
3. Architect applies findings → Rev2 if needed
4. User copies finals to Executor

**Dependency**: If Plan {Xn} STOPs, all plans with `Depends on: {Xn}` also STOP. Binary.

---

### Brief Format (Rev 1 Only)

One brief per batch. ≤80 lines. 9 sections in order. Rev 2+ does not include brief unless user explicitly requests.

#### Section Order

1. **Context** — baseline, repo state.
2. **Plans in this batch** — table: plan #, title, depends on, vision principles, AR rules, OR rules.
3. **Rules carried forward** — AR/OR/M-IDs only, pointer to `.agent/executor/ARCHITECTURE.md` or `.agent/executor/OR_RULES.md` or `.agent/shared/LANDMINES.md`.
4. **Questions for Round Table** — Q-ID.
5. **Open questions resolved** — list resolved Q-IDs; "none" if none.
6. **Risks flagged** — includes landmine pre-screen.
7. **Coverage target**
8. **Round Table protocol reminder**
9. **Superseded rules** — AR/OR/M-ID + pointer to replacement.

#### Rules

- Missing/reordered sections block delivery (GR7).
- Brief is created at Rev 1 only. Rev 2+ does not include brief unless user explicitly requests.

---

### Round Table Revision Rules

Round Table revisions are separate from log-fix iterations. A plan enters Round Table at a specific version (e.g., 25.2) and then goes through Round Table revisions.

| Revision | Includes | Notes |
|----------|----------|-------|
| Rev 1 | Plans + Brief + Prompt | First pass with complete material |
| Rev 2+ | Plans + Prompt | Brief only if user explicitly requests |
| User override | As specified | User may request full re-review or brief at any rev |

**Naming**: Round Table revisions do not change the plan file name. The plan remains `plan-{N}.{i}.md` throughout Round Table. Only the prompt changes (Rev 1, Rev 2, etc.).

---

### Round Table Prompt Best Practices

The Round Table prompt follows the **Panel-of-Experts** pattern with **Parallel Fan-Out** to multiple panelists:

**Prompt Structure** (per GR10 and research best practices):

```
## ROLES
{Panelist role definitions with expertise areas}
Each panelist is an independent expert. If any panelist realizes they are
wrong at any point, they must acknowledge it and withdraw that finding.

## MATERIAL
- Brief: {brief content} (Rev 1 only, unless user requests for Rev 2+)
- Plans: {plan files}
- Dimensions: {evaluation dimensions}
- Risks: {pre-screened risks}
- Settled findings: {previously accepted findings}

## EVALUATION CRITERIA (Rubric-Based)
For each plan, evaluate across five dimensions:
1. Clarity & Specificity — are objectives and success criteria explicit?
2. Structural Organization — is the plan well-organized with clear sections?
3. Context Management — are instructions placed strategically around context?
4. Reasoning & Tool Guidance — does the plan guide the executor's thinking?
5. Examples & Output Control — are output formats and style rules defined?

## SEVERITY LEVELS (Threshold-Based)
- CRITICAL (Score 1-3): Data loss, security, irreversible damage. Blocks delivery.
- HIGH (Score 4-5): Executor STOP, test failure, broken build. Blocks delivery.
- MEDIUM (Score 6-7): Degraded functionality, tech debt. Address or document.
- LOW (Score 8-10): Style, naming. Architect discretion.

## ANSWER FORMAT
For each finding, provide:
**Finding ID**: RT-{N}
**Severity**: {CRITICAL|HIGH|MEDIUM|LOW}
**Dimension**: {which of the 5 criteria}
**Evidence**: {specific line or section}
**Fix**: {concrete change required}
**Confidence**: {1-10, 10 = certain}
```

---

### Step 1 — Re-Read Relevant Documents (Individual Gates)

Before screening plans, re-read the current governance documents to ensure up-to-date context. Do not rely on cached knowledge from previous steps.

1. Read LANDMINES.md
2. Post: `✅ Read LANDMINES.md: {N} active landmines`
3. Read PRINCIPLES.md (workflow principles section)
4. Post: `✅ Read PRINCIPLES.md: {N} workflow principles`
5. Read ARCHITECTURE.md (relevant AR rules for this plan)
6. Post: `✅ Read ARCHITECTURE.md: {N} relevant AR rules`
7. Read OR_RULES.md (relevant OR rules for this plan)
8. Post: `✅ Read OR_RULES.md: {N} relevant OR rules`

---

### Step 2 — Prepare Round Table (Individual Gates)

1. Screen plans against LANDMINES.md
2. Post: `✅ Screened Landmines: {N} blocking, {N} non-blocking`
3. Assemble brief (Rev 1 only; Rev 2+ brief only if user requests)
4. Post: `✅ Assembled Brief: {N} sections, {lines} lines`
5. Assemble plans, dimensions, risks, settled findings
6. Post: `✅ Assembled Material: {N} plans, {N} dimensions, {N} risks`
7. Draft Round Table prompt with rubric-based criteria
8. Post: `✅ Drafted Prompt: Rev {n}, {N} panelists, rubric-based criteria`

---

### Step 2.5 — Architect Self-Check (Individual Gates)

**Applicable GR Rules**: GR3, GR14, GR15

Before handing material to the user for Round Table, the Architect runs its own draft against the same rubric and finding format the panelists will use, plus the known-pattern checklist from `ARCHITECT_PATTERNS.md`. This is a zero-cost internal pass — no panelist round is spent catching what the Architect can catch itself.

1. Read `ARCHITECT_PATTERNS.md` (Active section only)
2. Post: `✅ Read ARCHITECT_PATTERNS.md: {N} active patterns`
3. Apply the 5-dimension rubric (Clarity & Specificity, Structural Organization, Context Management, Reasoning & Tool Guidance, Examples & Output Control) to the plan draft, same as the Round Table Evaluation Criteria
4. Post: `✅ Self-Check Rubric Pass: {N} self-findings, {N} dimensions clean`
5. Check the draft against every Active entry in `ARCHITECT_PATTERNS.md`
6. Post: `✅ Self-Check Patterns Pass: {N} active patterns checked, {N} matches found`
7. Fix any self-identified CRITICAL/HIGH findings before delivery (same format as Step 4 finding processing: `✅ Self-Fixed Finding SC-{id}: {reasoning} — {fix applied}`)
8. Post: `✅ Self-Check Complete: {N} findings fixed pre-delivery, {N} deferred to Round Table with reasoning`

**Note**: This pass does not replace the real Round Table or reduce GR9's majority-panelist requirement — it reduces the number of findings the real panel needs to surface, which reduces the odds of needing a Rev 2+.

---

### Step 3 — User Executes Round Table (User-Completed)

**This step is completed by the user, not the Architect.**

1. User posts plans, brief (if Rev 1), and prompt to Round Table panelists
2. User collects panelist responses
3. User posts panelist findings back to the Architect

**Architect waits for user to post findings before proceeding to Step 4.**

---

### Step 4 — Process Findings (Individual Gates)

For each panelist finding posted by the user:

1. Post: `✅ Accepted Finding RT-{id}: {reasoning} — {fix applied or documented}`
2. Or: `❌ Rejected Finding RT-{id}: {reasoning}`

**Human verification checklist**:
- [ ] Every finding has a compliance line
- [ ] No finding is unaddressed
- [ ] Accepted findings have fix documentation
- [ ] Rejected findings have reasoning

**STOP conditions**:
- Any finding without a compliance line
- Accepted finding without documented fix
- Rejected finding without reasoning

---

### Step 5 — Score Panelists (Individual Gates)

1. Calculate panelist scores (weighted toward accepted findings)
2. Post: `✅ Calculated Scores: {panelist} {score}/100, {panelist} {score}/100`
3. Post scorecard inline
4. Post: `✅ Posted Scorecard: {N} panelists scored`
5. Check accepted CRITICAL/HIGH findings against existing `ARCHITECT_PATTERNS.md` entries. A matching finding on a second plan — update the entry's recurrence count (add write-task to next plan's Executor Manifest). A novel CRITICAL/HIGH finding with no existing entry — draft new AP entry (add write-task to next plan's Executor Manifest). Executor writes all ARCHITECT_PATTERNS.md updates per plan instruction.
6. Post: `✅ Reviewed Findings Against ARCHITECT_PATTERNS.md: {N} updated, {N} new entries added`

---

### Clean Pass Gate

This gate ensures delivery quality by verifying all critical criteria are met before plans are released to the Executor.

**Threshold Table**:

| Score Threshold | Action |
|----------------|--------|
| 90-100 | Clean pass — proceed to delivery |
| 70-89 | Review findings — Architect may proceed with documented rationale |
| <70 | BLOCK — requires additional Round Table round |

**Verification Checklist**:
- [ ] Panelist majority achieved (GR9)
- [ ] All CRITICAL and HIGH findings addressed
- [ ] MEDIUM findings addressed or documented
- [ ] Clean pass score ≥90 OR documented rationale for 70-89 (score = average of all panelist scores from Step 5)
- [ ] Executor Manifest present in all plans (GR13)
- [ ] No blocking landmines (GR8)

**STOP Conditions**:
- Score <70 without additional Round Table round
- CRITICAL or HIGH findings unaddressed
- Panelist majority not achieved
- Blocking landmines present
- Executor Manifest missing from any plan

---

### Step 6 — Create Round Table Score Document (Final Round Only)

After all Round Table rounds complete for a plan (clean pass achieved), add write-task to next plan's Executor Manifest to create a persistent score document for long-term tracking of panelist performance across plans.

**Do NOT create this document after each round. Only after the final round.**

1. Compile scores from all rounds for this plan
2. Post: `✅ Compiled All Scores: {N} rounds, {N} panelists, scores: {details}`
3. **Add to Executor Manifest**: Score document creation added as write-task in the next plan's Executor Manifest.
4. Post: `✅ Added to Executor Manifest: roundtable-scores-plan-{N}.md`

**Score Document Format** (`roundtable-scores-plan-{N}.md`):

```markdown
# Round Table Scores — Plan {N}

**Date**: {YYYY-MM-DD}
**Plan**: plan-{N}.{i}.md
**Total Rounds**: {N}

## Panelist Scores (All Rounds)

| Panelist | Round 1 | Round 2 | ... | Round N | Average | Total Findings | Accepted | Rejected |
|----------|---------|---------|-----|---------|---------|----------------|----------|----------|
| {name} | {score} | {score} | ... | {score} | {avg} | {N} | {N} | {N} |
| {name} | {score} | {score} | ... | {score} | {avg} | {N} | {N} | {N} |

## Summary

- Total findings across all rounds: {N}
- Critical/High findings: {N}
- Medium/Low findings: {N}
- Clean pass achieved: {Yes / No}

## Notes

{any relevant notes about panelist performance or patterns}
```

**Purpose**: This document enables long-term tracking of which panelists consistently provide the highest-quality findings. Use historical scores to optimize panel composition over time.

---

### Step 7 — Deliver (Individual Gates)

Gated by Clean Pass Gate above.

1. Finalize plans for delivery
2. Post: `✅ Finalized Plans: {N} plans ready`
3. Post delivery confirmation
4. Post: `✅ Delivered: {N} plans ready for copy`

---