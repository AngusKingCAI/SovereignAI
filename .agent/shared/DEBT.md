# DEBT.md — SovereignAI Deferred Items

Open items only. Resolved items → CHANGELOG.md.

---

## Open Items

| ID | Item | Severity | Priority | Status | Target | Trigger |
|----|------|----------|----------|--------|--------|---------|
| DEBT-1 | diskcache CVE-2025-69872 | Critical | High | Identified | TBD | diskcache PR #361 merged to PyPI |
| DEBT-2 | First-run experience UI | Medium | Low | Identified | TBD | UI implementation prioritised |

## Resolved Items → See CHANGELOG.md

---

## DEBT-1 — diskcache CVE-2025-69872

**Severity**: Critical
**Priority**: High
**Status**: Identified
**Target**: TBD
**Trigger**: When diskcache PR #361 is merged and released to PyPI.
**Reason**: pip-audit reports CVE-2025-69872 in diskcache 5.6.3 (transitive from huggingface_hub). Insecure pickle deserialization (CWE-94) — attacker with write access to cache directory achieves arbitrary code execution when victim application reads from cache. CVSS 9.8. Fix in PR #361 (HMAC-verified pickle envelope), not yet merged to PyPI as of 2026-07-03.

---

## DEBT-2 — First-run experience UI

**Severity**: Medium
**Priority**: Low
**Status**: Identified
**Target**: TBD
**Trigger**: When first-run experience UI implementation is prioritised.
**Reason**: Plan S4 deferred per OR17 (deliverables ship in full or defer). 5-step wizard with HTML/JS/web endpoints not implemented. Existing auth system has /api/auth/register; first-run UI would be a frontend wrapper.
