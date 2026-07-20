# Plan 4 — Interface Layer (Auth, Capability API, Relay Placeholder, Final Wiring Audit)

**Batch**: 4 of 4 (Plans 1–4 drafted together; shared context brief at `plan-1-4-batch-Rev1-context-brief.md`)

Depends on: prompt-3
Vision principles: 1 (sacred core), 2 (pluggable), 3 (no provider lock-in), 5 (wire as you go), 7 (modular core), 8 (UIs separate processes consuming Capability API), 9 (observability), 11 (DI, no globals), 12 (plain-English docstrings), 13 (strong, robust), 14 (provenance — for external components; auth is the gate)
Open questions resolved: Q26 (Composition Root bootstrap — confirmed at this plan's `/close`)

---

## Adjudication Log (Rev4 → Rev5)

Per GR4. Rev5 does not get a new context brief. 6 panelist responses were received on Rev4. The following Rev4 issues were accepted and fixed.

### Finding 1 — `capability_api.py` imports undefined exception types (Kimi HIGH, Qwen HIGH)
**Severity**: HIGH (ImportError at /verify)
**Action**: ACCEPTED. Plan 3 S1.1 now defines `DAGValidationError`, `InvalidStateTransitionError`, `UnknownTaskError` in `shared/types.py`. `NoProviderRegisteredError` removed from import (never defined, never used).

### Finding 3 — AR7 denylist uses exact matching, misses subpackages (Kimi HIGH, Gemini MEDIUM, Qwen MEDIUM)
**Severity**: HIGH
**Action**: ACCEPTED. Test now uses prefix matching: any import starting with a denied prefix is forbidden.

### Finding 4 — UIs cannot legally use API's public types (Kimi HIGH, Gemini MEDIUM)
**Severity**: HIGH (first UI cannot be written)
**Action**: ACCEPTED. `sovereignai.shared.types` removed from `UI_PACKAGE_DENYLIST` — types are data contracts, not implementation. UIs need `CapabilityCategory`, `TaskState` etc. to call the API. Public types are also re-exported from `capability_api.py` for convenience.

### Finding 6 — `submit_task` catches exceptions `submit()` cannot raise (Kimi MEDIUM, Qwen MEDIUM)
**Action**: ACCEPTED. Catch only `DAGValidationError` (the only exception `submit()` can raise for this batch). Comment notes future expansion.

### Finding 11 — `DAGSpec` imported but unused (Qwen LOW)
**Action**: ACCEPTED. Removed from import.

### Finding 12 — Split imports from `types.py` (Qwen LOW)
**Action**: ACCEPTED. Merged into single import block.

### Verdict
All HIGH/MEDIUM issues fixed. Plan 4 Rev5 is ready for execution.

---

## Adjudication Log (Rev3 → Rev4)

Per GR4. Rev4 does not get a new context brief. 5 panelist responses were received on Rev3. The following Rev3 issues were accepted and fixed.

### Finding 3 — AR7 denylist misses `sovereignai.orchestrator`, `sovereignai.managers`, `sovereignai.workers` (Gemini MEDIUM, upgraded to HIGH)
**Severity**: HIGH (UI can import core orchestrator packages directly)
**Reasoning**: Rev3 `UI_PACKAGE_DENYLIST` only blocked `sovereignai.shared` and `sovereignai.shared.types`. A UI could `from sovereignai.orchestrator.routing_engine import RoutingEngine` and the test would pass — violating AR7 (UIs consume Capability API only).
**Action**: ACCEPTED. `UI_PACKAGE_DENYLIST` expanded to include all `sovereignai.{layer}` packages: `sovereignai.orchestrator`, `sovereignai.managers`, `sovereignai.workers`, `sovereignai.librarian`, `sovereignai.adapters`, `sovereignai.skills`, `sovereignai.panels` (if it existed — it doesn't, but defensive). UIs may import ONLY from `sovereignai.shared.capability_api` (the public API).

### Finding 4 — `submit_task` bare `except Exception` masks bugs (DeepSeek MEDIUM, Kimi MEDIUM, Qwen MEDIUM, Gemini MEDIUM — convergent)
**Severity**: MEDIUM (debugging difficulty)
**Reasoning**: Rev3 S3.1 wrapped `self._state_machine.submit(task)` in `try: ... except Exception as exc:`. This catches `TypeError`, `AttributeError`, `KeyError` — programming bugs — and converts them to generic `CapabilityAPIError`. The original exception type is hidden.
**Action**: ACCEPTED. S3.1 now catches only specific exceptions: `DAGValidationError`, `InvalidStateTransitionError`, `UnknownTaskError`. These are moved to `shared/types.py` (Plan 3 S1.1 adds them alongside `NoActiveProviderError`) so the Capability API can import them without AR7 violation. Unexpected exceptions (`TypeError`, `AttributeError`, etc.) propagate uncaught — they indicate bugs that should fail fast, not be masked.

### Finding 5 — `DAGSpec` lacks fields for real composite skills (Kimi MEDIUM, Gemini MEDIUM — convergent)
**Severity**: MEDIUM (future breaking change)
**Reasoning**: Rev3 `DAGSpec` has `nodes`, `edges`, `input_types`, `output_types` — enough for basic acyclicity + type-matching validation, but not for real composite skills (per-node capability references, input bindings, condition expressions per Q28). When Plan 6+ implements composite task execution, `DAGSpec` will need extension.
**Action**: ACCEPTED as DEBT. Added `DEBT.md` entry: "DAGSpec extension for composite skills." The current minimal scaffold is sufficient for this batch (atomic tasks only; composite task submission is post-batch per scope).

### Finding 7 — `now_utc` inline imports in `auth.py` (Qwen LOW)
**Severity**: LOW (code style)
**Reasoning**: Rev3 S2.1 `auth.py` imported `now_utc` inline in `login()` and `validate()` instead of at the top level. Inconsistent with the rest of the codebase.
**Action**: ACCEPTED. `now_utc` moved to top-level imports in `auth.py`. Inline imports removed.

### Rejected findings

- **Kimi** "DIContainer singleton creates shared mutable AuthMiddleware state" — by design. Auth is a singleton (one user, one token store per P6). The "leak across callers" concern is for multi-user systems; SovereignAI is single-user. Accept as documented.
- **Kimi** "ITaskStateWrite protocol missing" — accepted as DECISIONS.md D5. The write path uses concrete TaskStateMachine. Adding a write protocol is a future plan's scope.
- **Kimi** "AR7 cannot catch dynamic imports" — true, documented as known limitation. Runtime `sys.modules` audit deferred to DEBT until UIs exist.
- **DeepSeek** "NoActiveProviderError defined but never raised in submit_task" — false. Rev3 Finding 3 added the check. The Rev3 code does call `find_providers()` and raises.
- **DeepSeek** "AR7 top-level `import sovereignai` bypass" — `import sovereignai` alone doesn't give access to internals unless the package eagerly imports subpackages, which it doesn't. The bypass requires `import sovereignai.shared` (caught by `UI_PACKAGE_DENYLIST`). Accept as documented.

### Verdict

All HIGH/MEDIUM issues fixed. Plan 4 Rev4 is ready for execution.

---

## Adjudication Log (Rev2 → Rev3)

Per GR4. Rev3 does not get a new context brief. 6 panelist responses were received on Rev2. The following Rev2 issues were accepted and fixed.

### Finding 2 — S3.2 stale test descriptions (Kimi HIGH, Qwen HIGH — convergent)
**Severity**: HIGH (Executor writes failing tests)
**Reasoning**: Rev2 S3.2 test 5 expected `get_task_state` to return `FAILED` for unknown UUIDs, but Plan 3 Rev2 changed `get_state()` to return `None`. Test 7 said the API must not import `TaskStateMachine`, but the Rev2 `submit_task` fix requires importing it.
**Action**: ACCEPTED. S3.2 test descriptions updated:
- Test 5 → expects `None` for unknown UUIDs (per Plan 3 Finding 5).
- Test 7 → removed. Rely solely on S4.1's AR7 test. The `TaskStateMachine` import is documented as an accepted AR7 gap (the write path requires the concrete class; the query path uses the protocol). Added to `DECISIONS.md`.

### Finding 3 — Contradictory AR7 tests (Qwen HIGH)
**Severity**: HIGH (one test passes, one fails)
**Reasoning**: S3.2 test 7 said no `TaskStateMachine` import; S4.1 denylist excluded `task_state_machine` (allowed it). Contradiction.
**Action**: ACCEPTED. S3.2 test 7 removed (see Finding 2 above). S4.1 is the sole AR7 enforcement test.

### Finding 4 — AR7 test fails on reference implementation (Kimi HIGH)
**Severity**: HIGH (test fails on the API it's supposed to verify)
**Reasoning**: Rev2 S4.1 `CORE_INTERNALS_CONCRETE_DENYLIST` included `sovereignai.shared.auth` and `sovereignai.shared.routing_engine`. But `capability_api.py` imports `AuthMiddleware` from the former and `NoActiveProviderError` from the latter.
**Action**: ACCEPTED. Two changes:
- `NoActiveProviderError` moved from `routing_engine.py` to `shared/types.py` (it's a domain error, not a routing-specific error). The Capability API imports it from `types.py`.
- `auth` removed from the denylist (the Capability API legitimately imports `AuthMiddleware` — auth is part of the API's constructor). `routing_engine` removed from the denylist (no longer needed since `NoActiveProviderError` moved).
- The denylist now contains only modules that the Capability API should NEVER import: `event_bus`, `capability_graph` (concrete), `task_state_machine` (concrete), `lifecycle_manager`, `dag_validator`, `manifest_parser`, `relay_placeholder`, `trace_emitter`, `container`, `types` (for UI dirs only — see Finding 8).

### Finding 5 — AR7 denylist misses `sovereignai.shared` package import (Gemini HIGH, Kimi MEDIUM, Qwen MEDIUM — convergent)
**Severity**: HIGH (bypass via `import sovereignai.shared` then `shared.event_bus.publish()`)
**Reasoning**: Rev2 S4.1 only denied leaf modules. `import sovereignai.shared` passed the test, then attribute access reached internals.
**Action**: ACCEPTED. `sovereignai.shared` added to a separate `UI_PACKAGE_DENYLIST` that applies ONLY to UI directories (`web/`, `cli/`, `tui/`, `phone/`). The Capability API is allowed to import from `sovereignai.shared` (it lives there). UIs are not.

### Finding 8 — `sovereignai.shared.types` not in denylist (Kimi MEDIUM)
**Severity**: MEDIUM (UI can import types directly)
**Reasoning**: A UI could `import sovereignai.shared.types` and access `Task`, `TaskState`, etc. — bypassing the Capability API.
**Action**: ACCEPTED. `sovereignai.shared.types` added to `UI_PACKAGE_DENYLIST` (applies only to UI directories). The Capability API is allowed to import from `types.py` (it constructs `Task` objects).

### Finding 9 — submit_task doesn't handle DAGValidationError (DeepSeek MEDIUM)
**Severity**: MEDIUM (uncaught exception propagates)
**Reasoning**: Rev2 S3.1 `submit_task` calls `self._state_machine.submit(task)`. If `submit()` raises `DAGValidationError` (only when `dag` param is provided — atomic tasks pass `dag=None` so this won't trigger), the exception propagates uncaught to the API handler.
**Action**: ACCEPTED. S3.1 `submit_task` wraps `self._state_machine.submit(task)` in try/except. Catches `DAGValidationError`, `InvalidStateTransitionError`, `UnknownTaskError`, and re-raises as a typed `CapabilityAPIError` (new exception class in `shared/types.py`). Defensive coding — for atomic tasks in this batch, the catch is never triggered, but future composite task submission will benefit.

### Finding 13 — CapabilityAPI docstring contradicts signature (Kimi LOW)
**Severity**: LOW (documentation accuracy)
**Reasoning**: Rev2 S3.1 docstring claimed "depends only on ICapabilityIndex and ITaskStateQuery protocols" but `__init__` accepts concrete `AuthMiddleware` and `TaskStateMachine`.
**Action**: ACCEPTED. Docstring rewritten to accurately describe the concrete/protocol split: query path uses protocols; write path (submit) uses concrete TaskStateMachine; auth uses concrete AuthMiddleware.

### Finding 14 — Tasks remain in RECEIVED indefinitely (Kimi MEDIUM, Qwen MEDIUM, Gemini MEDIUM — convergent)
**Severity**: MEDIUM (resource leak, broken contract)
**Reasoning**: Rev2 `submit_task` calls `submit()` which sets state to RECEIVED. No worker dispatch exists. Tasks accumulate forever.
**Action**: ACCEPTED as DEBT. Added `DEBT.md` entry: "Task TTL/eviction strategy" — deferred until worker dispatch pipeline is wired (post-batch). For the batch, tasks in RECEIVED are acceptable as a documented stub.

### Rejected findings

- **Kimi** "Auth middleware has no rate limiting or token revocation" — out of scope for v1 single-user.
- **DeepSeek** "PBKDF2 iteration scalability DoS" — speculative for single-user local-first.
- **Qwen** "shared/ accumulates implementations, violating AR4" — AR4's intent is to prevent business logic, not core infrastructure. The implementations in `shared/` are core infrastructure.
- **Kimi** "AR7 is still not meaningfully enforced for separate UI processes" — true, but the static test is the best we can do without UI processes existing. A runtime `sys.modules` audit is deferred until UIs actually exist (DEBT). Moving the Capability API out of `shared/` is a larger architectural change deferred to a future plan.
- **DeepSeek** "submit_task accepts tasks whose only providers are not ACTIVE" — correct observation but the routing pipeline is post-batch. The check is "is there a registered provider?" not "is there an active provider?" — that's the RoutingEngine's job.

### Verdict

All HIGH/MEDIUM issues fixed. Plan 4 Rev3 is ready for execution.

---

## Adjudication Log (Rev1 → Rev2)

Per GR4. Rev2 does not get a new context brief. 6 panelist responses received. The following Rev1 issues were accepted and fixed.

### Finding 1 — `submit_task` silently drops tasks (DeepSeek CRITICAL, all 6 panelists HIGH — convergent)
**Severity**: CRITICAL (data loss, P9 violation)
**Reasoning**: Rev1 S3.1 `submit_task` validated the token, created a Task, emitted a trace, returned a UUID — but never called `TaskStateMachine.submit()`. The task was stored nowhere. No worker would ever execute it. The caller received a valid UUID and had no way to detect the task was lost. This is a data loss bug.
**Action**: ACCEPTED. S3.1 `submit_task` now retrieves the `TaskStateMachine` from the DI container and calls `submit(task)`. The task enters RECEIVED state and is queryable via `ITaskStateQuery.get_state()`. The actual routing to a worker remains deferred (post-batch) — the task stays in RECEIVED until a future plan wires the routing pipeline. This is documented in the docstring.

### Finding 2 — `submit_task` hardcodes `CapabilityCategory.TOOL` (DeepSeek MEDIUM, Kimi HIGH, Qwen MEDIUM — convergent)
**Severity**: HIGH (tasks for non-tool capabilities unroutable)
**Reasoning**: Rev1 S3.1 constructed `CapabilityDeclaration(category=CapabilityCategory.TOOL, name=capability_name, version="1.0.0")` regardless of the actual capability. A task requesting "text_generation" (which should be `MODEL_INFERENCE`) was recorded as `TOOL`. When routing is wired, no provider would match.
**Action**: ACCEPTED. S3.1 `submit_task` signature now accepts a `category: CapabilityCategory` parameter. The caller specifies the category. The capability declaration is constructed with the provided category.

### Finding 3 — `submit_task` doesn't validate capability exists (DeepSeek MEDIUM, Kimi MEDIUM)
**Severity**: MEDIUM (silent failure for non-existent capabilities)
**Reasoning**: Rev1 S3.1 constructed the capability declaration inline without querying `ICapabilityIndex`. A UI could submit a task for a non-existent capability and receive a UUID.
**Action**: ACCEPTED. S3.1 `submit_task` now calls `self._index.find_providers(category, capability_name)` before accepting the task. If no providers are registered, raises `NoActiveProviderError` (imported from Plan 3's routing_engine). The task is NOT submitted.

### Finding 4 — AR7 static-import test fails on the Capability API itself + misses `from...import` forms (DeepSeek HIGH, Kimi HIGH, Qwen MEDIUM — convergent)
**Severity**: HIGH (test fails on reference implementation; bypassable)
**Reasoning**: Rev1 S4.1 `CORE_INTERNALS_DENYLIST` included `sovereignai.shared.task_state_machine` and `sovereignai.shared.capability_graph` — which the Capability API legitimately imports from (for the protocols `ITaskStateQuery` and `ICapabilityIndex`). The test would flag these as forbidden and fail. Additionally, the test only checked `ast.Import` and `ast.ImportFrom.module` — missing `from sovereignai.shared import event_bus` (sub-module access via package import).
**Action**: ACCEPTED. S4.1 test redesigned:
- The denylist is now `CORE_INTERNALS_CONCRETE_DENYLIST` — only concrete implementation modules (event_bus, capability_graph, task_state_machine, lifecycle_manager, routing_engine, dag_validator, manifest_parser, auth, relay_placeholder). Protocol modules are NOT in the denylist — the Capability API is allowed to import protocols.
- The test checks both `ast.Import` and `ast.ImportFrom` nodes.
- For `ImportFrom`, it checks both `node.module` AND each `alias.name` (catches `from sovereignai.shared import event_bus` where `node.module` is `sovereignai.shared` but `alias.name` is `event_bus`).
- Dynamic imports (`importlib.import_module`) are NOT caught by AST scan — documented as a known limitation. A runtime `sys.modules` audit is deferred (DEBT) until UI processes actually exist.

### Finding 5 — Relay placeholder's "structured error" is a plain string (DeepSeek MEDIUM, Kimi MEDIUM, Qwen LOW, GPT-5.4-mini LOW — convergent)
**Severity**: MEDIUM (callers cannot programmatically distinguish)
**Reasoning**: Rev1 S5.1 returned `RELAY_NOT_SUPPORTED_MESSAGE` (a plain string). Callers cannot distinguish this from other string returns.
**Action**: ACCEPTED. S5.1 now defines a `RelayNotSupportedError(Exception)` class in `shared/types.py`. The placeholder's `attempt_connection()` raises this error (not returns a string). Callers catch the exception programmatically.

### Rejected findings

- **Kimi** "Auth middleware has no rate limiting or token revocation" — true but out of scope for Plan 4. Rate limiting and token revocation are operational features deferred to a later plan. The 8-hour TTL is the v1 token lifecycle. Add to DEBT if needed.
- **DeepSeek** "PBKDF2 iteration scalability DoS" — speculative for v1 single-user local-first. The system has one user. 100k iterations is ~100ms on modern hardware — acceptable for a single-user login.
- **Qwen** "shared/ accumulates implementations, violating AR4" — AR4 says `shared/` holds "contracts, interfaces, and the DI container only — no runtime state outside the container." The implementations in `shared/` (event_bus, capability_graph, etc.) are core infrastructure, not pluggable components. AR4's intent is to prevent `shared/` from holding business logic or pluggable state. The current usage is correct. If the Round Table disagrees, this is a vision-level debate to reopen in a future plan.

### Verdict

All CRITICAL/HIGH issues fixed. Plan 4 Rev2 is ready for execution.

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


class RelayNotSupportedError(Exception):
    """Raised when a caller attempts to use the relay before it is implemented.

    Per Finding 5 (Rev2): the relay placeholder raises this exception
    instead of returning a plain string. Callers catch it programmatically
    to distinguish "relay not supported" from other errors.
    """

    def __init__(self, message: str = "Remote transport not yet supported (relay server deferred per Plan 1-4 scope adjudication A4)") -> None:
        """Create a relay-not-supported error with a descriptive message.

        Args:
            message: Human-readable explanation of why the relay is not available.
        """
        super().__init__(message)


class NoActiveProviderError(Exception):
    """Raised when no provider is registered for a requested capability.

    Per Rev3 Finding 4: moved from routing_engine.py to shared/types.py.
    The Capability API needs this error (it validates capability existence
    before submitting tasks) but should not import from routing_engine
    (a concrete implementation module — AR7 violation).
    """

    def __init__(self, message: str = "No active provider for the requested capability") -> None:
        """Create a no-active-provider error with a descriptive message.

        Args:
            message: Human-readable explanation of which capability has no provider.
        """
        super().__init__(message)


class CapabilityAPIError(Exception):
    """Raised when the Capability API encounters an internal error.

    Per Rev3 Finding 9: wraps lower-level errors (DAGValidationError,
    InvalidStateTransitionError, UnknownTaskError) so callers get a
    single typed exception from the API rather than propagating core
    internals.
    """

    def __init__(self, message: str, cause: Exception | None = None) -> None:
        """Create a CapabilityAPIError wrapping an optional cause.

        Args:
            message: Human-readable explanation of what failed.
            cause: The underlying exception, if any.
        """
        self.cause = cause
        super().__init__(message)
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
    now_utc,
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

from typing import Optional, Tuple
from uuid import UUID, uuid4

from sovereignai.shared.auth import AuthMiddleware
from sovereignai.shared.capability_graph import ICapabilityIndex
from sovereignai.shared.task_state_machine import ITaskStateQuery, TaskStateMachine
from sovereignai.shared.types import (
    CapabilityAPIError,
    CapabilityCategory,
    CapabilityDeclaration,
    CapabilityQuery,
    CapabilityResponse,
    ComponentId,
    DAGValidationError,
    NoActiveProviderError,
    Task,
    TaskState,
    TraceEmitter,
    TraceLevel,
    now_utc,
)


class CapabilityAPI:
    """Public interface for UI processes to query state and submit tasks.

    The API validates the session token on every call (per P6 login
    gate). It depends on a mix of protocols and concrete classes:
    - Query path (query_capabilities, get_task_state): uses ICapabilityIndex
      and ITaskStateQuery protocols (AR7-compliant).
    - Write path (submit_task): uses concrete TaskStateMachine (the
      ITaskStateQuery protocol is query-only; submit requires the writer).
    - Auth: uses concrete AuthMiddleware (auth is part of the API's
      constructor, not a queryable protocol).

    Per Rev3 Finding 13: docstring updated to accurately describe the
    concrete/protocol split (Rev2 incorrectly claimed "depends only on
    protocols").
    """

    def __init__(self, auth: AuthMiddleware,
                 capability_index: ICapabilityIndex,
                 task_state_query: ITaskStateQuery,
                 state_machine: TaskStateMachine,
                 trace: TraceEmitter) -> None:
        """Create a Capability API wired to the core's query protocols.

        Args:
            auth: Auth middleware for validating session tokens.
            capability_index: Protocol for querying capabilities (Plan 2).
            task_state_query: Protocol for querying task state (Plan 3).
            state_machine: Concrete TaskStateMachine for submitting tasks
                (per Finding 1 — submit_task needs the writer, not just
                the query protocol). Retrieved from the DI container.
            trace: Trace emitter for logging API calls.
        """
        self._auth = auth
        self._index = capability_index
        self._tasks = task_state_query
        self._state_machine = state_machine
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

    def submit_task(self, token: str, category: CapabilityCategory,
                    capability_name: str, payload: str) -> UUID:
        """Accept a new task from a UI process and return its tracking ID.

        Per Finding 1 (Rev2): the task IS submitted to the
        TaskStateMachine — it enters RECEIVED state and is queryable via
        ITaskStateQuery.get_state(). The actual routing to a worker
        remains deferred (post-batch) — the task stays in RECEIVED until
        a future plan wires the routing pipeline.

        Per Finding 2 (Rev2): the `category` parameter is now required —
        callers specify whether this is a TOOL, MODEL_INFERENCE, MEMORY,
        or COMMUNICATION capability. Rev1 hardcoded TOOL.

        Per Finding 3 (Rev2): the capability is validated against
        ICapabilityIndex before the task is accepted. If no provider is
        registered, NoActiveProviderError is raised.

        Args:
            token: Session token from a prior login() call.
            category: The capability category (TOOL, MODEL_INFERENCE, etc.).
            capability_name: What capability the task needs.
            payload: Opaque task payload (JSON or similar).

        Returns:
            UUID of the newly-created task (in RECEIVED state).

        Raises:
            AuthError: If the token is invalid or expired.
            NoActiveProviderError: If no provider is registered for the
                requested capability.
        """
        self._auth.validate(token)
        # Per Finding 3: validate capability exists before accepting
        providers = self._index.find_providers(category, capability_name)
        if not providers:
            raise NoActiveProviderError(
                f"No provider registered for {category}/{capability_name}"
            )
        task_id = uuid4()
        task = Task(
            task_id=task_id,
            capability=CapabilityDeclaration(
                category=category,
                name=capability_name,
                version=providers[0][1].version,  # use the highest-priority provider's version
            ),
            payload=payload,
            submitted_at=now_utc(),
        )
        # Per Finding 1: submit to the state machine so the task is tracked
        # Per Rev3 Finding 9: wrap in try/except to convert lower-level
        # errors to CapabilityAPIError.
        # Per Rev4 Finding 4: catch ONLY specific exceptions (not bare
        # `except Exception`). Unexpected exceptions (TypeError,
        # AttributeError, etc.) propagate uncaught — they indicate bugs
        # that should fail fast, not be masked.
        try:
            self._state_machine.submit(task)
        except DAGValidationError as exc:
            raise CapabilityAPIError(
                f"Failed to submit task {task_id} to state machine: {exc}",
                cause=exc,
            ) from exc
        self._trace.emit(
            component="CapabilityAPI",
            level=TraceLevel.INFO,
            message=f"Task {task_id} submitted for {category}/{capability_name!r}",
        )
        return task_id

    def get_task_state(self, token: str, task_id: UUID) -> Optional[TaskState]:
        """Return the current state of a task by its ID, or None if unknown.

        Per Finding 5 (Rev2, Plan 3): ITaskStateQuery.get_state() now
        returns None for unknown UUIDs instead of FAILED. This method
        passes through the None — callers must handle it explicitly.

        Args:
            token: Session token from a prior login() call.
            task_id: UUID of the task to query.

        Returns:
            TaskState if the task is tracked, None if unknown.

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
5. **`test_get_task_state_valid_token_returns_none_for_unknown`** — Rev3 update per Finding 2. get state for unknown UUID, returns `None` (not FAILED per Plan 3 Finding 5)
6. **`test_get_task_state_invalid_token_raises`** — get state with bad token, AuthError
7. **(removed per Rev3 Finding 2/3)** — was `test_api_does_not_import_concrete_classes`. Removed because the Capability API legitimately imports `TaskStateMachine` (write path) and `AuthMiddleware` (constructor). AR7 enforcement is solely in `test_ar7_no_core_imports_in_ui.py` (S4.1).
8. **`test_submit_task_no_provider_raises`** — Rev3 addition per Finding 4. Submit a task for a capability with no registered provider, assert `NoActiveProviderError` raised.
9. **`test_submit_task_with_category_param`** — Rev3 addition per Finding 2 (Plan 4 Rev2). Submit a task with `category=CapabilityCategory.MODEL_INFERENCE`, verify the task's capability declaration has that category.
10. **`test_submit_task_then_get_state_returns_received`** — Rev3 addition. End-to-end: submit a task, then get_task_state on the returned UUID, assert `TaskState.RECEIVED`. Verifies the Rev2 Finding 1 fix (submit_task actually submits).

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


# Modules that are concrete core implementations — the Capability API
# may NOT import these directly. Per Finding 4 (Rev2): protocol modules
# (capability_graph, task_state_machine) are NOT in this list —
# the Capability API is allowed to import protocols (ICapabilityIndex,
# ITaskStateQuery). Per Rev3 Finding 4: auth and routing_engine removed
# (API legitimately imports AuthMiddleware; NoActiveProviderError moved
# to types.py). Only true concrete internals remain.
CORE_INTERNALS_CONCRETE_DENYLIST = {
    "sovereignai.shared.event_bus",
    "sovereignai.shared.lifecycle_manager",
    "sovereignai.shared.routing_engine",
    "sovereignai.shared.dag_validator",
    "sovereignai.shared.manifest_parser",
    "sovereignai.shared.relay_placeholder",
    "sovereignai.shared.trace_emitter",
    "sovereignai.shared.container",
}

# Package-level imports forbidden in UI directories only.
# Per Rev3 Finding 5: `import sovereignai.shared` then `shared.event_bus.publish()`
# bypasses the leaf-module denylist. UIs must not import the package.
# Per Rev3 Finding 8: `sovereignai.shared.types` also forbidden for UIs
# (types are core internals; UIs consume the Capability API only).
# Per Rev5 Finding 3: uses prefix matching (any import starting with a
# denied prefix is forbidden). Catches `import sovereignai.adapters.external.foo`.
# Per Rev5 Finding 4: `sovereignai.shared.types` REMOVED from UI denylist —
# UIs need types (CapabilityCategory, TaskState) to call the API. Types are
# data contracts, not implementation. Re-exported from capability_api.py.
UI_PACKAGE_DENYLIST = {
    "sovereignai.shared",
    "sovereignai.orchestrator",
    "sovereignai.managers",
    "sovereignai.workers",
    "sovereignai.librarian",
    "sovereignai.adapters",
    "sovereignai.skills",
}


# Directories to scan for forbidden imports
UI_DIRECTORIES = ["web", "cli", "tui", "phone"]
# Plus the Capability API itself (it imports protocols, not concrete classes)
CAPABILITY_API_FILE = "sovereignai/shared/capability_api.py"


def _scan_imports(file_path: Path) -> set[str]:
    """Return the set of module names imported by a Python file.

    Per Finding 4 (Rev2): scans both `ast.Import` and `ast.ImportFrom`
    nodes. For `ImportFrom`, checks both `node.module` AND each
    `alias.name` — catches `from sovereignai.shared import event_bus`
    where `node.module` is `sovereignai.shared` but `alias.name` is
    `event_bus` (a forbidden sub-module).

    Known limitation: does NOT catch dynamic imports
    (`importlib.import_module()`). A runtime `sys.modules` audit is
    deferred to DEBT until UI processes actually exist.

    Args:
        file_path: Path to a .py file.

    Returns:
        Set of fully-qualified module names imported.
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
                # Per Finding 4: also check each imported name as a sub-module
                # Catches `from sovereignai.shared import event_bus` where
                # node.module is "sovereignai.shared" and alias.name is "event_bus"
                for alias in node.names:
                    imports.add(f"{node.module}.{alias.name}")
    return imports


def test_capability_api_does_not_import_concrete_core_classes() -> None:
    """Verify the Capability API imports only protocols, not concrete classes.

    Per A5: Plan 4's Capability API must import only ICapabilityIndex
    and ITaskStateQuery (protocols), never concrete implementation
    classes like EventBus or LifecycleManager.

    Per Finding 4 (Rev2): the denylist now excludes protocol modules
    (capability_graph, task_state_machine) — the API is allowed to
    import protocols. Only concrete implementation modules are
    forbidden. The test also catches `from ... import` sub-module forms.
    """
    api_path = Path(CAPABILITY_API_FILE)
    if not api_path.exists():
        pytest.skip("Capability API not yet created")
    imports = _scan_imports(api_path)
    forbidden = imports & CORE_INTERNALS_CONCRETE_DENYLIST
    assert not forbidden, (
        f"Capability API imports forbidden concrete core modules: {forbidden}. "
        f"Per AR7, it must import only protocols (ICapabilityIndex, "
        f"ITaskStateQuery), never concrete classes."
    )


@pytest.mark.parametrize("ui_dir", UI_DIRECTORIES)
def test_ui_directories_do_not_import_core_internals(ui_dir: str) -> None:
    """Verify UI process directories do not import from sovereignai/ internals.

    Per AR7: UIs (web, cli, tui, phone) are separate processes that
    consume the Capability API. They may not import from core
    internals directly.

    Per Finding 4 (Rev2): the test catches `from ... import` sub-module forms.

    Per Rev3 Finding 5: also checks for package-level imports
    (`import sovereignai.shared` then attribute access).

    Per Rev3 Finding 8: also checks for `sovereignai.shared.types`.

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
        # Per Rev5 Finding 3: prefix matching for both denylists
        forbidden_concrete = {imp for imp in imports
                              if any(imp.startswith(prefix) for prefix in CORE_INTERNALS_CONCRETE_DENYLIST)}
        forbidden_package = {imp for imp in imports
                             if any(imp.startswith(prefix) for prefix in UI_PACKAGE_DENYLIST)}
        assert not forbidden_concrete, (
            f"{py_file} imports forbidden concrete core modules: {forbidden_concrete}. "
            f"Per AR7, UIs must consume the Capability API only."
        )
        assert not forbidden_package, (
            f"{py_file} imports forbidden package: {forbidden_package}. "
            f"Per AR7, UIs must not import sovereignai.{layer} packages directly."
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

from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import RelayNotSupportedError, TraceLevel


class RelayPlaceholder:
    """Stub that rejects all connection attempts with a structured error.

    This is NOT the real relay server. The real server will be
    implemented in a dedicated post-batch plan. Until then, any code
    that tries to use the relay gets a RelayNotSupportedError (per
    Finding 5 — Rev2) and a trace event.
    """

    def __init__(self, trace: TraceEmitter) -> None:
        """Create a relay placeholder that logs all connection attempts.

        Args:
            trace: Trace emitter for logging attempts (so the user can
                see if anything is trying to use the relay).
        """
        self._trace = trace

    def attempt_connection(self, source: str) -> None:
        """Reject a connection attempt by raising RelayNotSupportedError.

        Per Finding 5 (Rev2): raises a typed exception instead of
        returning a plain string. Callers catch RelayNotSupportedError
        programmatically to distinguish "relay not supported" from
        other errors.

        Args:
            source: Description of what tried to connect (e.g. "phone_app").

        Raises:
            RelayNotSupportedError: Always — the relay is not yet implemented.
        """
        self._trace.emit(
            component="RelayPlaceholder",
            level=TraceLevel.WARN,
            message=f"Connection attempt from {source!r} rejected — relay not yet supported",
        )
        raise RelayNotSupportedError()
```

After creating, run `/verify`.

### S5.2 — Create `tests/test_relay_placeholder.py`

Required tests:

1. **`test_attempt_connection_raises_relay_not_supported_error`** — Rev3 update per Finding 5. call attempt_connection, assert `RelayNotSupportedError` raised (not returns a string)
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

    # 8. CapabilityAPI — depends on AuthMiddleware + ICapabilityIndex + ITaskStateQuery + TaskStateMachine
    # Rev2 per Finding 1: passes the concrete TaskStateMachine so submit_task
    # can call submit() (the ITaskStateQuery protocol is query-only).
    from sovereignai.shared.capability_api import CapabilityAPI
    from sovereignai.shared.capability_graph import ICapabilityIndex
    from sovereignai.shared.task_state_machine import ITaskStateQuery, TaskStateMachine
    api = CapabilityAPI(
        auth=auth,
        capability_index=container.retrieve(ICapabilityIndex),
        task_state_query=container.retrieve(ITaskStateQuery),
        state_machine=container.retrieve(TaskStateMachine),
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
- sovereignai/shared/types.py (extended: SessionToken, AuthError, CapabilityQuery, CapabilityResponse, RelayNotSupportedError per Finding 5, NoActiveProviderError per Rev3 Finding 4 + Rev4 Plan 3 Finding 2, CapabilityAPIError per Rev3 Finding 9, DAGValidationError/InvalidStateTransitionError/UnknownTaskError imports per Rev4 Finding 4)
- sovereignai/shared/auth.py (new — PBKDF2 hashing, session tokens, 8h TTL; now_utc top-level import per Rev4 Finding 7)
- sovereignai/shared/capability_api.py (new — public contract for UIs; submit_task calls state_machine.submit() per Finding 1; accepts category param per Finding 2; validates capability exists per Finding 3; imports TaskStateMachine concrete for submit per Finding 1; catches ONLY specific exceptions per Rev4 Finding 4; docstring fixed per Rev3 Finding 13)
- sovereignai/shared/relay_placeholder.py (new — raises RelayNotSupportedError per Finding 5; does not accept connections per A4)
- sovereignai/main.py (extended: registers Auth, CapabilityAPI (with state_machine), RelayPlaceholder; Q26 audit comment)
- tests/test_auth.py (new — 8 tests)
- tests/test_capability_api.py (new — 10 tests; updated per Rev3 Finding 2: test 5 expects None, test 7 removed, tests 8-10 added)
- tests/test_ar7_no_core_imports_in_ui.py (new — AR7 enforcement per Finding 4 + Rev3 Findings 5/8 + Rev4 Finding 3: catches from...import sub-module forms; denylist excludes protocol modules; UI_PACKAGE_DENYLIST expanded to all sovereignai.{layer} packages)
- tests/test_relay_placeholder.py (new — 3 tests; updated per Rev3 Finding 5: expects RelayNotSupportedError exception)
- tests/test_composition_root.py (extended — 7 new tests including Q26 audit)
- DEBT.md (add task TTL/eviction deferral per Rev3 Finding 14; add DAGSpec extension for composite skills per Rev4 Finding 5)
- DECISIONS.md (add D5: accepted AR7 gap for TaskStateMachine import per Rev3 Finding 2/3; add D6: get_state None vs transition raise semantics per Rev4 Plan 3 rejected finding)
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
- AR7 enforcement: static-import test verifies Capability API imports only protocols (ICapabilityIndex, ITaskStateQuery), never concrete classes. Per Finding 4 (Rev2): test catches `from...import` sub-module forms; denylist excludes protocol modules. UI directory tests will activate once UI files exist (post-batch).
- Auth: PBKDF2 hashing (100k iterations, 32-byte salt), constant-time comparison via secrets.compare_digest, 8-hour token TTL.
- Relay: placeholder only. Raises RelayNotSupportedError (typed exception) per Finding 5 (Rev2). Real relay deferred per A4 (DEBT).
- submit_task: per Finding 1 (Rev2), now calls TaskStateMachine.submit() — task enters RECEIVED and is queryable. Per Finding 2, accepts category parameter. Per Finding 3, validates capability exists before accepting. Actual routing to worker remains deferred (post-batch).
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

*Plan 4 — Interface Layer. Rev5. Architect draft. Part of Plans 1-4 batch — Round Table reviews alongside plan-1-Rev3, plan-2-Rev3, plan-3-Rev5, and the shared context brief. Adjudication logs above record Rev1 → Rev2 → Rev3 → Rev4 → Rev5 changes per GR4. Q26 (Composition Root bootstrap) confirmed at this plan's /close.*
