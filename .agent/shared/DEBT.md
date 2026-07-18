# DEBT.md — SovereignAI Deferred Items

Open items only. Resolved items → CHANGELOG.md.

---

## Open Items

| ID | Item | Severity | Priority | Status | Target | Trigger |
|----|------|----------|----------|--------|--------|---------|
| DEBT-1 | diskcache CVE-2025-69872 | High | High | Identified | TBD | diskcache PR #361 merged to PyPI |
| DEBT-2 | — | — | — | — | — | — |
| DEBT-3 | First-run experience UI | Medium | Low | Identified | TBD | UI implementation prioritised |
| DEBT-4 | UI implementations (web, tui) | Low | Low | Identified | TBD | UI implementation prioritised |
| DEBT-5 | P4 compliance test isolation | Low | Low | Identified | TBD | Test infrastructure improvement |
| DEBT-6 | Librarian.handle_event method + episodic event consumer | Medium | Medium | Identified | TBD | Event system prioritised |

## Resolved Items → See CHANGELOG.md

---

## DEBT-1 — diskcache CVE-2025-69872

**Severity**: High
**Priority**: High
**Status**: Identified
**Target**: TBD
**Trigger**: When diskcache PR #361 is merged and released to PyPI.
**Reason**: pip-audit reports CVE-2025-69872 in diskcache 5.6.3 (transitive from huggingface_hub). Insecure pickle deserialization (CWE-502) — attacker with write access to cache directory achieves arbitrary code execution when victim application reads from cache. CVSS 7.3 (High). Fix in PR #361 (HMAC-verified pickle envelope), not yet merged to PyPI as of 2026-07-03.

---

## DEBT-2 — Retired

Previously: setuptools CVE-2024-6345. Removed — fixed in setuptools v70.0 (July 2024), available on PyPI. Handle via dependency bump, not deferred debt.

---

## DEBT-3 — First-run experience UI

**Severity**: Medium
**Priority**: Low
**Status**: Identified
**Target**: TBD
**Trigger**: When first-run experience UI implementation is prioritised.
**Reason**: Plan S4 deferred per UOR-1 (deliverables ship in full or defer). 5-step wizard with HTML/JS/web endpoints not implemented. Existing auth system has /api/auth/register; first-run UI would be a frontend wrapper.

---

## DEBT-4 — UI implementations (cli, phone)

**Severity**: Low
**Priority**: Low
**Status**: Identified
**Target**: TBD
**Trigger**: When UI implementation is prioritised.
**Reason**: UI directories app/web and app/tui exist with main.py implementations, but app/cli and app/phone only have .gitkeep placeholders. Tests for AR7 (no core imports in UI) skip because there are no actual .py files in cli/phone directories to scan.

---

## DEBT-5 — P4 compliance test isolation

**Severity**: Low
**Priority**: Low
**Status**: Identified
**Target**: TBD
**Trigger**: When test infrastructure improves to support isolated file modifications.
**Reason**: P4 compliance tests (test_p4_compliance.py) require temporary modifications to manifest files and DEBT.md to test edge cases (1 adapter vs 2 adapters, exception handling). Current test infrastructure cannot safely isolate these modifications without risking impact on real files. Tests deferred until better isolation mechanisms available.

---

## DEBT-6 — Librarian.handle_event method + episodic event consumer

**Severity**: Medium
**Priority**: Medium
**Status**: Identified
**Target**: TBD
**Trigger**: When event system prioritised.
**Reason**: Plan 22 S5 deferred — Librarian has no handle_event method. Need to implement episodic event consumer pattern for librarian to subscribe to task events (created, updated, completed) for knowledge graph updates.
