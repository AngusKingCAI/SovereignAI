# Plan 5 — Scan 5 (First Whole-Repo Scan)

**Special plan**: Scan prompt — mechanical verification of the full Plans 1-4 batch. No new features. No new architecture. Fixes only. If any scan reveals a structural problem requiring design decisions, STOP and report — do not guess. Skips Round Table review (per AI_HANDOFF.md scan-prompt exemption).

Depends on: prompt-4
Vision principles: none (mechanical scan — no architectural impact)
Open questions resolved: none

---

## S0 — Opening

**S0.1** — Run `/open` workflow from `.devin/workflows/open.md`. Verify `prompt-4` tag exists on origin. Confirm clean working copy on `main`. Activate venv (OR45).

**S0.2** — Read `AGENTS.md` in full. Note OR2 (file-scoped mypy except at scan prompts — full repo mypy here), OR3 (run scan tools ONE AT A TIME), OR22 always-on subset.

**S0.3** — No new rules this plan. Proceed to S1.

---

## S1 — Run All Scan Tools (Full Repo, One at a Time per OR3)

Per `/scan` workflow step 1. Run each tool separately — parallel execution corrupts output streams (OR3).

### S1.1 — Full test suite

```bash
.venv/Scripts/python.exe -m pytest tests/ -vvv
```

Expected: 107 tests passed (per PLANS.md baseline). If count differs, update PLANS.md baseline with actual number + reason.

If any test fails, STOP. Do not fix — report to the Architect.

### S1.2 — Ruff (full repo)

```bash
.venv/Scripts/ruff.exe check . 2>&1 | tail -n 3
```

Expected: 0 errors. If errors, STOP.

### S1.3 — Mypy (full repo — scan prompt per OR2)

```bash
.venv/Scripts/mypy.exe . --ignore-missing-imports 2>&1 | tail -n 5
```

Expected: 0 errors (or known accepted warnings). This is the first full-repo mypy run. If errors, document each one and fix mechanically (type annotations, `type: ignore` with comment). If any error requires a design decision, STOP and report.

### S1.4 — Bandit

```bash
.venv/Scripts/bandit.exe -r . -ll --exclude .venv,venv,env,.git,node_modules,__pycache__,build,dist,.tox,.eggs,.pytest_cache 2>&1 | tail -n 5
```

Expected: 0 findings above Low. Low findings (B101: assert_used in tests) are expected — count them per OR4 (filter: `>> Issue: [B`). If new Medium/High findings, STOP.

**Note**: Bandit baseline is stale (still says 49 Low from Plan 1). With 107 tests, the actual count will be higher. Record the actual count and update PLANS.md baseline.

### S1.5 — pip-audit

```bash
.venv/Scripts/pip-audit.exe --strict --requirement txt/requirements.txt 2>&1 | tail -n 5
```

Expected: 0 CVEs. If CVEs, STOP.

### S1.6 — Vulture

```bash
.venv/Scripts/vulture.exe . --min-confidence 80 --exclude .venv,venv,env,.git,node_modules,__pycache__,build,dist,.tox,.eggs,.pytest_cache,.mypy_cache,.ruff_cache,htmlcov 2>&1 | tail -n 5
```

Compare against `txt/vulture-whitelist.txt`. If new findings, STOP.

### S1.7 — detect-secrets

```bash
.venv/Scripts/detect-secrets.exe scan --baseline txt/.secrets.baseline
```

If exit code != 0, STOP.

### S1.8 — Custom AR checks (per /close step 8)

Run each check separately:

- No globals in `sovereignai/`: `grep -rn "^global " sovereignai/ 2>/dev/null || echo "No globals found"`
- Constructor arg cap (15) in `sovereignai/`: scan all `__init__` methods
- No context bags in `sovereignai/`: check for `**kwargs` or untyped dict params
- Docstring verb-first, >=10 words on first line: scan all `def` in `sovereignai/`
- No hard-coded component names in `web/`, `cli/`, `tui/`, `phone/`: (currently empty, skip)
- UI changes do not touch `sovereignai/`: `git diff --name-only HEAD~4 | grep "^sovereignai/" | grep -E "^(web|cli|tui|phone)/"` (should be empty)

