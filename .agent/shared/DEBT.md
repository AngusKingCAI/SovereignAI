# DEBT.md — SovereignAI Deferred Items

Open items only. Resolved items → CHANGELOG.md.

---

## Open Items

| ID | Item | Severity | Priority | Status | Target | Trigger |
|----|------|----------|----------|--------|--------|---------|
| DEBT-4 | UI implementations (web, tui) | Low | Low | Identified | TBD | UI implementation prioritised |
| DEBT-5 | P4 compliance test isolation | Low | Low | Identified | TBD | Test infrastructure improvement |
| DEBT-6 | Librarian.handle_event method + episodic event consumer | Medium | Medium | Identified | TBD | Event system prioritised |
| DEBT-7 | TUI cookie auth for agent SSE stream | Low | Low | Identified | TBD | TUI framework investigation |
| DEBT-8 | Web UI consumer for agent SSE stream | Low | Low | Identified | TBD | Web UI implementation prioritised |
| DEBT-9 | Cross-task persistent graph memory | Medium | Medium | Identified | TBD | Graph memory prioritised |

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

## DEBT-4 — UI implementations (cli, phone)

**Severity**: Low
**Priority**: Low
**Status**: Identified
**Target**: TBD
**Trigger**: When UI implementation is prioritised.
**Reason**: UI directories app/web and app/tui exist with main.py implementations (completed in Plan 25.2), but app/cli and app/phone only have .gitkeep placeholders. Tests for AR7 (no core imports in UI) skip because there are no actual .py files in cli/phone directories to scan.

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
**Reason**: Plan 24 S5 implemented TaskGraphCache as per-task ephemeral memory using SQLite :memory: database. Cross-task persistent graph memory was deferred to avoid scope creep. Future implementation would use file-backed SQLite to maintain graph state across task boundaries for persistent knowledge accumulation.
