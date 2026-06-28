# SovereignAI Codebase Re-Scan Report

**Date**: 2026-06-28
**Scope**: Full repo review after Plans 1-4 completion (prompt-4 tag)
**Method**: Static analysis of all governance docs, source code, tests, workflows
**Previous scan**: 2026-06-28 (pre-Plan 3)

---

## Executive Summary

| Category | Count |
|----------|-------|
| **FIXED** (resolved since last scan) | 3 |
| **PERSISTENT HIGH** | 4 |
| **PERSISTENT MEDIUM** | 8 |
| **PERSISTENT LOW** | 12 |
| **NEW HIGH** | 3 |
| **NEW MEDIUM** | 4 |
| **NEW LOW** | 3 |
| **Total** | **37** |

**Key finding**: 3 new HIGH severity issues discovered, including a nested lock deadlock risk and an AR7 architectural boundary violation.

---

## FIXED ISSUES (3)

### F1: PLANS.md state contradiction — RESOLVED
**Previous**: Plan 2 was simultaneously "awaiting execution", "completed", and "▶️ Active".
**Current**: Active Plan = "None — awaiting next plan". Completed Prompts has prompt-0 through prompt-4. Next-5-Queue shows Scan 5 as ⏳ Pending.
**Status**: ✅ Fixed

### F2: CHANGELOG.md duplicate prompt-0.4 — RESOLVED
**Previous**: Two merged/duplicate prompt-0.4 entries.
**Current**: Single clean prompt-0.4 entry.
**Status**: ✅ Fixed

### F3: OR22 referenced non-existent AR16 — RESOLVED
**Previous**: OR22's always-on subset included AR16 (circuit breaker) which didn't exist.
**Current**: AR16 is fully implemented in lifecycle_manager.py with 50 errors/10s threshold, auto-recovery via try_recover(), and ERROR trace emission.
**Status**: ✅ Fixed

---

## PERSISTENT HIGH ISSUES (4)

### PH1: PLANS.md Baseline Reconciliation Note stale
**Location**: PLANS.md — Baseline Reconciliation Notes
**Issue**: Plan 1 reconciliation still says "established test baseline at 23 tests" but actual was 22 (confirmed by CHANGELOG and Completed Prompts table). The Test Baseline now shows 107 (Plan 4), making the old reconciliation note doubly stale.
**Evidence**: Reconciliation: "Plan 1: First code plan — established test baseline at 23 tests". CHANGELOG Plan 1: "Test baseline established at 22 tests exactly as planned."
**Impact**: Stale documentation. Doesn't affect current execution but creates confusion for anyone reading historical baselines.
**Fix**: Update reconciliation note to "22 tests".

### PH2: AGENTS.md AR4 — stale dependency-injector reference
**Location**: AGENTS.md — AR4
**Issue**: AR4 still says "managed through the dependency-injector DI container defined in shared/container.py". The container is hand-rolled (DIContainer class with dicts). DEBT.md has a deferred item for this but AGENTS.md was never updated across 4 plans.
**Evidence**: AR4 text vs. container.py implementation. DEBT.md: "Deferred: AR4 amendment — remove dependency-injector reference".
**Impact**: Executor confusion at S0.2. Could cause incorrect design decisions in Plan 5+.
**Fix**: Rewrite AR4 to remove dependency-injector reference. The container is a hand-rolled passive registry per A8.

### PH3: EventBus.publish() holds global lock during ALL subscriber callbacks
**Location**: sovereignai/shared/event_bus.py — publish() method
**Issue**: publish() acquires self._lock and holds it for the entire duration of iterating over subscribers AND calling their callbacks. A slow subscriber blocks the entire event bus across all channels. **Worsened**: TaskStateMachine._publish() calls bus.publish() from within its own lock — nested locks create deadlock risk if a subscriber calls back into the state machine.
**Evidence**:
```python
with self._lock:  # EventBus lock
    subscribers = list(...)
    for subscriber in subscribers:
        subscriber(event)  # Lock held during callback
```
TaskStateMachine.submit():
```python
with self._lock:  # TaskStateMachine lock
    ...
    self._publish(...)  # Calls bus.publish() → acquires EventBus lock
```
**Impact**: (1) Slow subscriber blocks entire system. (2) Deadlock risk: Thread A holds TaskStateMachine lock, wants EventBus lock. Thread B (subscriber) holds EventBus lock, wants TaskStateMachine lock.
**Fix**: Copy subscriber list under lock, release lock, then iterate. Or use per-channel locks.

### PH4: test_composition_root.py — Hard-coded Windows paths
**Location**: tests/test_composition_root.py — test_main_smoke_test()
**Issue**: Still hard-codes ".venv/Scripts/python.exe" and cwd="c:\SovereignAI". Test is not portable.
**Evidence**: Code unchanged from previous scan.
**Impact**: Test fails on any non-Windows machine or Windows machine with different path. CI incompatible.
**Fix**: Use sys.executable and pathlib.Path(__file__).resolve().parents[1] for project root.