If any check fails, STOP.

---

## S2 — Mechanical Fixes from Kimi Scan Report

The following 26 issues are mechanical fixes — no design decisions required. Apply them in the order listed. After each file edit, run `/verify`.

### S2.1 — Fix PH1: PLANS.md Baseline Reconciliation Note

**File**: `PLANS.md`
**Change**: Correct Plan 1 reconciliation note from '23 tests' to '22 tests'.

Old:
```
**Plan 1**: First code plan — established test baseline at 23 tests and static analysis baselines for all tools. Delta from expected: +1 test (di_container thread-safety test added per Finding 3).
```
New:
```
**Plan 1**: First code plan — established test baseline at 22 tests and static analysis baselines for all tools. Delta from expected: 0 tests (exactly as planned).
```

### S2.2 - Fix PH2: AGENTS.md AR4 - Remove dependency-injector reference

**File**: AGENTS.md
**Change**: Rewrite AR4 to remove dependency-injector reference and clarify the hand-rolled DI container.

Old (first sentence of AR4 body):
All shared state is managed through the `dependency-injector` DI container defined in `shared/container.py` - the single wiring point for the entire application.

New:
All shared state is managed through the hand-rolled DI container defined in `shared/container.py` - the single wiring point for the entire application. The container is a passive typed registry (per A8): no @inject decorators, no auto-wiring, no runtime magic. Components declare their dependencies as constructor arguments and receive them via explicit injection from the Composition Root - they never instantiate dependencies themselves or reach into global scope.

Also update the shared/ directory description in AR4:
Old:
The `shared/` directory holds contracts, interfaces, and the DI container definition only - no runtime state outside the container.

New:
The `shared/` directory holds contracts, interfaces, the DI container definition, and the singleton DI container instance. The container mutable state (_instances, _factories dicts) is runtime state managed by the container itself - no other runtime state lives in shared/.

Note: This resolves the DEBT.md item Deferred: AR4 amendment - remove dependency-injector reference. After this edit, add Resolved at: prompt-5 to that DEBT entry.

### S2.3 - Fix PH3: EventBus - Release lock before calling subscribers

**File**: sovereignai/shared/event_bus.py
**Change**: Copy subscriber list under lock, release lock, then iterate and call subscribers.

Old publish() method body (inside with block):
        with self._lock:
            subscribers = list(self._subscribers.get(event.channel, []))
            for subscriber in subscribers:
                try:
                    subscriber(event)
                except Exception as exc:
                    ...

New publish() method body:
        with self._lock:
            subscribers = list(self._subscribers.get(event.channel, []))
        for subscriber in subscribers:
            try:
                subscriber(event)
            except Exception as exc:
                ...

Also update the docstring to add: The subscriber list is copied under the lock, then the lock is released before calling subscribers. A slow subscriber does not block other publishers or subscribers on other channels.

### S2.4 - Fix NH1: TaskStateMachine - Use RLock to prevent nested lock deadlock

**File**: sovereignai/shared/task_state_machine.py
**Change**: Replace threading.Lock with threading.RLock in TaskStateMachine.

Old:
from threading import Lock

New:
from threading import RLock

Old:
        self._lock = Lock()

New:
        self._lock = RLock()

Rationale: TaskStateMachine._publish() calls bus.publish() from within its own lock. With the EventBus fix in S2.3, bus.publish() no longer holds its lock during callbacks, so the deadlock risk is reduced. However, RLock is still safer: if a subscriber (e.g., a Manager) calls back into TaskStateMachine (e.g., transition()), the same thread can re-acquire the lock. This is a standard pattern for nested locking scenarios.

### S2.5 - Fix PH4: test_composition_root.py - Make smoke test portable

**File**: tests/test_composition_root.py
**Change**: Use sys.executable and relative path for the smoke test.

Add imports at top of file:
import sys
from pathlib import Path

