# External AI Review Report: SovereignAI Planner Workflow Completeness & Functionality

**Reviewer**: External AI Review (independent of SovereignAI development team)
**Repository Reviewed**: `https://github.com/AngusKingCAI/SovereignAI` (branch: `main`)
**Commit Reviewed**: `07df9de Update workflow consistency and Gate A10 compliance`
**Review Date**: 2026-07-22
**Review Scope**: Planner workflow design, implementation, consistency, functionality simulation, best practices, and missing components
**Review Prompt Reference**: `EXTERNAL_AI_REVIEW_PROMPT.md`

---

## Executive Summary

- **Overall Assessment**: **NEEDS REVISION** — The workflow is comprehensively designed and structurally complete, but the validation-script implementation layer is functionally inert. Documentation is strong; runtime enforcement is weak.
- **Critical Issues**: **5 critical (blocking) issues** + 7 moderate issues found
- **Recommendation**: **REQUEST CHANGES** — The workflow cannot be honestly described as "100% complete and working" until the hard gate scripts actually perform validation and the JSON exporter's import path is fixed.

The design surface of the Planner workflow is excellent: phases 0-7 are clearly defined with triggers, goals, steps, exit gates, compliance postings, and BP-grounded reasoning. Templates are comprehensive. The schema is well-designed with audit triggers and history tables. However, **the validation scripts that are advertised as the enforcement mechanism are predominantly placeholders or contain a case-sensitivity bug that makes them silently no-op on Linux filesystems**. As written, no hard gate would actually block a malformed plan from advancing through the workflow.

---

## Detailed Findings

### 1. Workflow Design Status

**File examined**: `.Planner/workflows/PLAN_WORKFLOW.md` (535 lines)

| Criterion | Status |
|-----------|--------|
| Workflow rule index completeness (W1-W4) | ✅ PASS |
| Workflow overview shows complete process flow | ✅ PASS |
| Phases 0-7 properly defined with triggers and goals | ✅ PASS |
| Each phase has detailed steps with exit gates | ✅ PASS |
| Hard gates properly defined and mapped to phases | ✅ PASS |
| Soft gates properly defined for Round Table evaluation | ✅ PASS |
| Gate enforcement mechanisms clearly specified | ✅ PASS |
| Compliance posting requirements defined for each gate | ✅ PASS |
| Universal rules compliance clearly specified | ✅ PASS |
| Stop conditions properly defined | ✅ PASS |
| Evolution conditions documented | ✅ PASS |

**Issues Found**:
- **MODERATE — Phase 2/3 have no hard gate enforcement**: Phase 2 (Plan Structure Design) and Phase 3 (Plan Drafting) lack `run_phase_gates.py --phase 2/3` invocations and lack any explicit HG-* mapping. `run_phase_gates.py` only accepts phases 1, 4, 5, 6. This means structure and drafting defects have no automated enforcement point between Phase 1 and Phase 4.
- **MINOR — Phase 0 (Plan Batch Creation) has no hard gate**: Phase 0 exits on a soft "batch structure defined" gate. This is acceptable because batch creation is a planning decision, but it should be documented as deliberately un-gated.
- **MINOR — Stop Conditions section is inconsistent with phase gating**: It lists "Missing compliance line for any gate = HALT" but this is enforced socially (the agent posts the line), not by any script. The script-based gates do not check compliance-line presence per phase.

**Summary**: Workflow design is well-architected and BP-grounded. The W1-W4 rules are clearly defined with evidence citations. The 12-section brief structure and 4-point rubric design follow established panel-evaluation best practices. Phase 0 is correctly marked optional, and Phase 7 correctly implements the GR3 single-responsibility handoff to the Reviewer.

---

### 2. Implementation Status

**Directories examined**:
- `.Planner/scripts/hard_gates/` (HG-1 through HG-13 + `run_phase_gates.py`)
- `.Planner/scripts/soft_gates/` (SG-1 through SG-3)
- `.Planner/roundtable/` (database, export, templates, schema)
- `.Planner/rules/` (PLANNER_RULES.md)
- `Agents/reviewer/workflows/` (PATTERN_ANALYSIS_WORKFLOW.md, RULE_INTEGRATION_WORKFLOW.md)
- `Agents/reviewer/scripts/soft_gates/` (sg_pattern_count.py, sg_cluster_quality.py, sg_evidence_quality.py)

