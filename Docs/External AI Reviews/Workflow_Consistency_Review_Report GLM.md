# Workflow Folder Consistency Review Report

**Reviewer**: Super Z (external automated reviewer)
**Review Date**: 2026-07-26
**Review Scope**: `Workflow/` directory (25 markdown files across 5 agent folders + Workflow_Reference/)
**Review Focus**: Consistency across all workflow files, reference documents, and template compliance
**Repository Snapshot**: commit `1a2e8af` on `main` branch of `AngusKingCAI/SovereignAI`

---

## Executive Summary

The Workflow folder demonstrates a **well-conceived two-layer architecture** (universal frameworks in `Workflow_Reference/` + agent-specific implementations in `{Agent}/Reference/`) that is largely sound in design intent. However, the recent large refactor (commits `f41cc42 → 1a2e8af`, +2,448 / −1,144 lines) introduced several **path drift, step-numbering, and template-compliance defects** that affect day-to-day execution reliability.

### Issue count by severity

| Severity | Count | Examples |
|---|---|---|
| **High** | 5 | Missing Phase 9 in Planner workflow; Executor workflow fully non-compliant with template; referenced runtime directories (`Scripts/`, `.devin/`, `Plans/`) do not exist |
| **Medium** | 8 | Path drift for Planner Templates (`/Templates/` segment missing in 9 references); duplicate step 37 + missing step 44 in Architect workflow; "Agent Agent" placeholder leftover in `Role_Responsibilities_Framework.md`; Researcher Agent missing from `Quality_Assessment_Framework.md` |
| **Low** | 6 | Inconsistent workflow file naming convention (`{Agent}_Workflow.md` placeholder vs actual names); only 2 of 5 agents covered in `State_Management_Guidelines.md`; Phase 9/10 labeling mismatch between Planner workflow and its Overview reference doc |

### Critical issues requiring immediate attention

1. **Planner workflow skips Phase 9 entirely** — jumps from Phase 8 to Phase 10, contradicting both the template ("Maintain 0-10") and the Planner's own `Workflow_Overview.md`.
2. **Executor workflow is structurally non-compliant** with the template — uses 0–11 numbering, omits the mandatory "Universal Framework References" section, and references zero of the five universal frameworks.
3. **Multiple referenced runtime paths do not exist** in the repository (`Scripts/Planner/Gates/`, `Scripts/Governance/Hooks/`, `.devin/hooks.v1.json`, `.devin/skills/executor/SKILL.md`, `Plans/` (uppercase), `Logs/Planner/`, `Logs/Roundtable/`).
4. **Template path drift** — 9 references across Planner workflow and templates point to `Workflow/Planner/Plan_{Brief,Prompt}_Template.md` instead of `Workflow/Planner/Templates/Plan_{Brief,Prompt}_Template.md`.
5. **Architect workflow step numbering broken** — Phase 5 contains two `step 37` entries; `step 44` is skipped between Phase 5 and Phase 6.

---

## Metric 1: File References Consistency

**Status**: ❌ **FAIL**

### Findings

#### 1.1 Planner Template path drift (HIGH impact)
The Planner workflow correctly references the Plan_Template via the `/Templates/` subdirectory, but **drops the `/Templates/` segment** when referencing Plan_Brief_Template and Plan_Prompt_Template.

| File | Line | Current Reference | Correct Reference |
|---|---|---|---|
| `Workflow/Planner/Planner_Plan_Workflow.md` | 111 | `Workflow/Planner/Plan_Brief_Template.md` | `Workflow/Planner/Templates/Plan_Brief_Template.md` |
| `Workflow/Planner/Planner_Plan_Workflow.md` | 113 | `Workflow/Planner/Plan_Prompt_Template.md` | `Workflow/Planner/Templates/Plan_Prompt_Template.md` |
| `Workflow/Planner/Planner_Plan_Workflow.md` | 167 | `Workflow/Planner/Plan_Brief_Template.md` | `Workflow/Planner/Templates/Plan_Brief_Template.md` |
| `Workflow/Planner/Planner_Plan_Workflow.md` | 169 | `Workflow/Planner/Plan_Prompt_Template.md` | `Workflow/Planner/Templates/Plan_Prompt_Template.md` |
| `Workflow/Planner/Templates/Plan_Brief_Template.md` | 4 | `Workflow/Planner/Plan_Brief_Template.md` | `Workflow/Planner/Templates/Plan_Brief_Template.md` |
| `Workflow/Planner/Templates/Plan_Prompt_Template.md` | 4 | `Workflow/Planner/Plan_Prompt_Template.md` | `Workflow/Planner/Templates/Plan_Prompt_Template.md` |
| `Workflow/Planner/Templates/Plan_Template.md` | 52 | `Workflow/Planner/Plan_Brief_Template.md` | `Workflow/Planner/Templates/Plan_Brief_Template.md` |
| `Workflow/Planner/Templates/Plan_Template.md` | 134 | `Workflow/Planner/Plan_Brief_Template.md` | `Workflow/Planner/Templates/Plan_Brief_Template.md` |
| `Workflow/Planner/Templates/Plan_Template.md` | 136 | `Workflow/Planner/Plan_Prompt_Template.md` | `Workflow/Planner/Templates/Plan_Prompt_Template.md` |
| `Workflow/Planner/Templates/Plan_Template.md` | 149 | `Workflow/Planner/Plan_Prompt_Template.md` | `Workflow/Planner/Templates/Plan_Prompt_Template.md` |

**Internal contradiction**: `Workflow/Planner/Planner_Plan_Workflow.md` line 75 references the Plan_Template using the correct path `Workflow/Planner/Templates/Plan_Template.md`, but lines 111 and 167 (which reference the other two templates in the SAME subfolder) drop the `/Templates/` segment. This indicates an inconsistent copy-paste during the refactor.