Old test_main_smoke_test():
def test_main_smoke_test() -> None:
    result = subprocess.run(
        [".venv/Scripts/python.exe", "-m", "sovereignai.main"],
        cwd="c:\SovereignAI",
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "Composition root built successfully" in result.stdout

New test_main_smoke_test():
def test_main_smoke_test() -> None:
    project_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "-m", "sovereignai.main"],
        cwd=str(project_root),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "Composition root built successfully" in result.stdout

### S2.6 - Fix PM3: DIContainer - Release lock before calling factory

**File**: sovereignai/shared/container.py
**Change**: Copy factory reference under lock, release lock, then call.

Old retrieve() method (factory call inside lock):
        with self._lock:
            if interface in self._instances:
                return cast(T, self._instances[interface])
            if interface in self._factories:
                return cast(T, self._factories[interface]())
            raise KeyError(...)

New retrieve() method (factory call outside lock):
        with self._lock:
            if interface in self._instances:
                return cast(T, self._instances[interface])
            if interface in self._factories:
                factory = self._factories[interface]
            else:
                raise KeyError(...)
        # Call factory outside the lock so slow factories do not block
        # other retrieve() or register() calls.
        return cast(T, factory())

### S2.7 - Fix PM4: CapabilityGraph - Move sort to find_providers()

**File**: sovereignai/shared/capability_graph.py
**Change**: Remove sort from register(), sort in find_providers() instead.

Remove this line from register():
                self._index[key].sort(key=lambda x: -x[1].priority)

In find_providers(), change:
            return tuple(self._index.get(key, []))

To:
            providers = list(self._index.get(key, []))
        providers.sort(key=lambda x: -x[1].priority)
        return tuple(providers)

### S2.8 - Fix PM5: CapabilityGraph - Handle duplicate component_id registrations

**File**: sovereignai/shared/capability_graph.py
**Change**: Clean up old capabilities before registering new ones.

Add before self._manifests[manifest.component_id] = manifest in register():
            # Remove old capabilities if this component was previously registered
            old_manifest = self._manifests.get(manifest.component_id)
            if old_manifest is not None:
                for cap in old_manifest.provides:
                    key = (cap.category, cap.name)
                    if key in self._index:
                        self._index[key] = [
                            entry for entry in self._index[key]
                            if entry[0] != manifest.component_id
                        ]
                        if not self._index[key]:
                            del self._index[key]
                self._trace.emit(
                    component="CapabilityGraph",
                    level=TraceLevel.WARN,
                    message=f"Re-registering {manifest.component_id} - old capabilities removed",
                )

### S2.9 - Fix PM6: DI container thread-safety test - Test concurrent read/write on different types

**File**: tests/test_di_container.py
**Change**: Rewrite test to have threads register different interfaces and others retrieve them simultaneously.

Replace the existing test_di_container_thread_safety with a test that:
1. Pre-registers one interface (InterfaceA)
2. Spawns threads that register InterfaceB/InterfaceC while retrieving InterfaceA/InterfaceB/InterfaceC
3. Collects errors in a thread-safe list
4. Asserts no errors and all interfaces are retrievable after join

See the full test code in the original scan report for the exact implementation.

### S2.10 - Fix PM7: test_manifest_parser.py - Move assertions outside pytest.raises

**File**: tests/test_manifest_parser.py
**Change**: Move all assert ... in str(exc_info.value) lines outside the with pytest.raises(...) blocks.

Pattern: Change from:
    with pytest.raises(ManifestParseError) as exc_info:
        parse_manifest(manifest_file)
        assert "something" in str(exc_info.value)

To:
    with pytest.raises(ManifestParseError) as exc_info:
        parse_manifest(manifest_file)
    assert "something" in str(exc_info.value)

Apply to all affected tests.

### S2.11 - Fix PM9: Add coverage baseline

**File**: PLANS.md
**Change**: After running S7 (coverage measurement), add the coverage percentage to the Static Analysis Baseline table.

New row in Static Analysis Baseline:
| **Coverage** | {percentage}% | Plan 5 /close | First measurement at scan prompt |

### S2.12 - Fix L1-L2: TraceEmitter performance improvements