| Criterion | Status |
|-----------|--------|
| All hard gate scripts (HG-1 through HG-13) implemented | ⚠️ PARTIAL — All 13 files exist, but 8 are pure placeholders |
| All soft gate scripts (SG-1 through SG-3) implemented | ⚠️ PARTIAL — All 3 files exist and run, but use wrong path |
| Round Table templates complete | ✅ PASS (5 templates: PANELIST_PROFILE, BRIEF, SCORING_RUBRIC, PANELIST_PROMPT_TEMPLATES, COMPETENCY_ASSIGNMENT_FRAMEWORK) |
| Database schema properly defined (SQLITE_SCHEMA.md) | ✅ PASS |
| Database manager implemented (database_manager.py) | ✅ PASS (tested successfully — initializes and CRUDs) |
| JSON exporter implemented (json_exporter.py) | ❌ FAIL — Broken import path, runtime crash |
| Reviewer workflows properly defined | ✅ PASS |
| All scripts follow enforcement mechanisms in AGENTS.md | ❌ FAIL — Hard gate scripts do not enforce (see Critical Issue #1) |

**Issues Found**:

#### CRITICAL ISSUE #1 — Hard gate scripts do not actually validate (BLOCKER)

Of the 13 hard gate scripts, only 5 contain actual validation logic (HG-1, HG-2, HG-7, HG-8, HG-9). The other 8 are pure placeholders that always return `True`:

| Gate | File | Status |
|------|------|--------|
| HG-1 | hg1_requirements_complete.py | Logic present, but path bug (see #2) |
| HG-2 | hg2_scope_defined.py | Logic present, but path bug (see #2) |
| HG-3 | hg3_dependencies_feasible.py | **Placeholder — always returns True** |
| HG-4 | hg4_sections_complete.py | **Placeholder — always returns True** |
| HG-5 | hg5_language_clear.py | **Placeholder — always returns True** |
| HG-6 | hg6_landmines_screened.py | **Placeholder — always returns True** |
| HG-7 | hg7_compliance_lines_present.py | Logic present, but path bug (see #2) |
| HG-8 | hg8_paths_valid.py | Logic present, but path bug (see #2) |
| HG-9 | hg9_manifest_complete.py | Logic present, but path bug (see #2) |
| HG-10 | hg10_critical_findings_addressed.py | **Placeholder — always returns True** |
| HG-11 | hg11_high_findings_addressed.py | **Placeholder — always returns True** |
| HG-12 | hg12_no_blocking_landmines.py | **Placeholder — always returns True** |
| HG-13 | hg13_manifest_present.py | **Placeholder — always returns True** |

**AGENTS.md line 128 explicitly states**: "Next: Complete implementation of validation scripts with actual logic (currently placeholders)". The development team is aware of this. However, the workflow documentation does NOT mark these gates as "design only" — it presents them as actively enforced blocking constraints, which is misleading.

**Impact**: A malformed plan with missing sections, ambiguous language, blocking landmines, unaddressed CRITICAL/HIGH findings, or a missing Executor Manifest would pass every hard gate. The workflow cannot be described as "100% working" while the enforcement layer is non-functional.

#### CRITICAL ISSUE #2 — Path case-sensitivity bug in 5 gate scripts (BLOCKER)

The 5 hard gate scripts with logic (HG-1, HG-2, HG-7, HG-8, HG-9) and all 3 soft gate scripts (SG-1, SG-2, SG-3) use `Path("Plans")` (capital P):

```python
plans_dir = Path("Plans")
if not plans_dir.exists():
    print("⚠️  Plans directory not found, skipping validation")
    return True
```

The actual repository directory is **lowercase `plans/`**:

```
$ ls -la SovereignAI | grep plans
drwxrwxr-x  3 z z  4096 Jul 22 03:46 plans
```

On Linux (case-sensitive filesystem), `Path("Plans").exists()` returns `False`. The scripts then print a warning and `return True` (pass). **Empirically verified**:

```
$ python3 .Planner/scripts/hard_gates/run_phase_gates.py --phase 1
Running 3 hard gates for Phase 1...
⚠️  Plans directory not found, skipping validation
⚠️  Plans directory not found, skipping validation
✅ Gate HG-3 PASS: Dependencies are technically feasible
✅ All Phase 1 hard gates passed
```

The only gate that "passes" legitimately is HG-3, which is a pure placeholder.

**Impact**: Even the gates that have logic never run that logic against an actual plan. Hard gate enforcement is effectively zero across the entire workflow.

#### CRITICAL ISSUE #3 — JSON exporter crashes on launch (BLOCKER)

`json_exporter.py` line 15 uses a direct import:

```python
from database_manager import RoundTableDatabase
```

`database_manager.py` lives in `.Planner/roundtable/database/`, but `json_exporter.py` lives in `.Planner/roundtable/export/`. Running it produces:

```
$ python3 .Planner/roundtable/export/json_exporter.py
Traceback (most recent call last):
  File ".../json_exporter.py", line 15, in <module>
    from database_manager import RoundTableDatabase
ModuleNotFoundError: No module named 'database_manager'
```

**Impact**: The Phase 7 handoff step "Findings Export: Export findings to JSON for Reviewer analysis" cannot be executed. The Reviewer's pattern analysis workflow (which queries the JSON export per `PATTERN_ANALYSIS_WORKFLOW.md` Phase 1 SQL) has no JSON to read.

**Fix**: Add `sys.path.insert(0, str(Path(__file__).parent.parent / "database"))` before the import, or use a relative package import.

#### Other Implementation Issues

- **MINOR — `database_manager.py` uses deprecated `datetime.utcnow()`**: Python 3.12+ raises `DeprecationWarning`. Should migrate to `datetime.now(datetime.UTC)`. Tested — works but emits warnings.
- **MINOR — `database_manager.connect()` uses `with self.connect() as conn:` pattern incorrectly**: The context manager `__enter__`/`__exit__` is defined on `RoundTableDatabase`, not on the connection object. The pattern `with self.connect() as conn:` will not actually close the connection. Tested — operations succeed because the connection is reused, but resource cleanup is not happening as intended.
- **MINOR — `init_database.py` creates database in working directory**: Uses `Path(".Planner/roundtable/database")` relative to CWD. If invoked from outside the repo root, it will create stray databases. Should resolve relative to `__file__`.

---

### 3. Consistency Status

**Files examined**:
- `AGENTS.md` (architect session governance)
- `.Planner/workflows/PLAN_WORKFLOW.md` (workflow design)
- `.Planner/rules/PLANNER_RULES.md` (planner rules)
- `Agents/reviewer/workflows/*.md` (reviewer workflows)

| Criterion | Status |
|-----------|--------|
| Rule references are consistent (W1-W4, not A1-A4) | ✅ PASS |
| Gate numbering is consistent (PLAN-0 through PLAN-7) | ✅ PASS |
| Hard gate references match actual script implementations | ✅ PASS (filenames match) |
| Soft gate references match actual script implementations | ✅ PASS (filenames match) |
| Agent responsibilities properly separated (Planner vs Reviewer) | ✅ PASS (per GR3) |
| Handoff boundaries clearly defined | ✅ PASS (Phase 7 to Reviewer) |
| Gate A10 (git push confirmation) properly enforced | ✅ PASS (see below) |
| No conflicting rules or gate definitions | ⚠️ PARTIAL (see issues) |

**Issues Found**:

#### CRITICAL ISSUE #4 — Broken path reference: `Agents/shared/UNIVERSAL_RULES.md`

`Agents/planner/AGENTS.md` line 9, line 15, `Agents/reviewer/AGENTS.md` line 9, line 15, and `PLANNER_RULES.md` line 300 all reference:

```
../shared/UNIVERSAL_RULES.md
```

(or `Agents/shared/UNIVERSAL_RULES.md`)

**The `Agents/shared/` directory does not exist.** The actual file is at `Agents/UNIVERSAL_RULES.md`:

```
$ ls Agents/
UNIVERSAL_RULES.md  executor  planner  researcher  reviewer

$ ls Agents/shared/
ls: cannot access 'Agents/shared/': No such file or directory
```

**Impact**: When an agent follows its AGENTS.md "Supremacy Check" step 2 ("Follow ../shared/UNIVERSAL_RULES.md"), the read will fail. The supremacy-check protocol is broken at the first instruction.

#### CRITICAL ISSUE #5 — AGENTS.md self-contradicts on session gate count

- AGENTS.md line 69: "Architect Session Gates (A1-A10)"
- AGENTS.md line 133: "AGENTS.md: Session gates (A1-A7)"

The lower section was not updated when A8, A9, A10 were added.

**Impact**: Inconsistent documentation. The Rule Document Indexing section (which is supposed to be the canonical index) is wrong. A reviewer or auditor reading top-to-bottom would conclude A8-A10 don't exist.

#### Other Consistency Issues

- **MINOR — PR16 references `Agents/shared/UNIVERSAL_RULES.md`** but should reference `Agents/UNIVERSAL_RULES.md`. Same broken path as #4.
- **MINOR — `AGENTS.md` line 8** says "New structure: `Agents/` for governance, `.Planner/`, `.Executor/`, `.Reviewer/`, `.Researcher/` for working files" — this is accurate.
- **MINOR — Soft gate scripts path mismatch**: `run_phase_gates.py` line 106 defaults `--scripts-dir` to `.Planner/scripts/hard_gates`, but then runs soft gate scripts (line 96-97) using the same `scripts_dir`. The soft gates are actually in `.Planner/scripts/soft_gates/`. The runner will print "Gate script not found" and silently skip them. Verified: running `--phase 6` does not execute SG-1/2/3.

#### Gate A10 (Git Push Confirmation) — ✅ PROPERLY ENFORCED

`AGENTS.md` line 25 defines Gate A10. `json_exporter.py` `_git_commit()` method (line 158-170) correctly implements local commit only — no `git push` call. Commit messages explicitly state "local commit, not pushed per Gate A10". This is correctly enforced in code.

---

### 4. Functionality Status

**Scenario Simulated**: User requests "Create a plan to implement user authentication"

**Walkthrough**:

| Phase | Action | Hard Gates Would Pass? | Soft Gates Would Function? | Compliance Posted? |
|-------|--------|------------------------|----------------------------|---------------------|
| Phase 1 | Read design doc, assess requirements, define scope | ❌ Silently skipped (path bug) | N/A | Posted in markdown |
| Phase 2 | Design plan header, manifest, phases | No gates defined for Phase 2 | N/A | Posted in markdown |
| Phase 3 | Draft plan, fill sections | No gates defined for Phase 3 | N/A | Posted in markdown |
| Phase 4 | Verify quality, screen landmines | ❌ HG-4, HG-5, HG-6 are placeholders (return True) | N/A | Posted in markdown |
| Phase 5 | Finalize plan, validate manifest | ❌ HG-7, HG-8, HG-9 silently skipped (path bug) | N/A | Posted in markdown |
| Phase 6.1-6.3 | Pre-Round Table prep, panelist evaluation, debrief | N/A (no gates) | N/A | Posted in markdown |
| Phase 6.4 | Clean pass gate | ❌ HG-10, HG-11, HG-12, HG-13 are placeholders | ❌ SG-1, SG-2, SG-3 silently skipped (path bug + runner bug) | Posted in markdown |
| Phase 7 | Handoff to Reviewer | N/A | N/A | Posted in markdown |
| Phase 7 (Reviewer side) | Findings export | ❌ `json_exporter.py` crashes on import | N/A | N/A |

| Criterion | Status |
|-----------|--------|
| End-to-end workflow simulation | ❌ FAIL — Multiple blocker issues prevent execution |
| Hard gate blocking behavior | ❌ FAIL — No hard gate actually blocks (placeholders + path bug) |
| Soft gate recommendation behavior | ❌ FAIL — Soft gates silently skipped by runner |
| Database operations | ✅ PASS — `database_manager.py` tested successfully |
| JSON export functionality | ❌ FAIL — `json_exporter.py` crashes on import |
| Git operations respecting Gate A10 | ✅ PASS — Commit only, no push |

**Issues Found**:

#### Functionality Simulation — Detailed Walkthrough

1. **Phase 1 (Input Assessment)**: User submits authentication plan request. Planner reads Researcher design doc, assesses requirements, defines scope. The workflow says to run `python .Planner/scripts/hard_gates/run_phase_gates.py --phase 1`. As verified above, this prints "Plans directory not found, skipping validation" for HG-1 and HG-2, and HG-3 returns True as a placeholder. All three gates "pass" without examining any plan content. **The plan advances to Phase 2 regardless of whether requirements are actually complete, scope is defined, or dependencies are feasible.**

2. **Phase 2 (Plan Structure Design)**: No hard gates defined. Planner designs header, manifest, phase structure. Workflow exits on a soft compliance line. No automation runs.

3. **Phase 3 (Plan Drafting)**: No hard gates defined. Planner drafts the plan. Workflow exits on a soft compliance line. No automation runs.

4. **Phase 4 (Quality Gates Verification)**: Workflow says to run `python .Planner/scripts/hard_gates/run_phase_gates.py --phase 4`. This invokes HG-4 (sections complete), HG-5 (language clear), HG-6 (landmines screened). All three are pure placeholders that return `True` immediately without reading any file. **A plan missing required sections, with ambiguous language and blocking landmines, would pass Phase 4.**

5. **Phase 5 (Plan Finalization)**: Workflow says to run `python .Planner/scripts/hard_gates/run_phase_gates.py --phase 5`. This invokes HG-7 (compliance lines present), HG-8 (paths valid), HG-9 (manifest complete). All three have logic, but all use `Path("Plans")` (capital P). The scripts print "Plans directory not found, skipping validation" and return `True`. **A plan with no compliance lines, invalid paths, and an incomplete manifest would pass Phase 5.**

6. **Phase 6.1-6.3 (Round Table Preparation and Evaluation)**: These phases are documentation-driven. The Planner assembles a brief using the 12-section template, prepares panelist profiles using the panelist profile template, creates prompts using the prompt templates. The brief structure is well-defined and the templates are usable. However, no script validates that the brief has all 12 sections or that panelist profiles are correctly assembled. The phases execute as documentation workflows only.

7. **Phase 6.4 (Clean Pass Gate)**: Workflow says to run soft gates SG-1, SG-2, SG-3 individually, then hard gates via `run_phase_gates.py --phase 6`. Three problems:
   - The soft gate scripts use `Path("Plans")` (capital P) — they will silently skip.
   - The hard gate runner's `--phase 6` invocation tries to run soft gates using the hard-gate scripts directory (path mismatch bug) — soft gates silently skipped by runner.
   - The four hard gates HG-10, HG-11, HG-12, HG-13 are all pure placeholders that return `True`.
   
   **A plan with unaddressed CRITICAL findings, unaddressed HIGH findings, blocking landmines, and a missing Executor Manifest would pass Phase 6.4.**

8. **Phase 7 (Handoff to Reviewer)**: Workflow says "Export findings to JSON for Reviewer analysis". Running `python .Planner/roundtable/export/json_exporter.py` crashes immediately with `ModuleNotFoundError: No module named 'database_manager'`. **The handoff cannot be executed as designed.**

**End-to-end result**: The workflow would complete all phases from a documentation standpoint (compliance lines would be posted), but at no point would any automated gate actually validate or block anything. The "100% hard gate enforcement" claim is not realized in code.

---

### 5. Best Practices Status

| Criterion | Status |
|-----------|--------|
| Workflow follows BP for panelist evaluation (independent scoring, evidence-first) | ✅ PASS |
| Round Table evaluation uses BP-based quality gates | ✅ PASS (design only) |
| Web search integration properly specified | ✅ PASS (Rule W3, integrated into panelist prompts) |
| Template structures comprehensive and usable | ✅ PASS (5 templates, all detailed) |
| Database schema supports all required operations | ✅ PASS (tested CRUD, audit triggers, export views) |
| JSON export format properly structured | ✅ PASS (format is correct in `JSON_EXPORT_FORMAT.md`) |
| Git operations follow safety protocols (Gate A10) | ✅ PASS (commit only, no push) |
| Error handling and recovery defined | ⚠️ PARTIAL |

**Issues Found**:

- **MODERATE — BP claims not validated in code**: The workflow repeatedly cites BP research ("hard-gated verification catches 100% of corrupt episodes with zero false positives"). The actual hard gate implementation catches 0% of corrupt episodes because the gates don't run real validation. The BP justification is correct in principle but unimplemented in practice.
- **MINOR — No calibration process for panelist scoring**: The scoring rubric template mentions a calibration process but no script or workflow step enforces it. This is documented but not operationalized.
- **MINOR — No ML clustering implementation**: `PATTERN_ANALYSIS_WORKFLOW.md` Phase 3 specifies K-means/DBSCAN clustering with scikit-learn, but no Python script implements it. The workflow is documentation-only at the ML layer.
- **MINOR — Error recovery for failed gate scripts**: `run_phase_gates.py` handles `TimeoutExpired` and general `Exception`, but does not retry or log to the audit database. Recovery is "fail and stop".

---

### 6. Missing Components Status

| Criterion | Status |
|-----------|--------|
| No missing phase definitions | ✅ PASS (Phases 0-7 all defined) |
| No missing gate definitions | ✅ PASS (HG-1 to HG-13, SG-1 to SG-3, PA-1 to PA-8, RI-1 to RI-5) |
| No missing script implementations | ⚠️ PARTIAL — All scripts exist, but 8 of 13 hard gates are placeholders |
| No missing template files | ✅ PASS (5 templates in `.Planner/roundtable/templates/`) |
| No missing database components | ✅ PASS (init + manager + schema) |
| No missing integration points | ⚠️ PARTIAL — JSON exporter broken (Critical Issue #3) |
| No undefined references or broken links | ❌ FAIL — `Agents/shared/UNIVERSAL_RULES.md` broken (Critical Issue #4) |
| No incomplete rule definitions | ✅ PASS (PR1-PR16, GR1-GR5, ER1-ER5, W1-W4, G6, A1-A10) |

**Issues Found**:

- **MODERATE — No actual implementation of pattern analysis pipeline**: The `PATTERN_ANALYSIS_WORKFLOW.md` describes a 7-phase pipeline with frequency analysis, ML clustering, rule generation, validation, and reporting. No Python script exists to execute this pipeline. The Reviewer soft gate scripts (sg_pattern_count, sg_cluster_quality, sg_evidence_quality) only check for the *presence* of pattern-analysis files; they don't actually run the analysis.
- **MODERATE — No actual implementation of rule integration**: `RULE_INTEGRATION_WORKFLOW.md` Phase 4 specifies a Python function `integrate_rules_into_planner_rules()` that reads PLANNER_RULES.md, formats rules, and writes them back. No script implements this. The workflow is documentation-only.
- **MINOR — No brief validation script**: The 12-section brief structure is documented, but no script validates that an assembled brief actually contains all 12 sections. A brief missing sections 5, 9, and 11 would not be caught.

---

## Critical Issues (Blockers)

These issues prevent the workflow from functioning as designed and must be fixed before the workflow can be described as "100% complete and working":

1. **Hard gate scripts are predominantly placeholders** — 8 of 13 hard gate scripts (HG-3, HG-4, HG-5, HG-6, HG-10, HG-11, HG-12, HG-13) contain only `return True` with no validation logic. They will pass any plan regardless of content. **Fix**: Implement the validation logic described in each script's docstring and the AGENTS.md gate definitions.

2. **Path case-sensitivity bug in 5 hard gate + 3 soft gate scripts** — Scripts use `Path("Plans")` (capital P) but the actual directory is `plans` (lowercase). On Linux, the scripts silently skip validation and return `True`. **Fix**: Change `Path("Plans")` to `Path("plans")` in hg1, hg2, hg7, hg8, hg9, sg1, sg2, sg3.

3. **JSON exporter crashes on launch** — `json_exporter.py` uses `from database_manager import RoundTableDatabase` but `database_manager.py` is in a sibling directory. `ModuleNotFoundError` is raised immediately. **Fix**: Add `sys.path.insert(0, str(Path(__file__).parent.parent / "database"))` before the import, or restructure as a Python package with relative imports.

4. **Broken path reference to `Agents/shared/UNIVERSAL_RULES.md`** — The `Agents/shared/` directory does not exist. The actual file is at `Agents/UNIVERSAL_RULES.md`. The Planner and Reviewer AGENTS.md files and `PLANNER_RULES.md` rule PR16 all reference the broken path. **Fix**: Either create `Agents/shared/` and move `UNIVERSAL_RULES.md` there, or update all references to `../UNIVERSAL_RULES.md`.

5. **Hard gate runner does not execute soft gates** — `run_phase_gates.py` invokes soft gate scripts using the hard-gate scripts directory. Soft gate scripts are in `.Planner/scripts/soft_gates/`, but the runner looks in `.Planner/scripts/hard_gates/`. The runner prints "Gate script not found" and silently skips. **Fix**: Update `PHASE_SOFT_GATES` mapping to use a separate `soft_gates_dir` parameter, or run soft gate scripts via absolute path.

---

## Recommendations

Ordered by priority (highest impact first):

### Tier 1 — Required for "100% working" claim

1. **Implement all 8 placeholder hard gate scripts with actual validation logic.** Each script should read the most recent plan file (using the correct lowercase `plans` path), parse the markdown, and validate the specific gate condition. Reference the existing logic in HG-1, HG-2, HG-7, HG-8, HG-9 as templates.

2. **Fix the `Plans` → `plans` case-sensitivity bug in all 8 affected scripts** (HG-1, HG-2, HG-7, HG-8, HG-9, SG-1, SG-2, SG-3). This is a one-line fix per file but unblocks all path-based validation.

3. **Fix the JSON exporter import path.** Add `sys.path.insert(0, str(Path(__file__).parent.parent / "database"))` to `json_exporter.py` before the `from database_manager import` line. Test by running `python3 .Planner/roundtable/export/json_exporter.py` from the repo root.

4. **Resolve the `Agents/shared/UNIVERSAL_RULES.md` broken reference.** Either:
   - Create `Agents/shared/` and move `UNIVERSAL_RULES.md` there (preserves the "shared" semantic), OR
   - Update all references in `Agents/planner/AGENTS.md`, `Agents/reviewer/AGENTS.md`, `Agents/executor/AGENTS.md`, `Agents/researcher/AGENTS.md`, and `PLANNER_RULES.md` PR16 to point to `../UNIVERSAL_RULES.md`.

5. **Fix `run_phase_gates.py` soft gate invocation.** Add a separate `--soft-gates-dir` parameter (default `.Planner/scripts/soft_gates`) and pass it to `run_gate()` when `gate_type="soft"`.

### Tier 2 — Strongly recommended for production quality

6. **Add hard gates for Phases 2 and 3.** Phase 2 (Plan Structure Design) and Phase 3 (Plan Drafting) currently have no automated enforcement. Consider adding HG-14 (plan structure follows PR6) and HG-15 (path verification per PR2) mapped to Phase 3.

7. **Implement the pattern analysis pipeline as actual scripts.** `PATTERN_ANALYSIS_WORKFLOW.md` describes frequency analysis, ML clustering, and rule generation in pseudocode. Implement these as Python scripts in `Agents/reviewer/scripts/` so the Reviewer can actually execute the workflow.

8. **Implement the rule integration script.** `RULE_INTEGRATION_WORKFLOW.md` Phase 4 specifies `integrate_rules_into_planner_rules()` in pseudocode. Implement it as a Python script that reads PLANNER_RULES.md, formats approved rules, and writes them back with index updates.

9. **Update AGENTS.md line 133 from "(A1-A7)" to "(A1-A10)"** to match line 69. This is a one-line fix.

10. **Add a brief validation script** that checks an assembled brief has all 12 sections. This closes the gap between "brief assembled" (Phase 6.6) and "brief validated".

### Tier 3 — Polish and robustness

11. **Migrate `datetime.utcnow()` to `datetime.now(datetime.UTC)`** in `database_manager.py` and `json_exporter.py` to silence Python 3.12+ deprecation warnings.

12. **Fix `database_manager.connect()` context-manager usage.** The `with self.connect() as conn:` pattern doesn't close the connection because `__enter__`/`__exit__` are defined on `RoundTableDatabase`, not on the connection. Either return `self` from `connect()` and use `with self as db:` or restructure to use `sqlite3.Connection` context manager.

13. **Resolve `init_database.py` paths relative to `__file__`** instead of CWD, so the script can be invoked from any directory.

14. **Add per-phase compliance-line checking to the hard gate runner.** Currently, missing compliance lines are listed in "Stop Conditions" but no script checks for them. Consider HG-16: "All required `✅ Gate PLAN-N.M PASS` lines present in plan file".

15. **Add a `--plan-file` parameter to `run_phase_gates.py`** so the runner can validate a specific plan rather than auto-discovering the most-recently-modified file. This makes the gates testable and deterministic.

---

## Final Determination

**Is the workflow 100% complete and working?**: **NO**

### What Needs to Be Fixed to Achieve 100% Completion

The workflow is **structurally complete and well-designed** but **functionally non-enforcing**. To reach 100%:

1. **All 13 hard gate scripts must contain actual validation logic** (8 are currently placeholders).
2. **The `Plans` → `plans` case-sensitivity bug must be fixed** in 8 scripts (5 hard gates + 3 soft gates).
3. **The JSON exporter's import path must be fixed** so Phase 7 handoff can execute.
4. **The `Agents/shared/UNIVERSAL_RULES.md` broken reference must be resolved** so the agent supremacy check works.
5. **The hard gate runner's soft-gate directory mismatch must be fixed** so soft gates actually run.

Once these 5 critical issues are resolved, the workflow will be both structurally and functionally complete. The design layer (templates, schema, workflow phases, rule indexing, BP integration) is already at production quality and requires no changes.

### Summary Assessment

| Layer | Status |
|-------|--------|
| Workflow design (PLAN_WORKFLOW.md) | ✅ Complete |
| Rule definitions (PR1-PR16, W1-W4, G6) | ✅ Complete |
| Templates (5 files) | ✅ Complete |
| Database schema and manager | ✅ Complete and tested |
| Hard gate script logic | ❌ 8 of 13 are placeholders |
| Hard gate script paths | ❌ Case-sensitivity bug in 5 of 5 logic-bearing scripts |
| Soft gate script paths | ❌ Case-sensitivity bug in 3 of 3 scripts |
| Hard gate runner (orchestration) | ❌ Soft gate directory mismatch |
| JSON exporter | ❌ Broken import path |
| Reviewer workflows (design) | ✅ Complete |
| Reviewer workflows (implementation) | ❌ Pattern analysis and rule integration are documentation-only |
| Path references in AGENTS.md / rules | ❌ `Agents/shared/` does not exist |
| Gate A10 enforcement | ✅ Correctly implemented |
| Documentation consistency | ⚠️ A1-A7 vs A1-A10 inconsistency |

The SovereignAI Planner workflow has the architectural foundation of a production-grade system. The gap between design and implementation is concentrated in the validation-script layer. Closing that gap — primarily by replacing placeholder `return True` statements with real validation logic and fixing two path bugs — would move the workflow from "NEEDS REVISION" to "COMPLETE".

---

*End of review report.*