#### 1.2 Architect workflow uses non-existent file naming pattern (MEDIUM impact)
`Workflow/Architect/Architect_General_Workflow.md` line 113:
```
- Workflow/{Agent}/{Agent}_Workflow.md (if workflow changes)
```

This placeholder pattern, when resolved, becomes e.g. `Workflow/Architect/Architect_Workflow.md`. **No agent in the repo uses this naming convention**:

| Agent | Actual File Name | Pattern Produces |
|---|---|---|
| Architect | `Architect_General_Workflow.md` | `Architect_Workflow.md` ❌ |
| Planner | `Planner_Plan_Workflow.md` | `Planner_Workflow.md` ❌ |
| Executor | `Executor_Implementation_Cycle.md` | `Executor_Workflow.md` ❌ |
| Researcher | `Research.md` | `Researcher_Workflow.md` ❌ |
| Reviewer | `Review.md` | `Reviewer_Workflow.md` ❌ |

Either the naming convention needs to be standardized to `{Agent}_Workflow.md`, or the placeholder needs to be updated to reflect actual file names.

#### 1.3 Universal framework references — verified accurate (POSITIVE)
All references from agent workflows to `Workflow/Workflow_Reference/*.md` were verified:
- `Architect_General_Workflow.md` lines 151, 156, 161, 166, 171 — all 5 universal frameworks correctly referenced ✅
- `Workflow_Template.md` lines 102, 111, 115, 120, 125, 130 — all 5 correctly referenced ✅
- `Planner/Reference/Workflow_Overview.md` lines 35, 37, 39, 40, 41 — all correctly referenced ✅
- `Planner/Reference/Gate_Enforcement_System.md` lines 42, 44 — correctly referenced ✅
- `Planner/Reference/Convergence_Loop_Specifications.md` line 7 — correctly referenced ✅

#### 1.4 Agent-specific reference paths — verified accurate (POSITIVE)
All Architect references to `Workflow/Architect/Reference/*.md` (lines 14, 43, 52, 60, 64, 72, 73, 74, 88, 102, 117, 131) point to files that actually exist:
- `Execution_Mode_Patterns.md` ✅
- `Implementation_Mode_Patterns.md` ✅
- `Option_Evaluation_Framework.md` ✅

All Planner references to `Workflow/Planner/Reference/*.md` point to files that exist:
- `Gate_Enforcement_System.md` ✅
- `Convergence_Loop_Specifications.md` ✅
- `Delivery_Authorization_Specifications.md` ✅
- `Role_Responsibilities.md` ✅
- `Workflow_Overview.md` ✅

### Impact
- **HIGH** for issue 1.1: panelists following the workflow would fail to locate the Brief/Prompt templates, breaking the Round Table review process.
- **MEDIUM** for issue 1.2: architect attempting to update "the workflow file" would not find it under the suggested name.

### Recommendations
1. **Immediate (issue 1.1)**: Replace all 9 occurrences of `Workflow/Planner/Plan_{Brief,Prompt}_Template.md` with `Workflow/Planner/Templates/Plan_{Brief,Prompt}_Template.md`. A simple sed one-liner can do this:
   ```bash
   sed -i 's|Workflow/Planner/Plan_Brief_Template\.md|Workflow/Planner/Templates/Plan_Brief_Template.md|g; s|Workflow/Planner/Plan_Prompt_Template\.md|Workflow/Planner/Templates/Plan_Prompt_Template.md|g' \
     Workflow/Planner/Planner_Plan_Workflow.md \
     Workflow/Planner/Templates/Plan_Brief_Template.md \
     Workflow/Planner/Templates/Plan_Prompt_Template.md \
     Workflow/Planner/Templates/Plan_Template.md
   ```
2. **Short-term (issue 1.2)**: Update line 113 of `Architect_General_Workflow.md` to either (a) list each agent's actual workflow file by name, or (b) introduce a documented naming convention and rename all workflow files to match.

---

## Metric 2: Best Practices Compliance

**Status**: ⚠️ **WARNING**

### Findings

#### 2.1 Two-layer structure — implemented correctly (POSITIVE)
The folder structure cleanly separates universal from agent-specific content:

```
Workflow/
├── Workflow_Template.md            (universal template)
├── Workflow_Reference/              (universal frameworks)
│   ├── Convergence_Loop_Patterns.md
│   ├── Execution_Strategy_Guidelines.md
│   ├── Gate_Enforcement_Patterns.md
│   ├── Quality_Assessment_Framework.md
│   ├── Quality_Metrics_Framework.md
│   ├── Role_Responsibilities_Framework.md
│   ├── State_Management_Guidelines.md
│   └── Template_Usage_Guidelines.md
├── Architect/
│   ├── Architect_General_Workflow.md
│   └── Reference/                  (Architect-specific specs)
├── Planner/
│   ├── Planner_Plan_Workflow.md
│   ├── Reference/                  (Planner-specific specs)
│   └── Templates/                  (Planner-specific templates)
├── Executor/
│   └── Executor_Implementation_Cycle.md
├── Researcher/
│   └── Research.md
└── Reviewer/
    └── Review.md
```

#### 2.2 Universal framework naming convention — mostly consistent (POSITIVE with caveat)
Convention required: `{Concept}_Framework.md`, `{Concept}_Patterns.md`, `{Concept}_Guidelines.md`.

| File | Suffix | Compliant? |
|---|---|---|
| `Convergence_Loop_Patterns.md` | `_Patterns.md` | ✅ |
| `Execution_Strategy_Guidelines.md` | `_Guidelines.md` | ✅ |
| `Gate_Enforcement_Patterns.md` | `_Patterns.md` | ✅ |
| `Quality_Assessment_Framework.md` | `_Framework.md` | ✅ |
| `Quality_Metrics_Framework.md` | `_Framework.md` | ✅ |
| `Role_Responsibilities_Framework.md` | `_Framework.md` | ✅ |
| `State_Management_Guidelines.md` | `_Guidelines.md` | ✅ |
| `Template_Usage_Guidelines.md` | `_Guidelines.md` | ✅ |

