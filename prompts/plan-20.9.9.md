Depends on: none
Vision principles: P9 (observability by default), governance
Open questions resolved: none

S0 -- Opening
S0.1: Run `/open`
S0.2: Read `AGENTS.md`, `PLANS.md`, `LANDMINES.md` in full

S1 -- Fix LANDMINES.md prepend format
S1.1: Remove all "N/A -- no new patterns" stubs above `## L{n}` headers
S1.2: Ensure `---` separator appears only between entries, not before headers
S1.3: Verify each `## L{n}` header is followed by description, not separator
S1.4: Run `/verify`

S2 -- Update PLANS.md Completed Prompts table
S2.1: Add row for prompt-20.8 (AGENTS.md + LANDMINES.md restructure)
S2.2: Add row for prompt-20.9 (workflow optimization -- 480 tests)
S2.3: Add row for prompt-20.9.1 (TUI AR7 compliance -- 13 scoped tests)
S2.4: Add row for prompt-20.9.2 (hardware probe cleanup -- 59 tests)
S2.5: Verify "Current" test baseline field reads 464 (not 480)
S2.6: Run `/verify`

S3 -- Update AGENTS.md header
S3.1: Count actual AR rules (`## AR{n}` headers)
S3.2: Count actual OR rules (`## OR{n}` headers)
S3.3: Update header to match actual counts
S3.4: Run `/verify`

S4 -- Tests
S4.1: Add `test_document_hygiene.py` -- verify LANDMINES.md format, PLANS.md table completeness
S4.2: Run full test suite, verify no regressions

Closing: Run `/close`
