from __future__ import annotations

from contextvars import ContextVar, Token
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import NewType
from uuid import UUID, uuid4

# ============================================================================
# Trace types (used by TraceEmitter in S3)
# ============================================================================

class TraceLevel(StrEnum):
    TRACE = "trace"
    DEBUG = "debug"
    INFO = "info"
    WARN = "warn"
    ERROR = "error"


@dataclass(frozen=True)
class TraceEvent:
    component: str          # e.g. "EventBus", "TraceEmitter", "main"
    level: TraceLevel
    message: str            # plain-English description of what happened
    timestamp: datetime     # UTC, timezone-aware
    correlation_id: UUID    # groups events from the same task or request


# ============================================================================
# Event bus types (used by EventBus in S2)
# ============================================================================

# Typed channel identifier — NewType prevents passing a raw string where a
# Channel is expected. Channels are per-type: each event type has its own
# channel, and the bus guarantees in-order delivery per channel.
Channel = NewType("Channel", str)


@dataclass(frozen=True)
class Event:
    channel: Channel
    correlation_id: UUID
    timestamp: datetime     # UTC, timezone-aware


# ============================================================================
# Component identity (used by DI container in S4, capability graph in Plan 2)
# ============================================================================

ComponentId = NewType("ComponentId", str)  # e.g. "EventBus", "TraceEmitter"


# ============================================================================
# Helper functions
# ============================================================================

def now_utc() -> datetime:
    return datetime.now(UTC)


def new_correlation_id() -> UUID:
    return uuid4()


_current_correlation_id: ContextVar[UUID | None] = ContextVar(
    "_current_correlation_id", default=None
)


def bind_correlation_id(cid: UUID) -> Token:
    return _current_correlation_id.set(cid)


def current_correlation_id() -> UUID | None:
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
    routing_priority: int = 1000  # OR70: lower = higher priority; default 1000


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
class TaskStateChanged(Event):
    task_id: UUID
    old_state: TaskState
    new_state: TaskState


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
    CIRCUIT_BROKEN = "circuit_broken"  # unloaded due to >50 errors/10s (AR16)
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