**Caveat**: Convention is followed, but is overly rigid. Quality_Assessment and Quality_Metrics are conceptually siblings yet use the same `_Framework` suffix — readers may have trouble knowing which one to consult for a given question. Consider renaming `Quality_Metrics_Framework.md` to `Quality_Metrics_Guidelines.md` to signal "this is operational guidance, not a structural framework."

#### 2.3 Agent-specific naming convention — partially violated (MEDIUM impact)
Convention required: `{Agent}_{Concept}_Specifications.md`.

| File | Compliant? | Issue |
|---|---|---|
| `Architect/Reference/Execution_Mode_Patterns.md` | ❌ | Uses `_Patterns` suffix (universal-style) instead of `_Specifications` |
| `Architect/Reference/Implementation_Mode_Patterns.md` | ❌ | Same — `_Patterns` suffix |
| `Architect/Reference/Option_Evaluation_Framework.md` | ❌ | Uses `_Framework` suffix (universal-style) |
| `Planner/Reference/Convergence_Loop_Specifications.md` | ✅ | Correctly uses `_Specifications` |
| `Planner/Reference/Delivery_Authorization_Specifications.md` | ✅ | Correctly uses `_Specifications` |
| `Planner/Reference/Gate_Enforcement_System.md` | ⚠️ | Uses `_System` suffix — not in the convention |
| `Planner/Reference/Role_Responsibilities.md` | ⚠️ | Lacks agent prefix and proper suffix |
| `Planner/Reference/Workflow_Overview.md` | ⚠️ | Lacks agent prefix and proper suffix |

**The Architect/Reference/ folder uses universal-style suffixes (`_Patterns`, `_Framework`) for what are actually agent-specific documents.** This blurs the boundary between universal and agent-specific content, making it harder to tell at a glance whether a file is universal or Architect-specific.

**The Planner/Reference/ folder has mixed compliance**: 2 files follow the convention, 3 do not.

#### 2.4 Universal content in agent-specific folders — NOT detected (POSITIVE)
No universal patterns were duplicated into agent-specific Reference/ folders. Universal patterns stay in `Workflow_Reference/`. ✅

#### 2.5 Agent-specific content in universal folder — NOT detected (POSITIVE)
No agent-specific implementations leaked into `Workflow_Reference/`. The "Agent-Specific Customization" sections inside universal frameworks provide guidance only (not implementations). ✅

### Impact
- **MEDIUM** for issue 2.3: file naming inconsistency makes it harder to maintain the folder structure programmatically and to train new contributors on conventions.

### Recommendations
1. **Short-term (issue 2.3)**: Rename the three Architect/Reference/ files:
   - `Execution_Mode_Patterns.md` → `Architect_Execution_Mode_Specifications.md`
   - `Implementation_Mode_Patterns.md` → `Architect_Implementation_Mode_Specifications.md`
   - `Option_Evaluation_Framework.md` → `Architect_Option_Evaluation_Specifications.md`
   
   Update all references in `Architect_General_Workflow.md` (lines 14, 43, 52, 60, 64, 72, 73, 74, 88, 102, 117, 131) accordingly.
2. **Medium-term (issue 2.2)**: Consider renaming `Quality_Metrics_Framework.md` to `Quality_Metrics_Guidelines.md` to differentiate it from `Quality_Assessment_Framework.md`.

---

## Metric 3: Universal vs Agent-Specific Separation

**Status**: ✅ **PASS** (with minor warnings)

### Findings

#### 3.1 Universal frameworks contain only universal patterns (POSITIVE)
Spot-checked all 8 files in `Workflow_Reference/`. Each one:
- Defines patterns applicable to all agents ✅
- Includes a "Agent-Specific Customization" section that provides guidance (not implementations) ✅
- Does NOT contain agent-specific gate definitions, convergence criteria, or phase definitions ✅

