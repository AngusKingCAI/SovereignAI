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
| DEBT-11 | Workflow compliance verification system | Medium | High | In Progress | Plan 28 | Compliance system implementation |

## Resolved Items → See CHANGELOG.md

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

---

## DEBT-4 — UI implementations (cli, phone)

**Severity**: Low
**Priority**: Low
**Status**: Identified
**Target**: TBD
**Trigger**: When UI implementation is prioritised.
**Reason**: UI directories app/web and app/tui exist with functional main.py implementations (completed in Plan 25.2), but app/cli and app/phone only have .gitkeep placeholders. Tests for AR7 (no core imports in UI) skip because there are no actual .py files in cli/phone directories to scan.

---

## DEBT-6 — Librarian.handle_event method + episodic event consumer

**Severity**: Medium
**Priority**: Medium
**Status**: Identified
**Target**: TBD
**Trigger**: When event system prioritised.
**Reason**: Plan 22 S5 deferred — Librarian has no handle_event method. Need to implement episodic event consumer pattern for librarian to subscribe to task events (created, updated, completed) for knowledge graph updates.

---

## DEBT-7 — TUI cookie auth for agent SSE stream

**Severity**: Low
**Priority**: Low
**Status**: Identified
**Target**: TBD
**Trigger**: When TUI framework (textual) cookie attachment capability is investigated.
**Reason**: Plan 23 S8 requires TUI tasks panel to include session cookie in SSE request headers for agent task streaming. Textual framework may not support cookie attachment in HTTP requests. If textual cannot attach cookie, stream consumption is deferred until framework supports it or alternative auth mechanism is implemented.

---

## DEBT-8 — Web UI consumer for agent SSE stream

**Severity**: Low
**Priority**: Low
**Status**: Identified
**Target**: TBD
**Trigger**: When Web UI implementation is prioritised.
**Reason**: Plan 23 S7 created agent SSE endpoints (/api/agent/tasks/{task_id}/stream) but deferred web UI consumer implementation. Web UI needs to consume agent task streams for real-time progress display.

---

## DEBT-9 — Cross-task persistent graph memory

**Severity**: Medium
**Priority**: Medium
**Status**: Identified
**Target**: TBD
**Trigger**: When graph memory prioritised.
**Reason**: Plan 24 S5 implemented TaskGraphCache as per-task ephemeral memory using SQLite :memory: database by default for per-task isolation. Cross-task persistent graph memory functionality is already available via the db_path parameter (file-backed SQLite mode), but was not integrated into the agent system. Future work would integrate file-backed mode for persistent knowledge accumulation across task boundaries.

---

## DEBT-11 — Workflow compliance verification system

**Severity**: Medium
**Priority**: High
**Status**: In Progress
**Target**: Plan 28
**Trigger**: Implementation of compliance artifacts in workflow files.
**Reason**: The workflow needs verifiable artifacts to prevent scope drift and ensure exact procedure compliance. This debt tracks the implementation of: Executor Manifest in plan files, execution trace logging, execution attestation production, `verify_execution.py` script, and hook scripts for real-time enforcement. Once implemented and tested on Plan 28, this debt is resolved.
