# AR Static Analysis Checks

Committed implementations of the "Custom AR static analysis checks" referenced by
`/close` step 8 and `/scan` step 1 (per `AGENTS.md` OR48). Each script enforces one
Architecture Rule mechanically instead of being re-derived from memory at every close.

## Status: starting point, not yet validated against `sovereignai/`

These were written against the *rule text* in `AGENTS.md`, not against the actual
`sovereignai/` source tree (this governance review had access to the docs repo only,
not the code repo). Before relying on them:

1. Run each script against the real codebase.
2. Check for false positives/negatives against known-good code (e.g. the DI container,
   which AR4/D2 already establishes as compliant) and known violations.
3. Adjust the heuristics in-place — that's the point of OR48: fix the script once,
   reviewed in a diff, instead of re-deriving the check by eye every plan.

## Scripts

| Script | Enforces | Exit 1 on |
|---|---|---|
| `no_globals.py` | AR4 | module-level mutable variables, mutable class-attribute defaults |
| `constructor_arg_cap.py` | AR5 | constructors with >N args (excluding `self`; DTO dataclasses and `main.py` exempt) |
| `no_context_bags.py` | AR6 | untyped `dict`/`Any` params or bare `**kwargs` across function boundaries |
| `docstring_discipline.py` | AR21 | missing docstrings, non-verb-first or <10-word first lines, banned jargon words |
| `no_hardcoded_component_names.py` | AR7/AR9 | UI-layer imports from core component packages |
| `ui_does_not_touch_core.py` | AR7 | a commit touching both UI and core directories |

Each script takes one or more paths and exits non-zero with a list of violations on
stderr if it finds any. Run `--help` on any script for its specific rule citation.