#### 3.2 Agent-specific Reference/ folders contain only agent-specific content (POSITIVE)
Spot-checked all 8 files in `{Agent}/Reference/`. Each one:
- Contains only agent-specific implementations ✅
- References (does not duplicate) the universal framework ✅
- Provides concrete agent-specific parameters (e.g., Planner's "Maximum 5 internal iterations") ✅

#### 3.3 Cross-reference pattern — exemplary in some files (POSITIVE)
`Planner/Reference/Convergence_Loop_Specifications.md` lines 5-10 demonstrate the ideal cross-reference pattern:
```markdown
## Universal Pattern Reference

See Workflow/Workflow_Reference/Convergence_Loop_Patterns.md for universal convergence loop patterns including:
- Universal convergence loop pattern and logic
- Universal convergence criteria definitions
- Universal loop caps and escalation procedures
```

Then it provides Planner-specific implementation below. **This is the gold-standard pattern** and should be replicated across all agent-specific Reference/ files.

Same gold-standard pattern observed in:
- `Planner/Reference/Gate_Enforcement_System.md` lines 5-10 ✅

#### 3.4 Cross-reference pattern — missing in some files (MEDIUM impact)
The following agent-specific Reference/ files do NOT include the "Universal Pattern Reference" section at the top:

| File | Issue |
|---|---|
| `Architect/Reference/Execution_Mode_Patterns.md` | No reference to `Execution_Strategy_Guidelines.md` (the universal counterpart) |
| `Architect/Reference/Implementation_Mode_Patterns.md` | No reference to `Execution_Strategy_Guidelines.md` |
| `Architect/Reference/Option_Evaluation_Framework.md` | No reference to `Quality_Assessment_Framework.md` |
| `Planner/Reference/Delivery_Authorization_Specifications.md` | Has a "Gate System Reference" section but it points only to other Planner files, not to the universal `Gate_Enforcement_Patterns.md` |
| `Planner/Reference/Role_Responsibilities.md` | No reference to `Role_Responsibilities_Framework.md` |
| `Planner/Reference/Workflow_Overview.md` | Does reference all universal frameworks (lines 35-41) — ✅ this one is good |

#### 3.5 No duplicate content between universal and agent-specific files (POSITIVE)
Universal frameworks define patterns; agent-specific files instantiate those patterns with concrete parameters. No verbatim duplication detected. ✅

### Impact
- **MEDIUM** for issue 3.4: Agent-specific Reference/ files that don't link back to their universal counterpart create a risk of contributors modifying the agent-specific file without awareness of the universal pattern it should follow.

### Recommendations
1. **Short-term (issue 3.4)**: Add a "Universal Pattern Reference" section at the top of each agent-specific Reference/ file (template below) — apply to the 5 files listed above.
   ```markdown
   ## Universal Pattern Reference
   
   See Workflow/Workflow_Reference/{Universal_Document}.md for the universal {concept} pattern that this file implements.
   ```

---

## Metric 4: Path Accuracy

**Status**: ❌ **FAIL**

### Findings

#### 4.1 Templates path — partially broken (HIGH impact)
Already documented under Metric 1.1 — see above. The `/Templates/` subdirectory is inconsistently included when Planner templates are referenced.

#### 4.2 Runtime directories referenced but not present (HIGH impact)
The following paths are referenced in workflow files but **do not exist in the repository**:

| Referenced Path | Referenced In | Status |
|---|---|---|
| `Scripts/` (top-level directory) | `Executor_Implementation_Cycle.md` lines 231-234, `Planner_Plan_Workflow.md` lines 98, 153, 199 | ❌ Does not exist |
| `Scripts/Planner/Gates/run-all-planner-gates.sh` | `Planner_Plan_Workflow.md` lines 98, 153, 199; `Planner/Reference/Gate_Enforcement_System.md` lines 27, 32, 37 | ❌ Does not exist |
| `Scripts/Governance/Hooks/` | `Executor_Implementation_Cycle.md` line 231 | ❌ Does not exist |
| `Scripts/Governance/Config/phase_permissions.json` | `Executor_Implementation_Cycle.md` line 92, 274 | ❌ Does not exist |
| `Scripts/Governance/simple_logger.py` | `Executor_Implementation_Cycle.md` line 234 | ❌ Does not exist |
| `.devin/hooks.v1.json` | `Executor_Implementation_Cycle.md` lines 54, 81 | ❌ Does not exist |
| `.devin/skills/executor/SKILL.md` | `Executor_Implementation_Cycle.md` line 226 | ❌ Does not exist |
| `Plans/` (uppercase P) | `Planner_Plan_Workflow.md` lines 19, 93, 98, 153, 199, 213 | ❌ Only `plans/` (lowercase) exists |
| `Logs/Planner/` | `Planner_Plan_Workflow.md` lines 156, 213, 215; `Planner/Reference/Gate_Enforcement_System.md` line 47 | ❌ Only `Logs/Executor/` exists |
| `Logs/Roundtable/Devin/` | `Planner_Plan_Workflow.md` line 116, 124; `Planner/Templates/Plan_Brief_Template.md` line 5 | ❌ Does not exist |
| `Logs/Roundtable/External/` | `Planner_Plan_Workflow.md` line 172, 181; `Planner/Templates/Plan_Brief_Template.md` line 5 | ❌ Does not exist |
| `Logs/{AgentType}/Sessions/` | `Executor_Implementation_Cycle.md` lines 56, 191, 196, 233, 256 | ❌ Does not exist |

**Mitigation context**: Some of these may be "create-at-runtime" directories (e.g., `Logs/Planner/` could be created on first planner run). However:
- `Scripts/Planner/Gates/run-all-planner-gates.sh` is a **script** that the workflow expects to execute — its absence means the gate system cannot function as documented.
- `.devin/hooks.v1.json` is a **configuration file** that the Executor workflow claims is "automatically active" — its absence means the entire hook-based governance model described in `Executor_Implementation_Cycle.md` is non-functional.

#### 4.3 Governance file paths — verified accurate (POSITIVE)
All references to `Rules/{Agent}/{Agent}_Rules.md` were verified. All 5 rule files exist:
- `Rules/Architect/Architect_Rules.md` ✅
- `Rules/Executor/Executor_Rules.md` ✅
- `Rules/Planner/Planner_Rules.md` ✅
- `Rules/Researcher/Researcher_Rules.md` ✅
- `Rules/Reviewer/Reviewer_Rules.md` ✅

`INDEX.md` and `AGENTS.md` also exist as referenced. ✅

#### 4.4 Reference/ subdirectory paths — verified accurate (POSITIVE)
All references using `Workflow/{Agent}/Reference/{Document}.md` pattern point to files that exist. ✅

### Impact
- **HIGH** for issue 4.2: the Planner gate-validation steps (Phase 3, 5, 7) literally cannot execute because the script they invoke does not exist. The Executor workflow's entire hook-based governance claim is unverifiable because `.devin/hooks.v1.json` does not exist.
- **MEDIUM** for issue 4.1: documented in Metric 1.

### Recommendations
1. **Immediate (issue 4.2)**: One of:
   - (a) Create the missing scripts and `.devin/` configuration files (significant effort);
   - (b) Add a "Prerequisites" section to each affected workflow listing required runtime assets and noting that the workflow cannot execute until they are provisioned;
   - (c) Mark the affected steps as "TODO: implement" with clear placeholders until scripts are written.
2. **Immediate (issue 4.1)**: Apply the sed fix from Metric 1 Recommendation 1.

---

## Metric 5: No Redundancy

**Status**: ✅ **PASS**

### Findings

#### 5.1 Universal vs agent-specific — no duplication (POSITIVE)
The two-layer design works as intended:
- Universal frameworks (e.g., `Quality_Assessment_Framework.md`) define **dimensions and scoring rubrics** that apply to all agents.
- Agent-specific files (e.g., `Planner/Reference/Gate_Enforcement_System.md`) define **which gates Planner uses**, not how scoring works.

No verbatim duplication was detected between universal and agent-specific files.

#### 5.2 Agent-specific files reference (not duplicate) universal patterns (POSITIVE)
Spot-checked `Planner/Reference/Convergence_Loop_Specifications.md`, `Planner/Reference/Gate_Enforcement_System.md`, `Planner/Reference/Workflow_Overview.md`. Each one:
- Provides a "Universal Pattern Reference" section pointing to the universal counterpart ✅
- Then provides only Planner-specific implementation details ✅

#### 5.3 Each document has a unique, well-defined purpose (POSITIVE)
No two files were found to serve the same purpose. Each file addresses a distinct concern:
- Universal: pattern / framework / guidelines / metrics / role definitions
- Agent-specific: specifications / system implementation / overview / authorization / role instantiation

#### 5.4 Quality metrics in Executor workflow — partial duplication risk (LOW impact)
`Executor_Implementation_Cycle.md` lines 236-253 contain a "Quality Metrics" section that lists Quality (10 points), Token Cost (10 points), and Efficiency (10 points) — these are verbatim copies of what's in `Workflow/Workflow_Reference/Quality_Metrics_Framework.md` lines 7-89.

This is partial duplication. The Executor workflow should reference the universal framework rather than re-stating the metrics inline.

### Impact
- **LOW** for issue 5.4: maintenance burden if metrics evolve — the Executor workflow's copy may go stale.

### Recommendations
1. **Short-term (issue 5.4)**: Replace the inline "Quality Metrics" section in `Executor_Implementation_Cycle.md` (lines 236-253) with a reference:
   ```markdown
   ## Quality Metrics
   
   See `Workflow/Workflow_Reference/Quality_Metrics_Framework.md` for the universal quality metrics framework (Quality / Token Cost / Efficiency dimensions, 30 points total). Executor-specific metric weighting:
   - **Implementation Fidelity**: weight 5 (Executor primary)
   - **Code Quality**: weight 4
   - **Test Success Rate**: weight 3
   - **Deployment Success**: weight 2
   - **Bug Rate**: weight 1 (inverse)
   ```

---

## Metric 6: Template Compliance

**Status**: ❌ **FAIL**

### Findings

#### 6.1 Architect workflow — compliant (POSITIVE)
`Workflow/Architect/Architect_General_Workflow.md` follows the template:
- ✅ Has Phase 0 (Read Architect Rules) — line 22
- ✅ Has Phase 3 (Research Best Practices with web search) — line 47
- ✅ Has Phase 10 (Return to Phase 0) — line 141
- ✅ Has VALIDATION entries in multiple phases
- ✅ Has STATUS TRACKING entries in each phase
- ✅ Has PRINT commands throughout
- ✅ Has Universal Framework References section (lines 148-173)
- ✅ References all 5 universal frameworks

**Numbering issues** (MEDIUM impact):
- Phase 5 contains **two step 37 entries** (lines 71-72)
- **Step 44 is skipped** — Phase 5 ends at step 43 (line 78), Phase 6 begins at step 45 (line 81)

The header claims "91 steps" but the actual unique step numbers are 1-43, 45-91 (90 unique numbers due to missing step 44) plus the duplicate step 37 (one extra entry) = 91 total entries. The count is technically right but the numbering is broken.

#### 6.2 Planner workflow — partially non-compliant (HIGH impact)
`Workflow/Planner/Planner_Plan_Workflow.md`:

- ✅ Has Phase 0 (Read Planner Rules) — line 43
- ✅ Has Phase 3 (Plan Creation + Early Gate Validation) — line 82
- ✅ Has Phase 10 (Return to Phase 0) — line 223
- ✅ Has VALIDATION entries in most phases
- ✅ Has STATUS TRACKING entries in each phase
- ✅ Has PRINT commands throughout
- ❌ **Phase 9 is completely missing** — workflow jumps from Phase 8 (line 209) to Phase 10 (line 223)
- ⚠️ Has a "Quality Hierarchy" section (line 231) instead of "Universal Framework References"
- ⚠️ Does not explicitly reference the 5 universal frameworks (Quality Assessment, Role Responsibilities, Quality Metrics, State Management, Execution Strategy) — they are referenced indirectly via `Planner/Reference/Workflow_Overview.md` but not in the workflow itself
- ❌ Phase 2 (line 71) is "Read Governance" but only reads Plan_Template — does NOT include a web search step, violating the template requirement that Phase 3 must perform a web search. (Phase 3 here is "Plan Creation", not "Research" — the template intent for Phase 3 is research.)

**Critical**: the Planner workflow uses Phase 3 for "Plan Creation + Early Gate Validation" instead of "Research and Best Practices" as the template requires. This means there is **no Phase 3 web search** in the Planner workflow, which is a template violation.

**Internal contradiction**: `Planner/Reference/Workflow_Overview.md` line 28 lists "Phase 9: Return to Phase 0" but the actual workflow has "Phase 10: Return to Phase 0". The Overview document and the workflow disagree on the phase number for the same step.

#### 6.3 Executor workflow — fully non-compliant (HIGH impact)
`Workflow/Executor/Executor_Implementation_Cycle.md`:

- ❌ Does NOT use Phase 0–10 numbering — uses "Step 0" through "Step 11" (12 phases)
- ❌ Phase 0 is "Environment Initialization (Automatic)" — does not read Executor rules
- ❌ Has no "Research and Best Practices" phase — Phase 3 is "Implementation Setup" not research
- ❌ Phase 10 is "Session Finalization" instead of "Return to Phase 0"
- ❌ Phase 11 is "Cycle Back to Step 1" — extra phase beyond the template
- ❌ **No Universal Framework References section**
- ❌ Does not reference ANY of the 5 universal frameworks
- ❌ Has no VALIDATION entries with the standard format
- ❌ Has no STATUS TRACKING entries with the standard format
- ❌ Uses different PRINT format ("**Automatic Hook**: SessionStart hook..." instead of "**PRINT**: ...")
- ❌ Header is non-standard (uses `**File**:` instead of `**ID**:` etc.)

The Executor workflow is essentially written in a **different style guide** from the other workflows. It reads more like a Devin-CLI hook documentation page than a workflow following the Workflow_Template.

#### 6.4 Researcher and Reviewer workflows — stubs (LOW impact)
Both `Researcher/Research.md` and `Reviewer/Review.md` are explicitly marked "Status: Stub" with no workflow steps. Template compliance cannot be assessed until they are implemented. The stubs note: "This workflow will be gated with attestation per AGENTS.md requirement when fully implemented."

#### 6.5 Step numbering sequential consistency (MEDIUM impact)
- Architect workflow: step 37 duplicated; step 44 skipped (see 6.1)
- Planner workflow: step numbering is sequential (1-64) ✅
- Executor workflow: uses Step 0-11 numbering, not Phase 0-10 ✗ (see 6.3)

### Impact
- **HIGH** for issue 6.2: the missing Phase 9 and missing "Universal Framework References" section in the Planner workflow means it does not satisfy the template's "Maintain 0-10" requirement. The Phase 3 misuse (plan creation instead of research) means the Planner skips the mandatory web-search research phase.
- **HIGH** for issue 6.3: the Executor workflow is structurally incompatible with the template. It cannot be processed by any tooling that expects the standard Phase 0-10 layout.
- **MEDIUM** for issue 6.1: broken step numbering in the Architect workflow could confuse automated validators that expect sequential numbering.

### Recommendations
1. **Immediate (issue 6.2)**: 
   - Insert a Phase 9 (e.g., "Phase 9. Continuous Improvement" or any Planner-relevant phase) between Phase 8 and Phase 10 of `Planner_Plan_Workflow.md`.
   - Update `Planner/Reference/Workflow_Overview.md` line 28 to match (either "Phase 9: Return to Phase 0" or "Phase 10: Return to Phase 0" — pick one and use consistently).
   - Rename the existing "Quality Hierarchy" section to "Universal Framework References" and add explicit references to all 5 universal frameworks.
   - Move the "Research and Best Practices" content into Phase 3 (currently the web-search requirement is absent).
2. **Immediate (issue 6.1)**: 
   - Renumber the duplicate `step 37` to `step 38` in `Architect_General_Workflow.md` line 72, and bump all subsequent step numbers in Phase 5 accordingly (38→39, 39→40, 40→41, 41→42, 42→43, 43→44).
   - Verify that the resulting step numbering aligns with Phase 6 starting at step 45.
3. **Medium-term (issue 6.3)**: Refactor `Executor_Implementation_Cycle.md` to follow the standard Phase 0-10 structure. Phase 0 = Read Executor Rules; Phase 1 = Select Execution Strategy; Phase 3 = Research and Best Practices (with web search); Phase 10 = Return to Phase 0. Add a "Universal Framework References" section at the end. Add VALIDATION and STATUS TRACKING entries with the standard format.
4. **Long-term (issue 6.4)**: Implement the Researcher and Reviewer workflows following the template, with explicit Phase 0-10 structure and Universal Framework References.

---

## Metric 7: Cross-References Accuracy

**Status**: ⚠️ **WARNING**

### Findings

#### 7.1 Cross-references use proper relative paths (POSITIVE)
All cross-references use the `Workflow/...` relative path format consistently. No absolute paths or URLs were detected in references between workflow files. ✅

#### 7.2 Cross-referenced files exist (mostly POSITIVE)
All cross-references to universal frameworks (`Workflow/Workflow_Reference/*.md`) point to files that exist. ✅
All cross-references to agent-specific Reference/ files point to files that exist. ✅
All cross-references to Rules files point to files that exist. ✅

Cross-references that fail:
- 9 references to `Workflow/Planner/Plan_{Brief,Prompt}_Template.md` (should be in `/Templates/` subdirectory) — see Metric 1.1 ❌
- Multiple references to runtime paths that don't exist (`Scripts/`, `.devin/`, `Plans/`, `Logs/Planner/`, `Logs/Roundtable/`) — see Metric 4.2 ❌

#### 7.3 Cross-reference patterns — inconsistent (MEDIUM impact)
Three different cross-reference styles observed:

**Style A** (gold standard — used by `Planner/Reference/Convergence_Loop_Specifications.md` and `Planner/Reference/Gate_Enforcement_System.md`):
```markdown
## Universal Pattern Reference

See Workflow/Workflow_Reference/{Document}.md for universal {concept} patterns including:
- {bullet 1}
- {bullet 2}
```
Then provides agent-specific implementation below.

**Style B** (used by `Architect_General_Workflow.md` "Universal Framework References" section):
```markdown
### Quality Assessment
- **Universal Framework**: Workflow/Workflow_Reference/Quality_Assessment_Framework.md
- **Architect Customization**: Architect-specific infrastructure design quality criteria
- **Focus**: Infrastructure design quality assessment with architectural-specific criteria
```

**Style C** (inline combined reference — used in `Planner_Plan_Workflow.md` line 100):
```markdown
- 23. **VALIDATION**: Validate that plan creation completed successfully and early gates passed (see Workflow/Workflow_Reference/Gate_Enforcement_Patterns.md for universal pattern, see Workflow/Planner/Reference/Gate_Enforcement_System.md for Planner-specific gates)
```

All three styles are valid, but having three styles in the same repository reduces skimmability. **Style B** is what the template (`Workflow_Template.md` lines 117-132) recommends. **Style A** is the most thorough. **Style C** is appropriate for inline references but should be reserved for cases where the workflow step itself needs to point to both universal and specific context.

#### 7.4 Missing cross-references to universal frameworks (MEDIUM impact)
- `Architect/Reference/Execution_Mode_Patterns.md` does not reference `Workflow_Reference/Execution_Strategy_Guidelines.md` (its universal counterpart)
- `Architect/Reference/Implementation_Mode_Patterns.md` does not reference `Workflow_Reference/Execution_Strategy_Guidelines.md`
- `Architect/Reference/Option_Evaluation_Framework.md` does not reference `Workflow_Reference/Quality_Assessment_Framework.md`
- `Planner/Reference/Role_Responsibilities.md` does not reference `Workflow_Reference/Role_Responsibilities_Framework.md`
- `Planner/Reference/Delivery_Authorization_Specifications.md` references `Workflow/Planner/Reference/Gate_Enforcement_System.md` but not the universal `Workflow/Workflow_Reference/Gate_Enforcement_Patterns.md`
- `Executor/Executor_Implementation_Cycle.md` does not reference ANY universal framework

#### 7.5 No circular references detected (POSITIVE)
Spot-checked all Reference/ files — no circular reference chains found. ✅

### Impact
- **MEDIUM** for issues 7.3 and 7.4: the inconsistency makes the documentation harder to navigate and increases the risk of contributors modifying a universal pattern without checking agent-specific implementations (or vice versa).

### Recommendations
1. **Short-term (issue 7.4)**: Add a "Universal Pattern Reference" section at the top of each agent-specific Reference/ file that lacks one (see Metric 3.4 for the file list).
2. **Medium-term (issue 7.3)**: Pick one cross-reference style as the canonical pattern and document it in `Template_Usage_Guidelines.md`. The recommended canonical style is **Style A** for the top of agent-specific Reference/ files, and **Style B** (template-end Universal Framework References section) for the bottom of agent workflows. **Style C** remains appropriate for inline references in workflow steps.

---

## Critical Issues Summary

Listed in priority order for resolution:

| # | Issue | Severity | Effort | Dependencies |
|---|---|---|---|---|
| 1 | **Planner workflow skips Phase 9** (Metric 6.2) | High | Low (insert one section) | None |
| 2 | **Executor workflow non-compliant with template** (Metric 6.3) | High | High (full refactor) | None |
| 3 | **9 broken Planner template paths** missing `/Templates/` (Metric 1.1, 4.1) | High | Trivial (sed one-liner) | None |
| 4 | **Referenced runtime paths don't exist** (`Scripts/`, `.devin/`, `Plans/`, `Logs/Planner/`, `Logs/Roundtable/`) (Metric 4.2) | High | High (create scripts/configs) or Medium (add Prerequisites section) | None |
| 5 | **Architect workflow duplicate step 37 + missing step 44** (Metric 6.1) | Medium | Low (renumber) | None |
| 6 | **"Agent Agent" placeholder in `Role_Responsibilities_Framework.md` line 7** | Medium | Trivial | None |
| 7 | **Researcher Agent missing from `Quality_Assessment_Framework.md`** (inconsistent with other universal frameworks) | Medium | Low (add one section) | None |
| 8 | **Planner Overview doc says Phase 9 is "Return to Phase 0" but workflow says Phase 10** (Metric 6.2) | Medium | Low (fix one line) | Resolved alongside #1 |
| 9 | **Architect agent-specific Reference/ files use universal-style naming** (`_Patterns`/`_Framework` instead of `_Specifications`) (Metric 2.3) | Medium | Medium (rename + update refs) | None |
| 10 | **Missing Universal Pattern Reference sections** in 5 agent-specific Reference/ files (Metric 3.4, 7.4) | Medium | Low (add 5 short sections) | None |
| 11 | **Planner workflow has no "Universal Framework References" section** (Metric 6.2) | Medium | Low (add a section) | None |
| 12 | **State_Management_Guidelines.md only covers 2 of 5 agents** (Planner, Architect) | Low | Medium (add 3 sections) | None |
| 13 | **Executor workflow has duplicated Quality Metrics inline** instead of referencing universal framework (Metric 5.4) | Low | Low (replace with reference) | None |
| 14 | **Inconsistent cross-reference styles** (Metric 7.3) | Low | Medium (refactor + document) | None |

**Suggested resolution order**: 3 → 6 → 1 → 8 → 5 → 11 → 10 → 7 → 12 → 9 → 4 → 2 → 13 → 14

Issues 3, 6, 1, 8 are trivial fixes that immediately improve consistency. Issue 2 (Executor refactor) is the largest effort and should be planned as a dedicated work item.

---

## Positive Findings

### Exemplary areas to preserve

1. **Two-layer documentation architecture** (universal `Workflow_Reference/` + agent-specific `{Agent}/Reference/`) is sound and consistently applied at the folder level. The refactor that introduced this layering is a significant improvement over the prior monolithic `Quality_Rubric.md` approach.

2. **`Planner/Reference/Convergence_Loop_Specifications.md` and `Planner/Reference/Gate_Enforcement_System.md`** demonstrate the **gold-standard cross-reference pattern** (Style A in Metric 7.3). Every agent-specific Reference/ file should adopt this pattern.

3. **`Workflow/Workflow_Reference/Quality_Assessment_Framework.md`** is exceptionally well-structured: clear dimensions, weighted scoring formula, hard-fail conditions, agent-specific customization section, and usage guidelines. This file should be the model for other universal frameworks.

4. **Universal framework file naming** follows the `{Concept}_{Type}.md` convention consistently (8/8 files compliant).

5. **Architect workflow's "Universal Framework References" section** (lines 148-173) is the gold-standard for the bottom-of-workflow references section. Lists all 5 universal frameworks with `Universal Framework` / `Architect Customization` / `Focus` triplets. Other agent workflows should adopt this pattern.

6. **`Planner/Reference/Workflow_Overview.md`** provides an exemplary "Template References" section (lines 31-41) listing every referenced file with a brief description. This pattern should be replicated for other agents.

7. **All 5 Rules files exist and are referenced correctly** from every workflow that needs them.

8. **No content duplication** between universal and agent-specific files (Metric 5). The two-layer design successfully prevents redundancy.

9. **No circular references** detected (Metric 7.5).

10. **`Workflow_Template.md`** provides a clear, parameterized template that is easy to follow for new agents. The Phase 0 / Phase 3 / Phase 10 anchor requirements are well-defined.

---

## Recommendations

### Short-term actions (immediate fixes, < 1 day each)

1. **Fix the 9 broken Planner template paths** — apply the sed command from Metric 1.1 Recommendation 1.
2. **Fix "Agent Agent" placeholder** in `Role_Responsibilities_Framework.md` line 7 — replace with `{Agent} Agent (Universal Responsibilities)` or just `Agent (Universal Responsibilities)`.
3. **Insert Phase 9 in Planner workflow** — add a "Phase 9. Continuous Improvement" or similar phase between Phase 8 and Phase 10. Update `Planner/Reference/Workflow_Overview.md` to match.
4. **Fix Architect workflow step numbering** — renumber the duplicate `step 37` and shift subsequent steps to close the `step 44` gap.
5. **Add "Universal Framework References" section** to the bottom of `Planner_Plan_Workflow.md`, mirroring the Architect workflow's section.
6. **Add Researcher Agent section** to `Quality_Assessment_Framework.md` (Planner, Architect, Executor, Reviewer are present; Researcher is missing).
7. **Add "Universal Pattern Reference" section** to the top of the 5 agent-specific Reference/ files identified in Metric 3.4.
8. **Replace inline Quality Metrics in `Executor_Implementation_Cycle.md`** (lines 236-253) with a reference to `Workflow/Workflow_Reference/Quality_Metrics_Framework.md`.

### Medium-term improvements (structural changes, 1-5 days each)

9. **Refactor `Executor_Implementation_Cycle.md`** to comply with the Phase 0-10 template. This is the largest single work item. Recommended approach: keep the hook-system content as a supplementary "Hook-Based Governance" appendix, but restructure the main workflow body into Phase 0-10 with standard VALIDATION / STATUS TRACKING / PRINT entries.

10. **Rename Architect agent-specific Reference/ files** to use the `_Specifications` suffix per the convention (Metric 2.3). Update all references in `Architect_General_Workflow.md` accordingly.

11. **Add Executor, Reviewer, and Researcher agent-specific state schemas** to `State_Management_Guidelines.md` (currently only Planner and Architect are covered).

12. **Document the canonical cross-reference style** in `Template_Usage_Guidelines.md` — pick Style A for the top of agent-specific Reference/ files and Style B for the bottom of agent workflows. Update `Template_Usage_Guidelines.md` to include a "Cross-Reference Style Guide" section with examples.

13. **Address the missing runtime paths** (Metric 4.2). Either:
    - Create the missing `Scripts/Planner/Gates/run-all-planner-gates.sh` script and the `.devin/hooks.v1.json` configuration; or
    - Add a "Prerequisites" section to each affected workflow listing required runtime assets and noting that the workflow cannot execute until they are provisioned.

### Long-term enhancements (process improvements)

14. **Implement Researcher and Reviewer workflows** following the standard Phase 0-10 template, including Universal Framework References sections.

15. **Standardize workflow file naming** — either rename all workflow files to `{Agent}_Workflow.md` (matching the placeholder pattern in `Architect_General_Workflow.md` line 113) or update that placeholder to reflect the actual naming convention.

16. **Add a CI check** (e.g., a script run on every commit) that validates:
    - All workflow files have Phase 0, Phase 3, Phase 10
    - All workflow files have a Universal Framework References section
    - All cross-references point to existing files
    - All step numbers are sequential within each phase
    
    This would prevent regressions on the issues identified in this review.

17. **Establish a quarterly Workflow Folder consistency review** using this prompt as the basis. Track issue counts over time to verify that the recommendations are being implemented and that new issues are not being introduced.

---

## Appendix: Review Methodology

This review was conducted by:
1. Listing all 25 markdown files in the `Workflow/` directory tree.
2. Reading each file completely (no skimming).
3. Extracting all `Workflow/...` path references via grep.
4. Verifying each referenced path against the actual repository structure.
5. Cross-checking each workflow against the template requirements in `Workflow/Workflow_Template.md` and `Workflow/Workflow_Reference/Template_Usage_Guidelines.md`.
6. Checking each universal framework for completeness (all 5 agents represented in agent-specific customization sections).
7. Checking each agent-specific Reference/ file for the presence of a Universal Pattern Reference section.
8. Checking workflow step numbering for sequential consistency.
9. Verifying referenced runtime paths (`Scripts/`, `.devin/`, `Plans/`, `Logs/`) against the actual repository.

The review did NOT assess:
- Functional correctness of workflow logic (use a functional review prompt)
- Quality of code referenced by workflows (e.g., gate scripts)
- Performance characteristics of workflows
- Suitability of workflow design for its intended purpose