---

## NEW HIGH ISSUES (3)

### NH1: Nested lock deadlock risk — TaskStateMachine + EventBus
**Location**: sovereignai/shared/task_state_machine.py + event_bus.py
**Issue**: TaskStateMachine._publish() calls bus.publish() from within its own self._lock. bus.publish() acquires EventBus._lock. If a subscriber (e.g., a Manager) calls back into TaskStateMachine (e.g., transition()), it tries to acquire TaskStateMachine._lock again while holding EventBus._lock. This is a classic lock-ordering deadlock.
**Evidence**:
```python
# TaskStateMachine.submit()
with self._lock:
    self._tasks[task.task_id] = task
    self._states[task.task_id] = TaskState.RECEIVED
    self._publish(task.task_id, None, TaskState.RECEIVED)  # → bus.publish()

# EventBus.publish()
with self._lock:
    for subscriber in subscribers:
        subscriber(event)  # If this calls machine.transition() → deadlock
```
**Impact**: Deadlock in production when subscribers interact with the state machine. The test_transitions_published_in_order test doesn't catch this because it uses a simple lambda subscriber.
**Fix**: Release TaskStateMachine lock before calling _publish(). Or use a reentrant lock (threading.RLock) for TaskStateMachine.

### NH2: AuthMiddleware stores session tokens in plaintext
**Location**: sovereignai/shared/auth.py — AuthMiddleware._tokens
**Issue**: AuthMiddleware._tokens stores SessionToken objects (which contain the token string) in a plain dict. While passwords are hashed with PBKDF2, the session tokens themselves are stored in memory as plaintext strings. If memory is dumped or the process is inspected, active tokens are exposed.
**Evidence**: `self._tokens: dict[str, SessionToken] = {}` — stores full SessionToken including token string.
**Impact**: Session token exposure if memory is inspected. Violates defense-in-depth. A compromised process reveals all active session tokens.
**Fix**: Store only a verification hash of the token (e.g., HMAC or SHA-256), not the token string itself. Or encrypt tokens at rest.

### NH3: CapabilityAPI violates AR7 — imports concrete TaskStateMachine
**Location**: sovereignai/shared/capability_api.py
**Issue**: CapabilityAPI.__init__ takes both task_state_query: ITaskStateQuery (protocol) AND state_machine: TaskStateMachine (concrete). The docstring acknowledges: "Write path (submit_task): uses concrete TaskStateMachine (the ITaskStateQuery protocol is query-only; submit requires the writer)." This means the Capability API — consumed by UIs per AR7 — imports a concrete core class. AR7 says "UI processes consume the Capability API only. They may not import from core internals directly." But the Capability API ITSELF imports from core internals, breaking the architectural boundary.
**Evidence**:
```python
from sovereignai.shared.task_state_machine import ITaskStateQuery, TaskStateMachine
# ...
def __init__(..., state_machine: TaskStateMachine, ...) -> None:
```
**Impact**: AR7 is violated at the API boundary. The Capability API is not a clean facade — it leaks concrete core internals. Future UI processes that import capability_api.py transitively import task_state_machine.py.
**Fix**: Extend ITaskStateQuery to include a submit() method, or create a separate ITaskStateWriter protocol. The Capability API should depend only on protocols.

---

## PERSISTENT MEDIUM ISSUES (8)

### PM1: AR4 self-contradictory about runtime state in shared/
**Location**: AGENTS.md AR4
**Issue**: AR4 says "shared/ directory holds contracts, interfaces, and the DI container definition only — no runtime state outside the container." But container.py IS runtime state (mutable _instances and _factories dicts).
**Fix**: Clarify AR4 to acknowledge that the DI container instance holds runtime state.

### PM2: Bandit baseline stale
**Location**: PLANS.md Static Analysis Baseline
**Issue**: Baseline says Bandit: 49 Low from Plan 1. Plans 2-4 added 85 more tests with asserts. The baseline was never updated. Plan 4 shows Bandit: 0 in Completed Prompts, which is inconsistent.
**Fix**: Update Bandit baseline to reflect actual count (likely 200+ Low from 107 tests).

### PM3: DIContainer.retrieve() calls factory inside lock
**Location**: sovereignai/shared/container.py
**Issue**: retrieve() calls factory while holding lock. Lower impact now (no factories in use yet), but will be a bottleneck when Worker factories are added.
**Fix**: Copy factory reference, release lock, then call factory.

### PM4: CapabilityGraph sorts on every registration
**Location**: sovereignai/shared/capability_graph.py
**Issue**: register() sorts provider list on EVERY registration. O(N² log N).
**Fix**: Sort in find_providers() or use bisect.insort.

### PM5: CapabilityGraph silently overwrites manifests
**Location**: sovereignai/shared/capability_graph.py
**Issue**: register() overwrites manifest without cleaning old capabilities from _index.
**Fix**: Check for existing component_id, remove old capabilities, then add new ones.

