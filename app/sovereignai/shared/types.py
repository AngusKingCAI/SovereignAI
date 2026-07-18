from __future__ import annotations

from contextvars import ContextVar, Token
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, NewType
from uuid import UUID, uuid4

from sovereignai.shared.types_base import CorrelationId

# ============================================================================
# Trace types (used by TraceEmitter in S3)
# ============================================================================

class TraceLevel(StrEnum):
    TRACE = "trace"
    DEBUG = "debug"
    INFO = "info"
    WARN = "warn"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass(frozen=True)
class TraceEvent:
    component: str          # e.g. "EventBus", "TraceEmitter", "main"
    level: TraceLevel
    message: str            # plain-English description of what happened
    timestamp: datetime     # UTC, timezone-aware
    correlation_id: CorrelationId    # groups events from the same task or request


# ============================================================================
# Event bus types (used by EventBus in S2)
# ============================================================================

# Typed channel identifier — NewType prevents passing a raw string where a
# Channel is expected. Channels are per-type: each event type has its own
# channel, and the bus guarantees in-order delivery per channel.
Channel = NewType("Channel", str)


@dataclass(frozen=True)
class Event:
    channel: Channel = field(default_factory=lambda: Channel("default"))
    correlation_id: CorrelationId = field(default_factory=lambda: CorrelationId(uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    version: int = 1
    trace_level: TraceLevel = TraceLevel.INFO
    payload: dict[str, Any] = field(default_factory=dict)

    @property
    def event_type(self) -> str:
        return self.channel


# Event versioning
_deprecated_events: dict[str, str] = {}
_logged_deprecations: set[str] = set()


def register_deprecated_event(old_type: str, new_type: str) -> None:
    """Register a deprecated event type mapping."""
    _deprecated_events[old_type] = new_type


def check_event_version(event: Event) -> Event:
    """Check event version and emit deprecation warning if needed."""
    if (
        event.channel in _deprecated_events
        and event.channel not in _logged_deprecations
    ):
        _logged_deprecations.add(event.channel)
        import warnings

        warnings.warn(
            f"Event type '{event.channel}' is deprecated. "
            f"Use '{_deprecated_events[event.channel]}' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
    return event


# ============================================================================
# Component identity (used by DI container in S4, capability graph in Plan 2)
# ============================================================================

ComponentId = NewType("ComponentId", str)  # e.g. "EventBus", "TraceEmitter"


# ============================================================================
# Helper functions
# ============================================================================

def now_utc() -> datetime:
    return datetime.now(UTC)


def new_correlation_id() -> CorrelationId:
    return CorrelationId(uuid4())


_current_correlation_id: ContextVar[CorrelationId | None] = ContextVar(
    "_current_correlation_id", default=None
)


def bind_correlation_id(cid: CorrelationId) -> Token:
    return _current_correlation_id.set(cid)


def current_correlation_id() -> CorrelationId | None:
    return _current_correlation_id.get()


def reset_correlation_id(token: Token) -> None:
    _current_correlation_id.reset(token)


def _is_valid_uuid(value: str) -> bool:
    try:
        UUID(value)
        return True
    except (ValueError, AttributeError, TypeError):
        return False


# ============================================================================
# Capability types (used by manifest parser + capability graph in Plan 2)
# ============================================================================

class CapabilityCategory(StrEnum):
    MODEL_INFERENCE = "model_inference"      # adapters: OpenAI, Ollama, etc.
    TOOL = "tool"                            # skills: websearch, calculator
    MEMORY = "memory"                        # backends: Postgres, Qdrant
    COMMUNICATION = "communication"          # gateways: voice, IM
    SKILL = "skill"                          # user-authored skills


class AdapterCapability(StrEnum):
    GPU_COMPUTE = "gpu_compute"
    GPU_MEMORY = "gpu_memory"
    CPU_INFERENCE = "cpu_inference"
    QUANTIZATION = "quantization"


@dataclass(frozen=True)
class CapabilityDeclaration:
    category: CapabilityCategory
    name: str                 # e.g. "text_generation", "websearch", "vector_search"
    version: str              # semver, e.g. "1.0.0" (Q8 MVP — full negotiation deferred)
    priority: int = 0         # higher = preferred; routing engine picks max


@dataclass(frozen=True)
class ComponentManifest:
    component_id: ComponentId  # e.g. "OpenAIAdapter", "WebSearchSkill"
    version: str  # component semver, e.g. "1.2.0"
    provides: tuple[CapabilityDeclaration, ...]  # capabilities this component offers
    requires: tuple[CapabilityDeclaration, ...]  # capabilities needed (empty for Plan 2 MVP)
    author: str  # provenance — who built it (P14)
    content_hash: str  # provenance — verified on install (P14)
    core: bool = False
    _source_path: str = ""  # Rev8: source path for first-party detection
    routing_priority: int = 1000  # lower = higher priority; default 1000
    category: CapabilityCategory | None = None  # Component category for skills/other components
    metadata: dict[str, Any] = field(default_factory=dict)


# ============================================================================
# Routing errors (used by RoutingEngine in S2; moved here per Rev4 Finding 2)
# ============================================================================

class NoActiveProviderError(Exception):

    def __init__(self, message: str = "No active provider for the requested capability") -> None:
        super().__init__(message)


class UnknownTaskError(Exception):

    def __init__(self, task_id: UUID) -> None:
        self.task_id = task_id
        super().__init__(f"Unknown task {task_id} — never submitted")


class InvalidStateTransitionError(Exception):

    def __init__(self, task_id: UUID, old_state: TaskState, new_state: TaskState) -> None:
        self.task_id = task_id
        self.old_state = old_state
        self.new_state = new_state
        super().__init__(f"Invalid transition {old_state} -> {new_state} for task {task_id}")


class DAGValidationError(Exception):
    pass


# ============================================================================
# DAG types (used by DAG validator + TaskStateMachine.submit in S4/S5)
# ============================================================================

@dataclass(frozen=True)
class DAGSpec:
    nodes: tuple[str, ...]
    edges: tuple[tuple[str, str], ...]
    input_types: dict[str, str]
    output_types: dict[str, str]


# ============================================================================
# Task types (used by task state machine in S4)
# ============================================================================

class TaskState(StrEnum):
    RECEIVED = "received"      # task entered the system, not yet queued
    QUEUED = "queued"          # task is waiting for a worker
    EXECUTING = "executing"    # a worker is running this task
    COMPLETE = "complete"      # task finished successfully
    FAILED = "failed"          # task failed; see traces for details


# Event channel for task state transitions (bus guarantees order)
TASK_STATE_CHANNEL = Channel("task_state")


@dataclass(frozen=True)
class TaskStateChanged:
    channel: Channel = field(default_factory=lambda: TASK_STATE_CHANNEL)
    correlation_id: CorrelationId = field(default_factory=lambda: CorrelationId(uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    task_id: UUID = field(default_factory=uuid4)
    old_state: TaskState = field(default_factory=lambda: TaskState.RECEIVED)
    new_state: TaskState = field(default_factory=lambda: TaskState.RECEIVED)
    version: int = 1
    trace_level: TraceLevel = TraceLevel.INFO


@dataclass(frozen=True)
class Task:
    task_id: UUID
    capability: CapabilityDeclaration    # what the task needs done
    payload: str                          # opaque payload (JSON or similar)
    submitted_at: datetime                # UTC, timezone-aware


# ============================================================================
# Lifecycle types (used by Lifecycle Manager in S3)
# ============================================================================

class ComponentStatus(StrEnum):
    ACTIVE = "active"                # healthy and available
    DEGRADED = "degraded"            # experiencing errors but still running
    CIRCUIT_BROKEN = "circuit_broken"  # unloaded due to >50 errors/10s
    STOPPED = "stopped"              # explicitly stopped, not available

    def is_available(self) -> bool:
        return self is ComponentStatus.ACTIVE


# ============================================================================
# Auth types (used by AuthMiddleware in S2)
# ============================================================================

@dataclass(frozen=True)
class SessionToken:
    token: str                # opaque string (e.g. UUID4 hex)
    username: str             # who authenticated
    issued_at: datetime       # UTC, timezone-aware
    expires_at: datetime      # UTC, timezone-aware


class AuthError(Exception):
    pass


# ============================================================================
# Capability API types (used by CapabilityAPI in S3)
# ============================================================================

@dataclass(frozen=True)
class CapabilityQuery:
    category: CapabilityCategory
    name: str


@dataclass(frozen=True)
class CapabilityResponse:
    query: CapabilityQuery
    providers: tuple[ComponentId, ...]    # component IDs that provide this capability


class RelayNotSupportedError(Exception):

    def __init__(
        self,
        message: str = "Remote transport not yet supported "
        "(relay server deferred per Plan 1-4 scope adjudication A4)",
    ) -> None:
        super().__init__(message)


# NoActiveProviderError already defined by Plan 3 S1.1 — no action needed.


class AdapterUnavailableError(Exception):
    pass


class NoHealthyAdapterError(Exception):
    pass


@dataclass(frozen=True)
class ComponentMetadata:
    component_id: str
    version: str
    capabilities: tuple[CapabilityDeclaration, ...]
    routing_priority: int


@dataclass(frozen=True)
class AdapterHealth:
    healthy: bool
    detail: str


class CapabilityAPIError(Exception):

    def __init__(self, message: str, cause: Exception | None = None) -> None:
        self.cause = cause
        super().__init__(message)


# ============================================================================
# Model types (used by database providers in Plan 17)
# ============================================================================

@dataclass(frozen=True)
class ModelEntry:
    org: str
    family: str
    version: str
    quant: str
    file_size_bytes: int
    vram_required_mb: int
    num_layers: int
    category: str
    source_db: str


@dataclass(frozen=True)
class ModelFilter:
    search: str | None = None
    category: str | None = None
    vram_fit_max_mb: int | None = None
    quant_level_min: str | None = None


@dataclass(frozen=True)
class DiskUsage:
    path: str
    total_gb: float
    used_gb: float
    free_gb: float
    percent: float


@dataclass(frozen=True)
class GpuInfo:
    name: str
    vram_total_mb: int
    vram_used_mb: int
    utilization_percent: float
    memory_type: str | None


@dataclass(frozen=True)
class HardwareSnapshot:
    cpu_percent: float
    ram_percent: float
    ram_used_gb: float
    ram_total_gb: float
    ram_available_gb: float
    memory_bandwidth_gbps: float
    disks: list[DiskUsage]
    gpus: list[GpuInfo]


# ============================================================================
# Memory backend types (used by CapabilityAPI for TUI memory panel)
# ============================================================================

@dataclass(frozen=True)
class MemoryBackendInfo:
    name: str
    type: str
    status: str
    capacity_mb: int
    used_mb: int


# ============================================================================
# Task state summary types (used by CapabilityAPI for TUI tasks panel)
# ============================================================================

@dataclass(frozen=True)
class TaskStateSummary:
    task_id: UUID
    state: TaskState
    worker_id: str | None
    submitted_at: datetime
    completed_at: datetime | None


# ============================================================================
# Memory query types (used by memory backends)
# ============================================================================

@dataclass(frozen=True)
class EpisodicQuery:
    session_id: str
    time_range: tuple[datetime, datetime] | None = None
    tags: list[str] | None = None


@dataclass(frozen=True)
class ProceduralQuery:
    skill_name: str | None = None
    capability_type: str | None = None


@dataclass(frozen=True)
class WorkingQuery:
    context_id: str
    max_items: int = 10


@dataclass(frozen=True)
class TraceQuery:
    correlation_id: str | None = None
    span_type: str | None = None
    task_id: str | None = None


@dataclass(frozen=True)
class EpisodicResult:
    id: str
    timestamp: float
    component: str
    task_id: str
    event_type: str
    data: str
    metadata: dict | None


@dataclass(frozen=True)
class ProceduralResult:
    id: str
    pattern: str
    confidence: float
    created_at: float


@dataclass(frozen=True)
class WorkingResult:
    id: str
    context_id: str
    data: dict


@dataclass(frozen=True)
class TraceResult:
    id: str
    timestamp: float
    component: str
    level: str
    message: str
    correlation_id: str