**File**: sovereignai/shared/trace_emitter.py
**Change**: Two mechanical performance fixes.

Fix 1: Add O(1) level priority mapping at module level (after TraceLevel class):
TRACE_LEVEL_PRIORITY: dict[TraceLevel, int] = {
    TraceLevel.TRACE: 0,
    TraceLevel.DEBUG: 1,
    TraceLevel.INFO: 2,
    TraceLevel.WARN: 3,
    TraceLevel.ERROR: 4,
}

Replace list(TraceLevel).index() calls with TRACE_LEVEL_PRIORITY lookups in get_events().

Fix 2: Release lock before copying events list in get_events():
        with self._lock:
            events = list(self._events)
        if level is not None:
            ...
        if component is not None:
            ...
        return events

### S2.13 - Fix L4: LANDMINES.md placeholder entries

**File**: LANDMINES.md
**Change**: For each inherited landmine (L1-L9, L11, L12, L17), update the trigger line.

Change from:
Specific SovereignAI trigger TBD.

To:
Not yet triggered in SovereignAI - retained for diagnostic context.

For L24-L31 (which HAVE triggered in SovereignAI), keep their specific triggers as-is.

### S2.14 - Fix L5: Add tests/__init__.py

**File**: tests/__init__.py (new)
**Content**:
"""Test package for SovereignAI."""

### S2.15 - Fix L8: Add tie-breaking test for CapabilityGraph

**File**: tests/test_capability_graph.py
**Add new test**: test_register_equal_priority_stable_sort

Register two providers with the same priority (5). Verify stable sort preserves registration order (FirstAdapter before SecondAdapter).

### S2.16 - Fix L9: main.py docstring in if block

**File**: sovereignai/main.py
**Change**: Remove the orphaned docstring string literal from the if-block. The module-level docstring already explains what main.py does.

Remove the triple-quoted string between if __name__ == '__main__': and the first import inside the block.

### S2.17 - Fix L10: test_composition_root.py module-level imports (ACCEPTED)

**File**: tests/test_composition_root.py
**Decision**: SKIP this fix. The module-level import of build_container is appropriate for a composition-root test file where all 21 tests verify the container wiring. If build_container fails to import, the system is fundamentally broken and all tests should fail.

Document this acceptance in the plan closing summary.

### S2.18 - Fix L11: pyproject.toml missing pythonpath

**File**: pyproject.toml
**Change**: Add pythonpath to pytest config.

Find [tool.pytest.ini_options] section and add:
pythonpath = ["."]

If the section does not exist, add it.

### S2.19 - Fix L12: OR37 enforcement

**File**: AGENTS.md
**Change**: Add a verification step to OR37.

Add after 'This reduces 6 Executor actions...':
Verification: After batching, verify that each tool output was captured. If a tool produced zero output (e.g., ruff found no errors), confirm with echo "ruff: $?" that the exit code was 0. A missing tool output with exit code 0 is success; a missing tool output with non-zero exit code is a failure that must be re-run individually.

### S2.20 - Fix L13: Add EventBus thread-safety test

**File**: tests/test_event_bus.py
**Add new test**: test_concurrent_publish_and_subscribe

Spawn 5 threads, each publishing 10 events to the same channel. A single subscriber appends to a thread-safe list. Assert 50 events received after join.

### S2.21 - Fix NM2: CapabilityGraph.find_providers explicit list copy

**Already fixed in S2.7** - the new find_providers() uses list(self._index.get(key, [])) which creates an explicit copy. No additional change needed.

### S2.22 - Fix NM3: test_q26 restrict ast.walk to function body

**File**: tests/test_composition_root.py
**Change**: Replace ast.walk(build_container_func) with walk restricted to the function body.

Change from:
    for node in ast.walk(build_container_func):

To:
    for stmt in build_container_func.body:
        for node in ast.walk(stmt):

### S2.23 - Fix NM4: test_auth.py - Use mock instead of private state access

**File**: tests/test_auth.py
**Change**: Use unittest.mock.patch to manipulate time instead of mutating auth._tokens.

Add import:
from unittest.mock import patch

