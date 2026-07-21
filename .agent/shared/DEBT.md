# DEBT.md — SovereignAI Deferred Items

Open items only. Resolved items → CHANGELOG.md.

---

## Open Items

| ID | Item | Severity | Priority | Status | Target | Trigger |
|----|------|----------|----------|--------|--------|---------|
| DEBT-4 | UI implementations (cli, phone) | Low | Low | Identified | TBD | UI implementation prioritised |
| DEBT-6 | Librarian.handle_event method + episodic event consumer | Medium | Medium | Identified | TBD | Event system prioritised |
| DEBT-7 | TUI cookie auth for agent SSE stream | Low | Low | Identified | TBD | TUI framework investigation |
| DEBT-8 | Web UI consumer for agent SSE stream | Low | Low | Identified | TBD | Web UI implementation prioritised |
| DEBT-9 | Cross-task persistent graph memory | Medium | Medium | Identified | TBD | Graph memory prioritised |

## Resolved Items → See CHANGELOG.md

---

## DEBT-11 — Workflow compliance verification system (Resolved)

**Severity**: Medium
**Priority**: High
**Status**: Resolved
**Target**: Plan 28
**Reason**: Implemented in Plan 28. Created Executor Manifest in plan files, execution trace logging, execution attestation production, `verify_execution.py` script, and hook scripts for real-time enforcement. Compliance system fully functional and tested on Plan 28.

---

## DEBT-1 — diskcache CVE-2025-69872 (Resolved - False Debt)

**Severity**: High
**Priority**: High
**Status**: Resolved
**Target**: Plan 25.2
**Reason**: Investigation in Plan 25.2 revealed that diskcache is not a direct dependency in app/txt/requirements.txt and is not imported in any .py files under app/. TaskGraphCache uses SQLite directly. diskcache was only a transitive dependency from llama-cpp-python, which is now excluded from requirements. No action required - marked as false debt.

---

## DEBT-2 — Retired

Previously: setuptools CVE-2024-6345. Removed — fixed in setuptools v70.0 (July 2024), available on PyPI. Handle via dependency bump, not deferred debt.

---

## DEBT-3 — DIContainer Circular Import (Resolved - False Debt)

**Severity**: Medium
**Priority**: Low
**Status**: Resolved
**Target**: Plan 25.2
**Reason**: Investigation in Plan 25.2 revealed no circular import exists in app/sovereignai/di/container.py. The DIContainer implementation uses proper forward references and lazy imports. No circular dependency detected - marked as false debt.

---

## DEBT-10 — AR7 violation - UI/core layering in Plan 25 (Resolved)

**Severity**: Medium
**Priority**: Medium
**Status**: Resolved
**Target**: Plan 25.2
**Reason**: Fixed in Plan 25.2 by removing direct import of sovereignai.managers.coding.CodingManager from app/tui/panels/workers.py and app/web/main.py. These files now use DIContainer to retrieve LifecycleManager, maintaining proper UI/core layering per AR7.

---

## DEBT-5 — P4 compliance test isolation (Resolved - False Debt)

**Severity**: Low
**Priority**: Low
**Status**: Resolved
**Target**: Plan 25.3
**Reason**: Investigation in Plan 25.3 revealed that P4 compliance tests (test_p4_compliance.py) are passing and do not have isolation issues. The tests properly handle temporary modifications and edge cases. No action required - marked as false debt.
