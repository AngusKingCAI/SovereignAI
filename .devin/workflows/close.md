---
name: close
description: Alias for /close skill. Same rules, same gates.
---

See `.devin/skills/close/SKILL.md` for full checklist.

Key hard gates (cannot proceed if fail):
1. All AR check scripts pass
2. `scripts/verify_close.py` exits 0 (BEFORE git tag)
3. CHANGELOG has latest prompt at top
4. prompts/ root has no plan-{N} files
5. Execution log < 500 bytes

STOP on any failure. No workarounds. No "being helpful."