In test_validate_expired_token_raises_and_deleted, replace the direct mutation of auth._tokens with:
    with patch("sovereignai.shared.auth.now_utc") as mock_now:
        mock_now.return_value = token.expires_at + timedelta(hours=1)
        with pytest.raises(AuthError, match="Session token expired"):
            auth.validate(token.token)

### S2.24 - Fix NM5: Verify main.py integrity

**File**: sovereignai/main.py
**Action**: Read the file. If build_container() appears twice (corruption), fix by removing the duplicate.

Verification: Run python -c 'import ast; ast.parse(open(\'sovereignai/main.py\').read())' to confirm the file parses correctly.

### S2.25 - Fix L14-L17: Minor issues

**L14 (CapabilityAPI.submit_task defensive copy)**:
File: sovereignai/shared/capability_api.py
Change: After checking if not providers, assign provider_id, declaration = providers[0] before creating the Task. Use declaration.version instead of providers[0][1].version.

**L15 (Inconsistent test type hints)**: Add -> None to all test functions in tests/test_event_bus.py, tests/test_trace_emitter.py, tests/test_di_container.py that lack them.

**L16 (AR7 test uses CWD-relative paths)**: Fix tests/test_ar7_no_core_imports_in_ui.py:
Change: ui_path = Path(ui_dir) to ui_path = Path(__file__).resolve().parent.parent / ui_dir

**L17 (DECISIONS.md not verified)**: Read DECISIONS.md. Verify D4 exists (Q26 resolution). If not, add it.

---

## S3 - Issues Deferred to Plan 6 (Design Decisions Required)

The following 6 issues require architectural design decisions and are deferred to Plan 6 (or a dedicated plan). Do NOT fix them in Scan 5. Document each deferral in DEBT.md with trigger condition and target plan.

### D1: NH2 - Session tokens stored in plaintext (Security)

Issue: AuthMiddleware._tokens stores full SessionToken objects including the plaintext token string.
Options: (a) Hash tokens with HMAC/SHA-256, store only hash, (b) Encrypt tokens at rest, (c) Store only a verification hash.
Deferral reason: Security strategy decision - needs Round Table review on threat model (memory dump vs. process compromise).
Target plan: Plan 6 (security hardening) or dedicated security plan.
Trigger condition: When auth system is stable and threat model is defined.

### D2: NH3 - CapabilityAPI violates AR7 (Architectural boundary)

Issue: CapabilityAPI imports concrete TaskStateMachine instead of depending only on protocols.
Options: (a) Extend ITaskStateQuery with submit() method, (b) Create ITaskStateWriter protocol, (c) Redesign CapabilityAPI to queue tasks instead of direct submission.
Deferral reason: Protocol design decision - affects all future UI processes and task submission patterns.
Target plan: Plan 6 (protocol refinement).
Trigger condition: When UI processes begin consuming the Capability API.

### D3: PM8 - EventBus has no unsubscribe() (API design)

Issue: No way to remove subscribers. Memory leak for long-running systems.
Options: (a) unsubscribe(channel, subscriber) by callable identity, (b) unsubscribe by registration handle, (c) Document permanent subscriptions as design choice.
Deferral reason: API design decision - affects all event bus consumers.
Target plan: Plan 6 (API design).
Trigger condition: When dynamic UI components or Managers need to subscribe/unsubscribe at runtime.

### D4: NM1 - RoutingEngine.route() side effects (Recovery semantics)

Issue: route() calls try_recover() as a side effect of reading. Query operation mutates state.
Options: (a) Separate recovery from routing (explicit recover() call), (b) Router queries status without recovery, (c) Document recovery-as-side-effect as intentional.
Deferral reason: Recovery semantics design decision - affects system resilience strategy.
Target plan: Plan 6 (routing design).
Trigger condition: When automated recovery policy is defined.

### D5: L6 - Manifest parser no semver validation (Validation strategy)

Issue: Manifest parser accepts any string for version fields.
Options: (a) Regex validation, (b) packaging library dependency, (c) Custom validator.
Deferral reason: Validation strategy decision - adding a dependency (packaging) vs. custom regex has trade-offs.
Target plan: Plan 6 (validation strategy).
Trigger condition: When first incompatible version conflict occurs.