### PM6: DI container thread-safety test gives false confidence
**Location**: tests/test_di_container.py
**Issue**: All threads register same interface type, overwriting each other. No concurrent retrieve() tested.
**Fix**: Rewrite test with concurrent register/retrieve on different types.

### PM7: test_manifest_parser.py assertions inside pytest.raises
**Location**: tests/test_manifest_parser.py
**Issue**: Assertions on exc_info.value are inside the with block and never execute.
**Fix**: Move assertions outside the with block.

### PM8: EventBus has no unsubscribe()
**Location**: sovereignai/shared/event_bus.py
**Issue**: No unsubscribe() method. Memory leak for long-running systems.
**Fix**: Add unsubscribe() or document permanent subscriptions.

### PM9: No coverage baseline
**Location**: PLANS.md
**Issue**: No coverage % tracked. pytest-cov in dev deps but no baseline.
**Fix**: Add coverage baseline after running pytest --cov.

---

## NEW MEDIUM ISSUES (4)

### NM1: RoutingEngine.route() has side effects during read
**Location**: sovereignai/shared/routing_engine.py
**Issue**: route() calls lifecycle.try_recover(component_id) as a side effect of reading. A query operation mutates component status.
**Fix**: Separate recovery from routing. Router should query status without triggering recovery.

### NM2: CapabilityGraph.find_providers returns mutable list reference
**Location**: sovereignai/shared/capability_graph.py
**Issue**: find_providers() returns tuple(self._index.get(key, [])). The inner list is a reference to _index's mutable list. While tuple() copies the list, the objects are immutable so this is safe for now. Fragile if types change.
**Fix**: Return tuple(list(self._index.get(key, []))) to explicitly copy.

### NM3: test_q26 is fragile — ast.walk traverses entire tree
**Location**: tests/test_composition_root.py
**Issue**: test_q26_all_components_instantiated_in_main uses ast.walk() which walks ALL descendants, not just the function body. Could match names outside build_container().
**Fix**: Only walk nodes within build_container_func.body.

### NM4: test_auth.py reaches into private state
**Location**: tests/test_auth.py
**Issue**: test_validate_expired_token_raises_and_deleted directly mutates auth._tokens. Tests internal implementation, not public behavior.
**Fix**: Use time manipulation (mock now_utc or freezegun) to make token expire naturally.

### NM5: main.py may have corrupted content
**Location**: sovereignai/main.py
**Issue**: Raw fetched content appears to show build_container() body twice. Needs verification.
**Fix**: Verify file on origin. If corrupted, fix in Scan 5.

---

## PERSISTENT LOW ISSUES (12)

1. **TraceEmitter O(N×M) filtering** — list(TraceLevel).index() inside comprehension
2. **TraceEmitter copies list under lock** — get_events() blocks emit()
3. **LANDMINES.md placeholder entries** — L1-L9, L11, L12, L17 still say "TBD"
4. **No tests/__init__.py**
5. **Manifest parser no semver validation**
6. **No component_id/directory validation**
7. **test_capability_graph.py missing tie-breaking test**
8. **main.py docstring in if block**
9. **test_composition_root.py module-level imports**
10. **pyproject.toml missing pythonpath**
11. **OR37 has no enforcement mechanism**
12. **No EventBus thread-safety tests**

## NEW LOW ISSUES (3)

1. **CapabilityAPI.submit_task theoretical race** — providers[0] access after empty check
2. **Inconsistent test type hints** — some test files lack -> None on test functions
3. **AR7 test uses CWD-relative paths** — Path(ui_dir) instead of test-file-relative
4. **DECISIONS.md not verified** — need to check D4 exists

---

## Recommendations for Scan 5

### Must-fix (HIGH)
1. **Fix PH2** — Update AR4 to remove dependency-injector reference (DEBT item)
2. **Fix PH3** — Release EventBus lock before calling subscriber callbacks
3. **Fix NH1** — Address nested lock deadlock (RLock or release before publish)
4. **Fix NH2** — Hash session tokens at rest, not plaintext storage
5. **Fix NH3** — Extend ITaskStateQuery with submit() or create ITaskStateWriter protocol

### Should-fix (MEDIUM)
6. **Fix PH1** — Correct Plan 1 baseline reconciliation note
7. **Fix PH4** — Make smoke test portable
8. **Fix PM2** — Update Bandit baseline
9. **Fix PM7** — Fix test_manifest_parser.py assertion placement
10. **Fix NM3** — Fix test_q26 fragility
11. **Fix NM4** — Fix test_auth.py private state access
12. **Fix NM5** — Verify main.py integrity

### Could-fix (LOW)
13. **Fix all persistent LOW items** — Mechanical fixes, no design decisions
14. **Fix all new LOW items** — Minor improvements

---

*Re-scan performed after Plans 1-4 completion (prompt-4 tag).*
