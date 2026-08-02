# Plan 4 — Interface Layer (Auth, Capability API, Relay Placeholder, Final Wiring Audit)

**Batch**: 4 of 4 (Plans 1–4 drafted together; shared context brief at `plan-1-4-batch-Rev1-context-brief.md`)

Depends on: prompt-3
Vision principles: 1 (sacred core), 2 (pluggable), 3 (no provider lock-in), 5 (wire as you go), 7 (modular core), 8 (UIs separate processes consuming Capability API), 9 (observability), 11 (DI, no globals), 12 (plain-English docstrings), 13 (strong, robust), 14 (provenance — for external components; auth is the gate)
Open questions resolved: Q26 (Composition Root bootstrap — confirmed at this plan's `/close`)

---

## S0 — Opening

**S0.1** — Run `/open` workflow. Verify `prompt-3` on origin. Clean working copy on `main`. Activate venv (OR45).

**S0.2** — Read `AGENTS.md`. Note AR7 (UIs consume Capability API only — no imports from core internals; the static-import test in S4 enforces this), AR9 (no hard-coded component names in `web/`, `cli/`, `tui/`, `phone/` — the Capability API exposes capability-class names only).

**S0.3** — No new AR/OR rules this plan. Proceed to S1.

---

## Architectural Context

Per the locked scope adjudication:

- **A4** — Relay server deferred out of Plan 4 entirely. Plan 4 ships a local-only placeholder that returns a structured error ("remote transport not yet supported") and emits a trace — it does NOT accept connections. Remote UIs are explicitly a later deliverable.
- **A5** — Plan 4 imports ONLY `ICapabilityIndex` (from Plan 2) and `ITaskStateQuery` (from Plan 3). A static-import test in S4 confirms no transitive imports from core internals (AR7 enforcement).
- **A3** — Composition Root final wiring audit happens here. Q26 ("single file instantiates all core components explicitly") is confirmed at this plan's `/close`.

**Key constraints:**
- AR7: UI processes may not import from `orchestrator/`, `managers/`, `workers/`, `librarian/`, `adapters/`, `skills/`, or `shared/` directly. They consume the Capability API only.
- P8: UIs are separate processes connecting via local socket (or cloud relay — deferred). The Capability API is the contract they consume.
- P6: Login gate (username + password) for all UI connections. Session tokens issued on auth.

---

## S1 — Extend `shared/types.py` with Auth Types

### S1.1 — Add auth and capability-API types

Append to `sovereignai/shared/types.py`:

```python
# ============================================================================
# Auth types (used by AuthMiddleware in S2)
# ============================================================================

@dataclass(frozen=True)
class SessionToken:
    """Token issued to a UI process after successful authentication.

    Frozen so tokens cannot be mutated after issuance. The token
    carries the user it represents and an expiry timestamp. UIs attach
    the token to every request; AuthMiddleware validates it.
    """
    token: str                # opaque string (e.g. UUID4 hex)
    username: str             # who authenticated
    issued_at: datetime       # UTC, timezone-aware (per OR20)
    expires_at: datetime      # UTC, timezone-aware (per OR20)


class AuthError(Exception):
    """Raised when a request lacks a valid session token."""


# ============================================================================
# Capability API types (used by CapabilityAPI in S3)
# ============================================================================

@dataclass(frozen=True)
class CapabilityQuery:
    """Request from a UI process asking what the system can do right now.

    Frozen so queries are immutable once submitted. The Capability API
    returns a CapabilityResponse with the matching providers.
    """
    category: CapabilityCategory
    name: str


@dataclass(frozen=True)
class CapabilityResponse:
    """Reply from the Capability API listing providers for a query.

    Frozen so the response cannot be mutated after the API builds it.
    Contains only public-facing fields — never internal component
    state (AR7 enforcement).
    """
    query: CapabilityQuery
    providers: tuple[ComponentId, ...]    # component IDs that provide this capability
```

After edit, run `/verify`. Run existing tests to confirm no regressions:
```bash
.venv/Scripts/python.exe -m pytest tests/ -vvv
```

---

## S2 — Auth Middleware

### S2.1 — Create `sovereignai/shared/auth.py`

Per P6: login gate (username + password) for all UI connections. Session tokens issued on auth. Per AR4: auth state is in the DI container, not module-level.

Per AR5: ≤15 constructor args (this class has 2: token store + trace emitter).

Per P13: invalid tokens raise AuthError, not silently ignored.

```python
"""Authenticate UI processes and issue session tokens.

Per P6: all UI connections (local and remote) authenticate via a
login gate. The user creates a username + password on first-run
setup; UIs authenticate and receive a session token. Tokens are
attached to every subsequent request.

Per AR4: the token store is instance state, not module-level. The
AuthMiddleware receives it via constructor injection.
"""
from __future__ import annotations

import hashlib
import os
import secrets
from threading import Lock
from typing import Dict
from datetime import timedelta

from sovereignai.shared.types import (
    AuthError,
    SessionToken,
    TraceEmitter,
    TraceLevel,
)


# Token expires after 8 hours (configurable in a future plan via Options panel)
TOKEN_TTL = timedelta(hours=8)


class AuthMiddleware:
    """Validate session tokens and issue new ones after username/password check.

    The middleware stores password hashes (never plaintext) and active
    session tokens. It does NOT store the user's password in memory
    after initial setup — only the hash (per P10 security principle).
    """

    def __init__(self, trace: TraceEmitter) -> None:
        """Create an empty auth middleware with no registered users.

        Args:
            trace: Trace emitter for logging auth events (login
                attempts, token validations, failures).
        """
        self._trace = trace
        self._password_hashes: Dict[str, bytes] = {}  # username -> salted hash
        self._salts: Dict[str, bytes] = {}             # username -> salt
        self._tokens: Dict[str, SessionToken] = {}     # token string -> SessionToken
        self._lock = Lock()

    def register_user(self, username: str, password: str) -> None:
        """Add a new user with a username and password for first-run setup.

        Stores a salted hash of the password — never the plaintext.
        If the user already exists, raises ValueError (no silent
        overwrite per P13).

        Args:
            username: The login name.
            password: The plaintext password (hashed before storage).

        Raises:
            ValueError: If the username is already registered.
        """
        with self._lock:
            if username in self._password_hashes:
                raise ValueError(f"User {username!r} already registered")
            salt = os.urandom(32)
            hashed = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"),
                                         salt, iterations=100_000)
            self._salts[username] = salt
            self._password_hashes[username] = hashed
        self._trace.emit(
            component="AuthMiddleware",
            level=TraceLevel.INFO,
            message=f"User {username!r} registered",
        )

    def login(self, username: str, password: str) -> SessionToken:
        """Verify credentials and return a fresh session token if valid.

        Args:
            username: The login name.
            password: The plaintext password to verify.

        Returns:
            SessionToken valid for TOKEN_TTL (8 hours by default).

        Raises:
            AuthError: If the username is unknown or the password
                does not match.
        """
        with self._lock:
            if username not in self._password_hashes:
                raise AuthError(f"Unknown user {username!r}")
            salt = self._salts[username]
            expected = self._password_hashes[username]
            actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"),
                                         salt, iterations=100_000)
            if not secrets.compare_digest(expected, actual):
                raise AuthError(f"Invalid password for {username!r}")
            # Issue token
            from sovereignai.shared.types import now_utc
            issued = now_utc()
            token_str = secrets.token_hex(32)
            token = SessionToken(
                token=token_str,
                username=username,
                issued_at=issued,
                expires_at=issued + TOKEN_TTL,
            )
            self._tokens[token_str] = token
        self._trace.emit(
            component="AuthMiddleware",
            level=TraceLevel.INFO,
            message=f"User {username!r} logged in (token expires {token.expires_at})",
        )
        return token

    def validate(self, token_str: str) -> SessionToken:
        """Check that a session token is valid and not expired.

        Args:
            token_str: The opaque token string from a UI request.

        Returns:
            The matching SessionToken if valid.

        Raises:
            AuthError: If the token is unknown or expired.
        """
        with self._lock:
            token = self._tokens.get(token_str)
            if token is None:
                raise AuthError("Unknown session token")
            from sovereignai.shared.types import now_utc
            if now_utc() > token.expires_at:
                del self._tokens[token_str]
                raise AuthError("Session token expired")
        return token
```

**Verify:**
- Passwords stored as salted PBKDF2 hashes (never plaintext)
- Constant-time comparison via `secrets.compare_digest` (prevents timing attacks)
- Token TTL = 8 hours (configurable later)
- Thread-safe (Lock around all state)
- AuthError raised on invalid credentials (P13 — no silent failures)
- Every `def` has a docstring (AR21)

After creating, run `/verify`.

### S2.2 — Create `tests/test_auth.py`

Required tests:

1. **`test_register_user_stores_hash_not_plaintext`** — register, verify `_password_hashes` does not contain the plaintext
2. **`test_login_valid_credentials_returns_token`** — register, login, get SessionToken
3. **`test_login_unknown_user_raises`** — login with unregistered username, AuthError
4. **`test_login_wrong_password_raises`** — register, login with wrong password, AuthError
5. **`test_validate_valid_token_returns_token`** — login, validate the returned token, succeeds
6. **`test_validate_unknown_token_raises`** — validate random string, AuthError
7. **`test_validate_expired_token_raises_and_deleted`** — issue token, mock time forward 9 hours, validate raises AuthError, token removed from store
8. **`test_register_duplicate_user_raises`** — register same username twice, ValueError

For test 7 (expiry), use `unittest.mock.patch` on `now_utc`.

After tests pass, run `/verify`.

---

## S3 — Capability API

### S3.1 — Create `sovereignai/shared/capability_api.py`

Per AR7: UIs consume this API only — no imports from core internals. Per A5: depends only on `ICapabilityIndex` (Plan 2) and `ITaskStateQuery` (Plan 3).

Per P8: the Capability API is the contract UI processes call to query state and submit tasks.

```python
"""Public contract that UI processes consume to query state and submit tasks.

Per AR7: UIs may not import from sovereignai/ internals directly. They
consume this API only. The API depends on ICapabilityIndex (Plan 2)
and ITaskStateQuery (Plan 3) — never on concrete classes.

Per P8: the API exposes three operations:
  1. query_capabilities — what can the system do right now?
  2. submit_task — ask the system to do something
  3. subscribe_traces — observe what's happening (deferred to a later plan)
"""
from __future__ import annotations

from typing import Tuple
from uuid import UUID, uuid4

from sovereignai.shared.auth import AuthMiddleware
from sovereignai.shared.capability_graph import ICapabilityIndex
from sovereignai.shared.task_state_machine import ITaskStateQuery
from sovereignai.shared.types import (
    CapabilityCategory,
    CapabilityQuery,
    CapabilityResponse,
    ComponentId,
    Task,
    TaskState,
    TraceEmitter,
    TraceLevel,
)
from sovereignai.shared.types import now_utc


class CapabilityAPI:
    """Public interface for UI processes to query state and submit tasks.

    The API validates the session token on every call (per P6 login
    gate). It depends only on the ICapabilityIndex and ITaskStateQuery
    protocols — never on the concrete CapabilityGraph or
    TaskStateMachine classes (per AR7).
    """

    def __init__(self, auth: AuthMiddleware,
                 capability_index: ICapabilityIndex,
                 task_state_query: ITaskStateQuery,
                 trace: TraceEmitter) -> None:
        """Create a Capability API wired to the core's query protocols.

        Args:
            auth: Auth middleware for validating session tokens.
            capability_index: Protocol for querying capabilities (Plan 2).
            task_state_query: Protocol for querying task state (Plan 3).
            trace: Trace emitter for logging API calls.
        """
        self._auth = auth
        self._index = capability_index
        self._tasks = task_state_query
        self._trace = trace

    def query_capabilities(self, token: str,
                           query: CapabilityQuery) -> CapabilityResponse:
        """Return the components that currently provide a requested capability.

        Args:
            token: Session token from a prior login() call.
            query: What capability the UI is asking about.

        Returns:
            CapabilityResponse with the list of provider component IDs.

        Raises:
            AuthError: If the token is invalid or expired.
        """
        self._auth.validate(token)
        providers = self._index.find_providers(query.category, query.name)
        component_ids = tuple(component_id for component_id, _ in providers)
        self._trace.emit(
            component="CapabilityAPI",
            level=TraceLevel.DEBUG,
            message=f"Query {query.category}/{query.name} -> {len(component_ids)} providers",
        )
        return CapabilityResponse(query=query, providers=component_ids)

    def submit_task(self, token: str, capability_name: str,
                    payload: str) -> UUID:
        """Accept a new task from a UI process and return its tracking ID.

        Note: this Plan 4 stub does NOT actually route the task to a
        worker — that requires the full routing pipeline (Plan 3's
        RoutingEngine + a Worker dispatch, which is post-batch). The
        task is recorded in the state machine as RECEIVED. A later
        plan connects the routing engine to dispatch.

        Args:
            token: Session token from a prior login() call.
            capability_name: What capability the task needs.
            payload: Opaque task payload (JSON or similar).

        Returns:
            UUID of the newly-created task.

        Raises:
            AuthError: If the token is invalid or expired.
        """
        self._auth.validate(token)
        task_id = uuid4()
        task = Task(
            task_id=task_id,
            # MVP: capability declaration is constructed inline.
            # A later plan adds a proper lookup against the capability graph.
            capability=CapabilityDeclaration(
                category=CapabilityCategory.TOOL,
                name=capability_name,
                version="1.0.0",
            ),
            payload=payload,
            submitted_at=now_utc(),
        )
        # Submit to the state machine — but the state machine is the
        # query protocol, not the writer. The actual TaskStateMachine
        # class has a submit() method; we retrieve it via the
        # container in main.py. For Plan 4, this method just emits
        # a trace — the actual submit is wired in a later plan.
        self._trace.emit(
            component="CapabilityAPI",
            level=TraceLevel.INFO,
            message=f"Task {task_id} submitted for capability {capability_name!r}",
        )
        return task_id

    def get_task_state(self, token: str, task_id: UUID) -> TaskState:
        """Return the current state of a task by its ID.

        Args:
            token: Session token from a prior login() call.
            task_id: UUID of the task to query.

        Returns:
            TaskState.

        Raises:
            AuthError: If the token is invalid or expired.
        """
        self._auth.validate(token)
        return self._tasks.get_state(task_id)
```

**Verify:**
- Depends only on `ICapabilityIndex` and `ITaskStateQuery` protocols (A5, AR7)
- Validates token on every call (P6)
- `submit_task` is a stub for now (notes this explicitly)
- Every `def` has a docstring (AR21)

After creating, run `/verify`.

### S3.2 — Create `tests/test_capability_api.py`

Required tests:

1. **`test_query_capabilities_valid_token_returns_providers`** — register user, login, query, get response
2. **`test_query_capabilities_invalid_token_raises`** — query with bad token, AuthError
3. **`test_submit_task_valid_token_returns_uuid`** — submit, get UUID back
4. **`test_submit_task_invalid_token_raises`** — submit with bad token, AuthError
5. **`test_get_task_state_valid_token_returns_state`** — get state for a task UUID (returns FAILED for unknown — defensive default)
6. **`test_get_task_state_invalid_token_raises`** — get state with bad token, AuthError
7. **`test_api_does_not_import_concrete_classes`** — static-import test (AST scan) confirming `capability_api.py` does not import `CapabilityGraph` or `TaskStateMachine` directly (AR7 enforcement)

Test 7 is the AR7 enforcement test mentioned in the adjudication (A5). It uses `ast.parse` to walk the module's import statements.

After tests pass, run `/verify`.

---

## S4 — Static-Import Test (AR7 Enforcement)

### S4.1 — Create `tests/test_ar7_no_core_imports_in_ui.py`

Per A5: a static-import test in Plan 4 confirms no transitive imports from core. This test scans `web/`, `cli/`, `tui/`, `phone/` (when they exist — currently empty) and `capability_api.py` to verify they don't import from `sovereignai.shared.event_bus`, `sovereignai.shared.capability_graph`, `sovereignai.shared.task_state_machine`, etc.

```python
"""AR7 enforcement: UI processes and the Capability API must not import core internals.

Per A5: a static-import test confirms the Capability API has no
transitive imports from core internals. UI processes (web/, cli/,
tui/, phone/) are also subject to this rule.

This test scans Python files in the relevant directories and checks
their import statements against a deny-list of core modules.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest


# Modules that are core internals — UIs and the Capability API may
# NOT import these directly. They must go through the Capability API.
CORE_INTERNALS_DENYLIST = {
    "sovereignai.shared.event_bus",
    "sovereignai.shared.capability_graph",
    "sovereignai.shared.task_state_machine",
    "sovereignai.shared.lifecycle_manager",
    "sovereignai.shared.routing_engine",
    "sovereignai.shared.dag_validator",
    "sovereignai.shared.manifest_parser",
}


# Directories to scan for forbidden imports
UI_DIRECTORIES = ["web", "cli", "tui", "phone"]
# Plus the Capability API itself (it imports protocols, not concrete classes)
CAPABILITY_API_FILE = "sovereignai/shared/capability_api.py"


def _scan_imports(file_path: Path) -> set[str]:
    """Return the set of module names imported by a Python file.

    Args:
        file_path: Path to a .py file.

    Returns:
        Set of fully-qualified module names imported (both `import X`
        and `from X import Y` forms).
    """
    tree = ast.parse(file_path.read_text())
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module)
    return imports


def test_capability_api_does_not_import_concrete_core_classes() -> None:
    """Verify the Capability API imports only protocols, not concrete classes.

    Per A5: Plan 4's Capability API must import only ICapabilityIndex
    and ITaskStateQuery (protocols), never CapabilityGraph or
    TaskStateMachine (concrete classes).
    """
    api_path = Path(CAPABILITY_API_FILE)
    if not api_path.exists():
        pytest.skip("Capability API not yet created")
    imports = _scan_imports(api_path)
    forbidden = imports & CORE_INTERNALS_DENYLIST
    assert not forbidden, (
        f"Capability API imports forbidden core modules: {forbidden}. "
        f"Per AR7, it must import only protocols (ICapabilityIndex, "
        f"ITaskStateQuery), never concrete classes."
    )


@pytest.mark.parametrize("ui_dir", UI_DIRECTORIES)
def test_ui_directories_do_not_import_core_internals(ui_dir: str) -> None:
    """Verify UI process directories do not import from sovereignai/ internals.

    Per AR7: UIs (web, cli, tui, phone) are separate processes that
    consume the Capability API. They may not import from core
    internals directly.

    Currently these directories are empty (no UI code yet — UIs are
    post-batch). This test will start enforcing once UI files exist.
    """
    ui_path = Path(ui_dir)
    if not ui_path.exists():
        pytest.skip(f"UI directory {ui_dir}/ does not exist yet")
    py_files = list(ui_path.rglob("*.py"))
    if not py_files:
        pytest.skip(f"No .py files in {ui_dir}/ yet")
    for py_file in py_files:
        imports = _scan_imports(py_file)
        forbidden = imports & CORE_INTERNALS_DENYLIST
        assert not forbidden, (
            f"{py_file} imports forbidden core modules: {forbidden}. "
            f"Per AR7, UIs must consume the Capability API only."
        )
```

After creating, run:
```bash
.venv/Scripts/python.exe -m pytest tests/test_ar7_no_core_imports_in_ui.py -vvv
```

The Capability API test must pass. The UI directory tests will skip (no `.py` files yet). After tests pass, run `/verify`.

---

## S5 — Relay Placeholder

### S5.1 — Create `sovereignai/shared/relay_placeholder.py`

Per A4: relay server deferred entirely. Plan 4 ships a local-only placeholder that returns a structured error and emits a trace — does NOT accept connections.

```python
"""Placeholder for the relay server — returns a structured error, does not accept connections.

Per A4: the relay server (E2EE endpoint for remote UIs) is deferred
out of Plan 4 entirely. Remote UIs are explicitly a later deliverable.
This placeholder ensures any code that tries to use the relay gets a
clear, structured error rather than a silent failure or a connection
that hangs.
"""
from __future__ import annotations

from sovereignai.shared.types import TraceEmitter, TraceLevel


RELAY_NOT_SUPPORTED_MESSAGE = "Remote transport not yet supported (relay server deferred per Plan 1-4 scope adjudication A4)"


class RelayPlaceholder:
    """Stub that rejects all connection attempts with a structured error.

    This is NOT the real relay server. The real server will be
    implemented in a dedicated post-batch plan. Until then, any code
    that tries to use the relay gets a clear error and a trace event.
    """

    def __init__(self, trace: TraceEmitter) -> None:
        """Create a relay placeholder that logs all connection attempts.

        Args:
            trace: Trace emitter for logging attempts (so the user can
                see if anything is trying to use the relay).
        """
        self._trace = trace

    def attempt_connection(self, source: str) -> str:
        """Reject a connection attempt and return a structured error message.

        Args:
            source: Description of what tried to connect (e.g. "phone_app").

        Returns:
            Structured error string explaining the relay is not yet
            supported.
        """
        self._trace.emit(
            component="RelayPlaceholder",
            level=TraceLevel.WARN,
            message=f"Connection attempt from {source!r} rejected — relay not yet supported",
        )
        return RELAY_NOT_SUPPORTED_MESSAGE
```

After creating, run `/verify`.

### S5.2 — Create `tests/test_relay_placeholder.py`

Required tests:

1. **`test_attempt_connection_returns_error_message`** — call attempt_connection, get RELAY_NOT_SUPPORTED_MESSAGE back
2. **`test_attempt_connection_emits_trace`** — call attempt_connection, verify TraceEmitter recorded a WARN event
3. **`test_placeholder_does_not_open_socket`** — verify no socket is created (check that the class has no `socket` import — defensive)

After tests pass, run `/verify`.

---

## S6 — Final Composition Root Wiring Audit (Q26 Confirmation)

### S6.1 — Extend `main.py` with Plan 4 components + Q26 audit

Per A3: this is the final wiring audit. After this plan, `main.py` wires all 12 Core Scope components (those that exist in the first batch — the relay is a placeholder). Q26 is confirmed at this `/close`.

Extend `sovereignai/main.py`'s `build_container()` to add Plan 4 components:

```python
    # 7. AuthMiddleware — depends on TraceEmitter, singleton (Plan 4)
    from sovereignai.shared.auth import AuthMiddleware
    auth = AuthMiddleware(trace=trace)
    container.register_singleton(AuthMiddleware, auth)

    # 8. CapabilityAPI — depends on AuthMiddleware + ICapabilityIndex + ITaskStateQuery
    from sovereignai.shared.capability_api import CapabilityAPI
    from sovereignai.shared.capability_graph import ICapabilityIndex
    from sovereignai.shared.task_state_machine import ITaskStateQuery
    api = CapabilityAPI(
        auth=auth,
        capability_index=container.retrieve(ICapabilityIndex),
        task_state_query=container.retrieve(ITaskStateQuery),
        trace=trace,
    )
    container.register_singleton(CapabilityAPI, api)

    # 9. RelayPlaceholder — depends on TraceEmitter, singleton (Plan 4)
    # Real relay server deferred to a post-batch plan per A4.
    from sovereignai.shared.relay_placeholder import RelayPlaceholder
    relay = RelayPlaceholder(trace=trace)
    container.register_singleton(RelayPlaceholder, relay)

    # === Q26 CONFIRMATION ===
    # Per A3: Q26 ("single file instantiates all core components explicitly")
    # is confirmed at Plan 4 /close. As of this plan, main.py wires:
    #   1. TraceEmitter (Plan 1)
    #   2. EventBus (Plan 1)
    #   3. CapabilityGraph + ICapabilityIndex (Plan 2)
    #   4. LifecycleManager (Plan 3)
    #   5. RoutingEngine (Plan 3)
    #   6. TaskStateMachine + ITaskStateQuery (Plan 3)
    #   7. AuthMiddleware (Plan 4)
    #   8. CapabilityAPI (Plan 4)
    #   9. RelayPlaceholder (Plan 4 — real relay deferred per A4)
    # All 9 components instantiated explicitly in topological order.
    # No runtime magic, no auto-discovery (per Q26 resolution).

    return container
```

After edit, run `/verify`.

### S6.2 — Update `tests/test_composition_root.py` with Q26 audit tests

Add tests:

16. **`test_auth_middleware_registered`** — retrieve AuthMiddleware, not None
17. **`test_capability_api_registered`** — retrieve CapabilityAPI, not None
18. **`test_relay_placeholder_registered`** — retrieve RelayPlaceholder, not None
19. **`test_capability_api_has_auth_wired`** — retrieve CapabilityAPI, verify its `_auth` is the registered AuthMiddleware
20. **`test_capability_api_has_capability_index_wired`** — verify `_index` is the registered CapabilityGraph
21. **`test_capability_api_has_task_state_query_wired`** — verify `_tasks` is the registered TaskStateMachine
22. **`test_q26_all_components_instantiated_in_main`** — Q26 audit: parse `main.py` via AST, verify all 9 component classes are instantiated in `build_container()`. (This is the Q26 confirmation test.)

After tests pass, run `/verify`.

---

## S7 — Update PLANS.md + DECISIONS.md

### S7.1 — Update PLANS.md

- Update Test Baseline: total = 69 (Plan 3) + 8 (auth) + 7 (capability API) + 1 (AR7 test) + 3 (relay placeholder) + 7 (composition root extensions including Q26 audit) = **95 tests**
- Update Active Plan to "Plan 5 (Scan) — awaiting execution"
- Update Next-5-Prompt Queue: promote Scan 5 to slot 1, mark "▶️ Active"
- Strike Q26 from Open Questions Outstanding (resolved at this `/close`)

### S7.2 — Update DECISIONS.md

Append Q26 resolution:

```markdown
## D4 — Q26 Composition Root bootstrap confirmed

**Context**: Q26 ("single file instantiates all core components explicitly") — locked in the vision but not confirmable until all 12 Core Scope components exist.
**Options considered**: Not separately debated — the decision was made during the Plan 1-4 scope adjudication (A3) and confirmed at Plan 4 /close.
**Decision**: Q26 confirmed. `main.py` instantiates all 9 components that exist in the first batch (Plans 1-4) explicitly in topological order. No runtime magic, no auto-discovery. The relay is a placeholder (real relay deferred per A4).
**Rationale**: A3 — incremental Composition Root. Each plan extended `build_container()` to add its components. Plan 4 performs the final audit and confirms Q26.
**Trade-offs**: Adding a 10th component (e.g. the real relay server in a post-batch plan) requires extending `build_container()` again — no auto-wiring shortcut.
**Status**: Active. Revisit if a future plan proposes auto-discovery (would require a Round Table review to amend Q26).
**Source**: `project-vision-Rev5.md` Q26 (resolved); `documents/plan-1-4-scope-adjudication.md` A3.
```

After edits, run `/verify`.

---

## S8 — Update CHANGELOG.md

Append to `CHANGELOG.md`:

```markdown
## prompt-4 — Interface layer (auth, Capability API, relay placeholder, Q26 audit)

**Date**: {YYYY-MM-DD}
**Plan file**: prompts/plan-4-Rev1.md

**Files changed**:
- sovereignai/shared/types.py (extended: SessionToken, AuthError, CapabilityQuery, CapabilityResponse)
- sovereignai/shared/auth.py (new — PBKDF2 hashing, session tokens, 8h TTL)
- sovereignai/shared/capability_api.py (new — public contract for UIs, AR7-compliant)
- sovereignai/shared/relay_placeholder.py (new — returns structured error per A4)
- sovereignai/main.py (extended: registers Auth, CapabilityAPI, RelayPlaceholder; Q26 audit comment)
- tests/test_auth.py (new — 8 tests)
- tests/test_capability_api.py (new — 7 tests including AR7 static-import)
- tests/test_ar7_no_core_imports_in_ui.py (new — AR7 enforcement for UI dirs + capability_api.py)
- tests/test_relay_placeholder.py (new — 3 tests)
- tests/test_composition_root.py (extended — 7 new tests including Q26 audit)
- DECISIONS.md (added D4 — Q26 resolution)
- PLANS.md (updated test baseline, active plan, queue; struck Q26 from open questions)

**Results**:
- Tests: 95 passed (69 from Plans 1-3 + 26 new)
- Ruff: 0 errors
- Mypy: 0 errors (file-scoped per OR47)
- Bandit: 0 findings
- pip-audit: 0 CVEs
- Vulture: 0 findings
- Detect-secrets: pass

**Notes**:
- Q26 (Composition Root bootstrap) confirmed at this /close. main.py instantiates all 9 first-batch components explicitly in topological order.
- AR7 enforcement: static-import test verifies Capability API imports only protocols (ICapabilityIndex, ITaskStateQuery), never concrete classes. UI directory tests will activate once UI files exist (post-batch).
- Auth: PBKDF2 hashing (100k iterations, 32-byte salt), constant-time comparison via secrets.compare_digest, 8-hour token TTL.
- Relay: placeholder only. Returns "Remote transport not yet supported" structured error. Real relay deferred per A4 (DEBT).
- Plans 1-4 batch complete. Next: Scan 5 (mechanical verification), then Plans 6-9 batch.
```

After edit, run `/verify`.

---

## S9 — Commit and Tag Prompt-4

**STOP condition**: If any `/verify` failed, STOP.

1. Stage all changes:
   ```bash
   git add -A
   git status -s | tail -n 30
   ```

2. Commit (multiple `-m` per OR42):
   ```bash
   git commit -m "prompt-4: Interface layer — auth, Capability API, relay placeholder, Q26 audit" -m "shared/auth.py: PBKDF2 password hashing (100k iterations, 32-byte salt), session tokens with 8h TTL, constant-time comparison via secrets.compare_digest." -m "shared/capability_api.py: public contract for UI processes. Depends only on ICapabilityIndex + ITaskStateQuery protocols (A5, AR7). submit_task is a stub — full routing pipeline is post-batch." -m "shared/relay_placeholder.py: returns structured error per A4. Real relay deferred to DEBT." -m "tests/test_ar7_no_core_imports_in_ui.py: AR7 enforcement — static-import test scans capability_api.py and UI dirs for forbidden core imports." -m "main.py: Q26 audit comment added. All 9 first-batch components instantiated explicitly in topological order." -m "Tests: 26 new (8 auth + 7 capability_api + 1 ar7 + 3 relay + 7 composition_root incl Q26 audit). Total: 95." -m "Q26 confirmed at /close. DECISIONS.md D4 added. Plans 1-4 batch complete."
   ```

3. Tag, push, verify:
   ```bash
   git tag prompt-4
   git push origin main
   git push origin prompt-4
   git ls-remote --tags origin | grep "prompt-4"
   ```

---

## Closing

Run `/close` workflow (all 21 steps). Expected:
- Tests: 95 passed
- Ruff: 0 errors
- Mypy: 0 errors (file-scoped to Plan 4 `.py` files per OR47)
- Bandit: 0 findings
- pip-audit: 0 CVEs
- Vulture: 0 findings
- Detect-secrets: pass
- Custom AR checks: pass (no globals, ≤15 args, no context bags, docstrings, no hard-coded component names in UI dirs)

**Key verifications**:
- AR7 enforcement test passes (Capability API imports only protocols)
- Q26 audit test passes (all 9 components instantiated in main.py)
- Auth uses PBKDF2 + constant-time comparison (no plaintext passwords)
- Relay placeholder rejects connections with structured error (A4)
- `submit_task` is documented as a stub (full routing is post-batch)

After `/close`, create `logs/execution-log-prompt-4.md`. User pastes log, then asks Executor to commit/push.

**Reminder**: Step 21 (kill bash) mandatory.

---

## Files WILL Create

- `sovereignai/shared/auth.py`
- `sovereignai/shared/capability_api.py`
- `sovereignai/shared/relay_placeholder.py`
- `tests/test_auth.py`
- `tests/test_capability_api.py`
- `tests/test_ar7_no_core_imports_in_ui.py`
- `tests/test_relay_placeholder.py`
- `logs/execution-log-prompt-4.md` (created by `/close`)

## Files WILL Edit

- `sovereignai/shared/types.py` (append auth + capability-API types at S1.1)
- `sovereignai/main.py` (extend `build_container()` at S6.1; Q26 audit comment)
- `tests/test_composition_root.py` (add 7 new tests at S6.2 including Q26 audit)
- `DECISIONS.md` (add D4 — Q26 resolution at S7.2)
- `PLANS.md` (update test baseline, active plan, queue; strike Q26 at S7.1; add prompt-4 row at `/close`)
- `CHANGELOG.md` (append prompt-4 entry at S8)

## Files WILL NOT Edit

- `AGENTS.md`, `AI_HANDOFF.md`, `.devin/workflows/*.md` (stable)
- `documents/*` (archived)
- `prompts/*` (no changes)
- `pyproject.toml`, `.pre-commit-config.yaml`, `.gitignore`, `README.md`, `txt/*` (stable)
- All `.gitkeep` files
- `DEBT.md`, `LANDMINES.md` (no new deferrals/landmines unless execution surfaces them)

---

*Plan 4 — Interface Layer. Rev1. Architect draft. Part of Plans 1-4 batch — Round Table reviews alongside plan-1, plan-2, plan-3, and the shared context brief. Q26 (Composition Root bootstrap) confirmed at this plan's /close.*