### D6: L7 - No component_id/directory validation (Directory structure)

Issue: Parser does not validate component_id matches directory name.
Options: (a) Enforce match at parse time, (b) Warn but allow mismatch, (c) Use directory name as canonical component_id.
Deferral reason: Directory structure policy decision.
Target plan: Plan 6 (directory structure policy).
Trigger condition: When first manifest directory mismatch causes debugging confusion.

---

## S4 - Scan LANDMINES.md

For any landmine without a corresponding rule in AGENTS.md, propose the missing rule via C9.

Current landmine-to-rule table in AGENTS.md covers L1-L9, L11, L12, L17, L24-L31. Verify all are present.

---

## S5 - Scan CHANGELOG.md

Verify every plan in the completed batch (prompt-0 through prompt-4) has an entry. Verify the entries match the actual commits.

---

## S6 - Scan PLANS.md

Verify baselines are current after S2 fixes:
- Test baseline: 107 + any new tests from S2 fixes (e.g., S2.15 tie-breaking test, S2.20 thread-safety test, S2.9 DI test rewrite). Count actual tests after S2 and update baseline.
- Ruff: 0 errors
- Mypy: 0 errors (full repo - scan prompt)
- Bandit: actual Low count (update from stale 49)
- pip-audit: 0 CVEs
- Vulture: 0 findings
- detect-secrets: pass
- Coverage: newly added baseline from S7

Verify next-5-queue reflects actual state:
- Slot 1: Scan 5 (this plan) - Active
- Slot 2: Plan 6 - Pending Scan 5
- Slot 3: Plan 7 - Pending Plan 6
- Slot 4: Plan 8 - Pending Plan 7
- Slot 5: Plan 9 - Pending Plan 8

---

## S7 - Verify Coverage

```bash
.venv/Scripts/python.exe -m pytest tests/ --cov=. --cov-report=term 2>&1 | tail -n 10
```

Verify coverage has not dropped >5% from baseline. Since this is the first coverage measurement, record the baseline in PLANS.md.

---

## S8 - Audit Against Vision Principles

For each of the 14 principles in project-vision-Rev5.md, verify the codebase complies. If any principle is violated, STOP - architectural violations require a regular plan with Round Table review, not a scan fix.

Key checks:
- P1 (sacred core): Verify only the 12 Core Scope components are in sovereignai/shared/ - no business logic
- P7 (modular core): Verify fault isolation - kill any skill -> system stays up (conceptual check, not runtime)
- P8 (UIs separate processes): Verify web/, cli/, tui/, phone/ are empty (no UI code yet)
- P9 (observability): Verify every component emits traces via TraceEmitter
- P10 (no silent failures): Verify EventBus catches subscriber exceptions and logs at ERROR
- P11 (DI, no globals): Verify no global keyword in sovereignai/
- P12 (docstrings): Verify every def has a docstring with verb-first >=10 words first line

---

## S9 - Audit Against Success Criteria

For each of the 40 success criteria in project-vision-Rev5.md, verify the codebase passes. If any criterion fails, STOP.

Key criteria to verify:
- Criterion 4 (acyclic dependency test): Verify import graph has no cycles
- Criterion 5 (no globals): grep -rn "^global " sovereignai/ returns zero matches
- Criterion 6 (constructor arg cap): No class in sovereignai/ has >15 constructor args
- Criterion 7 (no context bags): No class accepts **kwargs or untyped dict as constructor arg

---

## S10 - Review DEBT.md

For each deferred item, check if its trigger condition has been met. If yes, flag for the next plan.

