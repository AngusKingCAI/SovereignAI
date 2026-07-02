Depends on: prompt-20.8
Vision principles: A8 (no hidden complexity), workflow efficiency
Open questions resolved: none

## S0 — Opening

- S0.1: Run `/open`
- S0.2: Read `AGENTS.md` in full
- S0.3: Add new rules if needed, commit before coding

## S1 — Close Workflow (Post-Implementation)

- S1.1: Verify workflow optimization already implemented (scripts, workflow files, governance files)
- S1.2: Run full test suite: `pytest tests/ -q`
- S1.3: Run ruff check on all modified files
- S1.4: Append to CHANGELOG.md with workflow optimization summary
- S1.5: Update PLANS.md baseline with new test count (480)
- S1.6: Add diskcache CVE to DEBT.md with target plan prompt-21
- S1.7: Update LANDMINES.md with "N/A — no new patterns for prompt-20.9"
- S1.8: Verify DEBT.md has exactly 1 reference to prompt-20.9
- S1.9: Run spec_match.py to verify plan matches implementation
- S1.10: Run all close workflow checks (AR checks, etc.)
- S1.11: Git add, commit, tag, and push

## Closing

Run `/close`
