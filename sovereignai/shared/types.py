"""Core domain types shared across all SovereignAI components.

This module is the single source of truth for domain types. All other
modules import from here — never define duplicate types elsewhere.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import NewType
from uuid import UUID, uuid4

# ============================================================================
# Trace types (used by TraceEmitter in S3)
# ============================================================================

class TraceLevel(StrEnum):
    """Severity level for trace events, ordered from least to most severe."""
    TRACE = "trace"
    DEBUG = "debug"
    INFO = "info"
    WARN = "warn"
    ERROR = "error"


@dataclass(frozen=True)
class TraceEvent:
    """Single observability event emitted by a component via TraceEmitter.

    Immutable so events can be safely shared across threads and stored in
    trace memory without risk of mutation.
    """
    component: str          # e.g. "EventBus", "TraceEmitter", "main"
    level: TraceLevel
    message: str            # plain-English description of what happened
    timestamp: datetime     # UTC, timezone-aware (per OR20)
    correlation_id: UUID    # groups events from the same task or request


# ============================================================================
# Event bus types (used by EventBus in S2)
# ============================================================================

# Typed channel identifier — NewType prevents passing a raw string where a
# Channel is expected. Channels are per-type: each event type has its own
# channel, and the bus guarantees in-order delivery per channel (per A9).
Channel = NewType("Channel", str)


@dataclass(frozen=True)
class Event:
    """Base type for all events published on the event bus.

    Subclasses (defined in Plans 2-4) add payload fields. The base type
    carries only routing metadata. Frozen so events are immutable once
    published — a subscriber cannot modify an event before another
    subscriber sees it.
    """
    channel: Channel
    correlation_id: UUID
    timestamp: datetime     # UTC, timezone-aware (per OR20)


# ============================================================================
# Component identity (used by DI container in S4, capability graph in Plan 2)
# ============================================================================

ComponentId = NewType("ComponentId", str)  # e.g. "EventBus", "TraceEmitter"


# ============================================================================
# Helper functions
# ============================================================================

def now_utc() -> datetime:
    """Return the current time in UTC with timezone awareness to avoid naive datetime issues.

    Use this instead of datetime.now() or datetime.utcnow() — both are
    forbidden per OR20 (naive/aware datetime mixing caused L6).
    """
    return datetime.now(UTC)


def new_correlation_id() -> UUID:
    """Generate a fresh UUID4 for correlating events across components in the system."""
    return uuid4()


def _is_valid_uuid(value: str) -> bool:
    """Check if a string is a valid UUID format without raising an exception.

    This helper is used for validation when parsing task IDs from external
    sources like trace storage. It returns False for invalid formats instead
    of raising ValueError, allowing graceful degradation.
    """
    try:
        UUID(value)
        return True
    except (ValueError, AttributeError, TypeError):
        return False


# ============================================================================
# Capability types (used by manifest parser + capability graph in Plan 2)
# ============================================================================

class CapabilityCategory(StrEnum):
    """Category of capability a component provides.

    Adapters declare model categories; skills declare tool categories;
    memory backends declare storage categories. The capability graph
    routes requests to components based on these declarations.
    """
    MODEL_INFERENCE = "model_inference"      # adapters: OpenAI, Ollama, etc.
    TOOL = "tool"                            # skills: websearch, calculator
    MEMORY = "memory"                        # backends: Postgres, Qdrant
    COMMUNICATION = "communication"          # gateways: voice, IM


@dataclass(frozen=True)
class CapabilityDeclaration:
    """Single capability a component claims to provide.

    Frozen so declarations can be safely shared and compared across
    threads. The priority field lets the routing engine (Plan 3)
    pick the highest-priority provider when multiple components
    satisfy the same capability.
    """
    category: CapabilityCategory
    name: str                 # e.g. "text_generation", "websearch", "vector_search"
    version: str              # semver, e.g. "1.0.0" (Q8 MVP — full negotiation deferred)
    priority: int = 0         # higher = preferred; routing engine picks max


@dataclass(frozen=True)
class ComponentManifest:
    """Parsed manifest declaring what a component provides and needs.

    Read from a TOML file at startup (per Q1 resolution: static manifest
    declaring capability categories plus a protocol/interface). Frozen
    so manifests are immutable once loaded.
    """
    component_id: ComponentId  # e.g. "OpenAIAdapter", "WebSearchSkill"
    version: str  # component semver, e.g. "1.2.0"
    provides: tuple[CapabilityDeclaration, ...]  # capabilities this component offers
    requires: tuple[CapabilityDeclaration, ...]  # capabilities needed (empty for Plan 2 MVP)
    author: str                           # provenance — who built it (P14)
    content_hash: str                     # provenance — verified on install (P14)


# ============================================================================
# Routing errors (used by RoutingEngine in S2; moved here per Rev4 Finding 2)
# ============================================================================

class NoActiveProviderError(Exception):
    """Raised when no active component provides the requested capability.

    Per Rev4 Finding 2: defined here (shared/types.py) so both
    routing_engine.py and capability_api.py import from the same location.
    """

    def __init__(self, message: str = "No active provider for the requested capability") -> None:
        """Create a no-active-provider error instance with a descriptive error message."""
        super().__init__(message)


class UnknownTaskError(Exception):
    """Raised when an operation references a task_id that was never submitted.

    Per Rev5 Finding 1: moved from task_state_machine.py to types.py.
    """

    def __init__(self, task_id: UUID) -> None:
        """Create an error instance for an unknown task identifier value."""
        self.task_id = task_id
        super().__init__(f"Unknown task {task_id} — never submitted")


class InvalidStateTransitionError(Exception):
    """Raised when a task state transition violates the state machine's rules.

    Per Rev5 Finding 1: moved from task_state_machine.py to types.py.
    """

    def __init__(self, task_id: UUID, old_state: TaskState, new_state: TaskState) -> None:
        """Create an error instance describing an invalid state transition attempt."""
        self.task_id = task_id
        self.old_state = old_state
        self.new_state = new_state
        super().__init__(f"Invalid transition {old_state} -> {new_state} for task {task_id}")


class DAGValidationError(Exception):
    """Raised when a skill DAG has a cycle or a type mismatch.

    Per Rev5 Finding 1: moved from dag_validator.py to types.py.
    """


# ============================================================================
# DAG types (used by DAG validator + TaskStateMachine.submit in S4/S5)
# ============================================================================

@dataclass(frozen=True)
class DAGSpec:
    """Specification of a composite skill's directed acyclic graph.

    Per Rev3 Finding 6: defined here so TaskStateMachine.submit() can
    accept it as a typed parameter. Frozen so the spec is immutable
    once constructed — a composite skill's DAG cannot be mutated after
    submission.

    Attributes:
        nodes: Tuple of skill node IDs (e.g. ("open_browser", "register_email")).
        edges: Tuple of (source, target) pairs meaning source's output
            feeds into target's input.
        input_types: Map of node ID -> type name it requires as input.
        output_types: Map of node ID -> type name it produces as output.
    """
    nodes: tuple[str, ...]
    edges: tuple[tuple[str, str], ...]
    input_types: dict[str, str]
    output_types: dict[str, str]


# ============================================================================
# Task types (used by task state machine in S4)
# ============================================================================

class TaskState(StrEnum):
    """Lifecycle state of a single task, from receipt to completion.

    The task state machine transitions: RECEIVED → QUEUED → EXECUTING
    → COMPLETE or FAILED. Transitions are published as events on the
    event bus so subscribers (e.g. the Capability API in Plan 4) can
    react to state changes.
    """
    RECEIVED = "received"      # task entered the system, not yet queued
    QUEUED = "queued"          # task is waiting for a worker
    EXECUTING = "executing"    # a worker is running this task
    COMPLETE = "complete"      # task finished successfully
    FAILED = "failed"          # task failed; see traces for details


# Event channel for task state transitions (per A9 — bus guarantees order)
TASK_STATE_CHANNEL = Channel("task_state")


@dataclass(frozen=True)
class TaskStateChanged(Event):
    """Event published when a task transitions between states.

    Frozen so subscribers receive an immutable snapshot. Subscribers
    cannot modify the event before another subscriber sees it.
    """
    task_id: UUID
    old_state: TaskState
    new_state: TaskState


@dataclass(frozen=True)
class Task:
    """A unit of work submitted to the system for execution.

    Frozen so a task cannot be mutated after submission. The state
    machine tracks transitions externally (via TaskStateChanged events)
    rather than mutating the Task itself.
    """
    task_id: UUID
    capability: CapabilityDeclaration    # what the task needs done
    payload: str                          # opaque payload (JSON or similar)
    submitted_at: datetime                # UTC, timezone-aware (per OR20)


# ============================================================================
# Lifecycle types (used by Lifecycle Manager in S3)
# ============================================================================

class ComponentStatus(StrEnum):
    """Health status of a registered component, used by the routing engine.

    The Lifecycle Manager tracks status; the Routing Engine queries it
    to skip degraded or circuit-broken components (per A1).
    """
    ACTIVE = "active"                # healthy and available
    DEGRADED = "degraded"            # experiencing errors but still running
    CIRCUIT_BROKEN = "circuit_broken"  # unloaded due to >50 errors/10s (AR16)
    STOPPED = "stopped"              # explicitly stopped, not available

    def is_available(self) -> bool:
        """Return True if a component in this state can accept new work.

        Only ACTIVE components are available. DEGRADED components may
        be running existing tasks but should not receive new ones.
        CIRCUIT_BROKEN and STOPPED are never available.
        """
        return self is ComponentStatus.ACTIVE


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

    def __init__(
        self,
        message: str = "Remote transport not yet supported "
        "(relay server deferred per Plan 1-4 scope adjudication A4)",
    ) -> None:
        """Create a relay-not-supported error instance with a descriptive error message.

        Args:
            message: Human-readable explanation of why the relay is not available.
        """
        super().__init__(message)


# NoActiveProviderError already defined by Plan 3 S1.1 — no action needed.


class CapabilityAPIError(Exception):
    """Raised when the Capability API encounters an internal error.

    Per Rev3 Finding 9: wraps lower-level errors (DAGValidationError,
    InvalidStateTransitionError, UnknownTaskError) so callers get a
    single typed exception from the API rather than propagating core
    internals.
    """

    def __init__(self, message: str, cause: Exception | None = None) -> None:
        """Create a CapabilityAPIError instance wrapping an optional cause exception value.

        Args:
            message: Human-readable explanation of what failed.
            cause: The underlying exception, if any.
        """
        self.cause = cause
        super().__init__(message)