Current DEBT items to review:
- AR4 amendment (remove dependency-injector reference) - RESOLVED in S2.2. Add Resolved at: prompt-5.
- Security Guard implementation - trigger: post Plan 4 (flag for Plans 6-9 batch)
- Cross-platform packaging - trigger: when core is stable
- Model loading/unloading - trigger: when local model adapters are wired
- Self-correction/learning loops - trigger: when skill framework is stable
- Relay server E2EE - trigger: when Plan 4 placeholder is merged (flag for dedicated plan)
- Durable persistence - trigger: when Plan 3 in-memory store is stable (flag for Plans 6-9 batch)
- Full Q8 versioning - trigger: when second adapter version is needed
- Memory abstraction implementation - trigger: when Librarian Registry is needed (post Plan 4) (flag)
- Circuit breaker auto-recovery heartbeat - trigger: when periodic heartbeat component exists
- Task TTL/eviction strategy - trigger: when worker dispatch pipeline is wired
- DAGSpec extension for composite skills - trigger: when composite task execution is implemented

New deferrals from S3: Add D1-D6 to DEBT.md with target plan = Plan 6 and appropriate trigger conditions.

---

## S11 - Audit Open Questions

Check if any open questions from project-vision-Rev5.md have been implicitly resolved by recent plans. If yes, move to Resolved Open Questions with a note.

Currently resolved: Q5-Q7, Q10-Q12, Q15-Q30, Q26 (confirmed at Plan 4 /close)
Still open: Q1 (adapter contract - resolved by Plan 2), Q2 (skill discovery - resolved by Plan 2), Q3 (memory abstraction - interface defined Plan 3), Q4 (routing - resolved by Plan 3), Q8 (versioning MVP - resolved by Plan 2), Q9 (test strategy - resolved by Plan 1), Q13 (learning - deferred), Q14 (persistence - in-memory Plan 3), Q31 (packaging - deferred), Q32 (DEBT register - resolved by Plan 1)

Verify the vision doc open questions section is updated to reflect these resolutions.

---

## S12 - Final Summary

```
=== SCAN COMPLETE (prompt-5) ===

Tools run:
- pytest: {count} tests, {count} passed
- ruff: {count} findings
- mypy: {count} findings (full repo)
- bandit: {count} findings (Low only, B101 assert_used)
- pip-audit: {count} CVEs
- vulture: {count} findings ({count} new)
- custom AR checks: all pass / {count} failures
- coverage: {percentage}%

Mechanical fixes applied (S2):
- S2.1: PLANS.md baseline reconciliation note corrected
- S2.2: AGENTS.md AR4 dependency-injector reference removed
- S2.3: EventBus lock released before subscriber callbacks
- S2.4: TaskStateMachine uses RLock for nested locking safety
- S2.5: test_main_smoke_test made portable (sys.executable, relative paths)
- S2.6: DIContainer retrieves factory outside lock
- S2.7: CapabilityGraph sorts in find_providers() instead of register()
- S2.8: CapabilityGraph handles duplicate component_id registrations
- S2.9: DI container thread-safety test tests concurrent read/write on different types
- S2.10: test_manifest_parser.py assertions moved outside pytest.raises blocks
- S2.11: Coverage baseline added to PLANS.md
- S2.12: TraceEmitter performance improved (O(1) level comparison, lock released before copy)
- S2.13: LANDMINES.md placeholder entries updated
- S2.14: tests/__init__.py added
- S2.15: CapabilityGraph tie-breaking test added
- S2.16: main.py orphaned docstring removed
- S2.17: L10 accepted - module-level import justified for composition-root test file
- S2.18: pyproject.toml pythonpath added
- S2.19: OR37 verification step added
- S2.20: EventBus thread-safety test added
- S2.22: test_q26 AST walk restricted to function body
- S2.23: test_auth.py uses mock instead of private state access
- S2.24: main.py integrity verified
- S2.25: Minor fixes (L14-L17)

Design decisions deferred to Plan 6 (S3):
- D1: Session token plaintext storage (security strategy)
- D2: CapabilityAPI AR7 violation (protocol design)
- D3: EventBus unsubscribe() (API design)
- D4: RoutingEngine side effects (recovery semantics)
- D5: Manifest semver validation (validation strategy)
- D6: component_id/directory validation (directory structure)

Vision principle audit: 14/14 pass / {count} violations
Success criteria audit: 40/40 pass / {count} failures

DEBT.md review: {count} items reviewed, {count} flagged, {count} resolved
Open questions audit: {count} resolved, {count} remain

=== REMINDER ===
Copy the chat log to logs/execution-log-prompt-5.md before closing this session.
```

