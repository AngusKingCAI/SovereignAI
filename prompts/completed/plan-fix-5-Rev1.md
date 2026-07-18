Depends on: plan-fix-4-Rev1
Vision principles: P3 (Reliability), P11 (Quality)
Open questions resolved: none

## S0 — Opening

S0.0: Clone latest repo. Verify plan-fix-4-Rev1 completed.
S0.1: Run `/open`
S0.2: Read `AGENTS.md` in full
S0.3: Check `.agent/shared/DEBT.md`
S0.4: Run `grep -r '\bOR(17|19|29|48|61|63|65)\b' --include='*.md' --include='*.py' .` — catalog all legacy OR citations

## F1 — Map Legacy OR IDs to New Scheme

**Problem**: UOR-1, UOR-2, COR-1, OR48, OR61, UOR-3, OR65 cited across repo but undefined in OR_RULES.md.

F1.1: Read `.agent/shared/OR_RULES.md` and identify current rule IDs
F1.2: Create mapping:
  - UOR-1 → UOR-1 (Deliverables Ship in Full) — already exists, just update citations
  - UOR-2 → UOR-2 (Test/Static Analysis Failures) — already exists, just update citations
  - UOR-3 → UOR-3 (diskcache CVE Monitoring) — already exists, just update citations
  - COR-1 → COR-1 (test-fix plans run full suite) — define if not exists
  - OR48 → [RETIRED] No equivalent found; document as retired
  - OR61 → [RETIRED] No equivalent found; document as retired
  - OR65 → [RETIRED] No equivalent found; document as retired
F1.3: Add "Retired Rules" section to OR_RULES.md with mapping table
F1.4: Run `pytest .agent/executor/tests/test_document_hygiene.py -v` — verify pass

## F2 — Run Migration Script Across Repo

F2.1: Create `.agent/executor/scripts/migrate_or_ids.py` — script that:
  - Reads mapping from F1
  - Scans all .md and .py files for legacy OR citations
  - Replaces with new IDs where mapping exists
  - Flags ambiguous citations for manual review
F2.2: Run on: CHANGELOG.md, DEBT.md, DECISIONS.md, all SKILL.md files, all plan files, all log files
F2.3: Manual review of flagged ambiguous replacements
F2.4: Run `pytest .agent/executor/tests/test_document_hygiene.py -v` — verify pass

## F3 — Fix check_rule_crossrefs.py Blind Spots

**Problem**: Only scans 4 files, exempts CHANGELOG.md entirely, doesn't scan skills/scripts/plans.

F3.1: Read `.agent/executor/scripts/check_rule_crossrefs.py`
F3.2: Expand scanned files to include:
  - AGENTS.md
  - .devin/skills/*/SKILL.md
  - .agent/executor/scripts/**/*.py
  - prompts/*.md
  - logs/*.md
F3.3: Remove blanket CHANGELOG.md exemption; exempt only entries older than rule-rename date
F3.4: Add validation: every cited rule ID must exist in OR_RULES.md or ARCHITECTURE.md
F3.5: Run `python .agent/executor/scripts/check_rule_crossrefs.py` — verify exits 0
F3.6: Run `pytest .agent/executor/tests/test_check_rule_crossrefs.py -v` — verify pass

## F4 — Verify No Undefined Citations Remain

F4.1: Run `grep -r '\bOR(17|19|29|48|61|63|65)\b' --include='*.md' --include='*.py' .` — should return only historical log entries
F4.2: If any non-log citations remain, fix manually
F4.3: Run full test suite: `pytest .agent/executor/tests/ -x --tb=short`

## Closing

Run `/close`
