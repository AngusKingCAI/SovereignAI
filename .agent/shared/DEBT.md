# DEBT.md — SovereignAI Deferred Items

Open items only. Resolved items → CHANGELOG.md.

---

## Open Items

| ID | Item | Severity | Priority | Status | Target | Trigger |
|----|------|----------|----------|--------|--------|---------|
| DEBT-1 | diskcache CVE-2025-69872 | High | Medium | Identified | TBD | diskcache PR #361 merged to PyPI |
| DEBT-2 | setuptools CVE-2024-6345 ×5 | High | Medium | Identified | 20.11 | Dependency upgrade scheduled |
| DEBT-3 | First-run experience UI | Medium | Low | Identified | TBD | UI implementation prioritised |

## Resolved Items → See CHANGELOG.md

---

## DEBT-1 — diskcache CVE-2025-69872

**Severity**: High
**Priority**: Medium
**Status**: Identified
**Target**: TBD
**Trigger**: When diskcache PR #361 is merged and released to PyPI.
**Reason**: pip-audit reports CVE-2025-69872 in diskcache 5.6.3 (transitive from huggingface_hub). Path traversal vulnerability. Fix in PR #361, not yet merged to PyPI as of 2026-07-03.

---

## DEBT-2 — setuptools CVE-2024-6345 ×5

**Severity**: High
**Priority**: Medium
**Status**: Identified
**Target**: 20.11
**Trigger**: When dependency upgrade plan is scheduled.
**Reason**: pip-audit reports 5 CVEs in setuptools (CVE-2024-6345). Transitive dependencies. Upgrade may break other packages.

---

## DEBT-3 — First-run experience UI

**Severity**: Medium
**Priority**: Low
**Status**: Identified
**Target**: TBD
**Trigger**: When first-run experience UI implementation is prioritised.
**Reason**: Plan S4 deferred per OR17 (deliverables ship in full or defer). 5-step wizard with HTML/JS/web endpoints not implemented. Existing auth system has /api/auth/register; first-run UI would be a frontend wrapper.