---

## S13 - Commit, Tag, Push

1. Stage any mechanical fixes:
   ```bash
   git add -A
   git status -s | tail -n 20
   ```

2. Commit (if fixes were applied):
   ```bash
   git commit -m "prompt-5: Scan 5 - mechanical fixes" -m "Full-repo scan of Plans 1-4 batch. Fixes applied: {list}." -m "Baselines verified: {count} tests, 0 ruff errors, 0 mypy errors, {count} bandit Low, 0 CVEs, 0 vulture findings, {percentage}% coverage."
   ```

3. Tag:
   ```bash
   git tag prompt-5
   git tag --list prompt-5
   ```

4. Push:
   ```bash
   git push origin main
   git push origin prompt-5
   ```

5. Verify tag on origin:
   ```bash
   git ls-remote --tags origin | grep "prompt-5"
   ```

---

## Closing

Run `/close` workflow from `.devin/workflows/close.md`. Run all 21 steps.

Expected results:
- Tests: {count} passed (107 + new tests from S2 fixes)
- Ruff: 0 errors
- Mypy: 0 errors (full repo - scan prompt)
- Bandit: {count} Low findings (B101 assert_used in tests - expected, updated baseline)
- pip-audit: 0 CVEs
- Vulture: 0 findings
- Detect-secrets: pass
- Coverage: {percentage}% (first measurement, recorded as baseline)

Reminder: Step 21 (kill bash) mandatory.

---

## Files WILL Create

- tests/__init__.py (S2.14)
- logs/execution-log-prompt-5.md (created by /close step 14)

## Files WILL Edit

- PLANS.md (S2.1 baseline fix, S2.11 coverage baseline, S6 queue update, prompt-5 row)
- AGENTS.md (S2.2 AR4 fix, S2.19 OR37 fix)
- CHANGELOG.md (append prompt-5 entry)
- LANDMINES.md (S2.13 placeholder updates)
- DEBT.md (S10 review, S3 deferrals D1-D6, mark AR4 amendment resolved)
- sovereignai/shared/event_bus.py (S2.3 lock release)
- sovereignai/shared/task_state_machine.py (S2.4 RLock)
- sovereignai/shared/container.py (S2.6 factory outside lock)
- sovereignai/shared/capability_graph.py (S2.7 sort move, S2.8 duplicate cleanup)
- sovereignai/shared/trace_emitter.py (S2.12 performance)
- sovereignai/shared/capability_api.py (S2.25 L14 defensive copy)
- sovereignai/main.py (S2.16 remove orphaned docstring, S2.24 verify integrity)
- tests/test_composition_root.py (S2.5 portable smoke test, S2.22 AST walk fix)
- tests/test_di_container.py (S2.9 thread-safety test rewrite)
- tests/test_manifest_parser.py (S2.10 assertion placement)
- tests/test_capability_graph.py (S2.15 tie-breaking test)
- tests/test_event_bus.py (S2.20 thread-safety test)
- tests/test_auth.py (S2.23 mock-based expiration test)
- tests/test_ar7_no_core_imports_in_ui.py (S2.25 L16 path fix)
- pyproject.toml (S2.18 pythonpath)
- tests/test_event_bus.py, tests/test_trace_emitter.py, tests/test_di_container.py (S2.25 L15 type hints)
- DECISIONS.md (S2.25 L17 verify D4)

## Files WILL NOT Edit

- AI_HANDOFF.md (no changes)
- .devin/workflows/*.md (no changes - S2.19 updates AGENTS.md, not workflow files)
- documents/* (archived - do not touch)
- prompts/* (no changes to existing plan files)
- project-vision-Rev5.md (locked - but open questions section may be crossed off per S11)

---

*Plan 5 - Scan 5. Rev2. Architect draft. Skips Round Table review per AI_HANDOFF.md scan-prompt exemption (mechanical verification, no architectural decisions).*
