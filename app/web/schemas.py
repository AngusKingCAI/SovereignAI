from typing import TYPE_CHECKING, Generic, TypeVar

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    pass

T = TypeVar("T")


class CapabilityResponseDTO(BaseModel):

    id: str
    name: str
    category: str
    description: str
    priority: int
    input_schema: str | None = None   # Per Finding 21: include schemas
    output_schema: str | None = None  # Per Finding 21: include schemas


class TaskSubmitDTO(BaseModel):

    category: str
    capability_name: str
    payload: str


class TaskResponseDTO(BaseModel):

    task_id: str
    state: str
    result: str | None = None
    error: str | None = None


class TraceEventDTO(BaseModel):

    timestamp: str
    level: str
    component: str
    correlation_id: str
    message: str


class DatabaseResponseDTO(BaseModel):

    name: str
    status: str
    models: list[str]


class ServiceResponseDTO(BaseModel):

    name: str
    status: str
    pid: int | None = None
    port: int | None = None


class DiskUsageDTO(BaseModel):

    path: str
    total_gb: float
    used_gb: float
    free_gb: float
    percent: float


class GpuInfoDTO(BaseModel):

    name: str
    vram_total_mb: int
    vram_used_mb: int
    utilization_percent: float
    memory_type: str | None = None


class HardwareSnapshotDTO(BaseModel):

    cpu_percent: float
    ram_percent: float
    ram_used_gb: float
    ram_total_gb: float
    ram_available_gb: float
    memory_bandwidth_gbps: float
    disks: list[DiskUsageDTO]
    gpus: list[GpuInfoDTO]


class ModelEntryDTO(BaseModel):

    org: str
    family: str
    version: str
    quant: str
    file_size_bytes: int
    vram_required_mb: int
    num_layers: int
    category: str
    source_db: str
    tok_s_estimated: float | None = None


class FirstRunStatusDTO(BaseModel):

    healthy_adapters: list[str]
    instructions: str


class SkillListDTO(BaseModel):

    skills: list[dict]


class SkillExecuteDTO(BaseModel):

    skill_id: str
    args: dict


class SkillResultDTO(BaseModel):

    output: str
    error: str | None
    execution_time_ms: int


class EventTypeDTO(BaseModel):

    event_type: str
    version: int
    description: str


class EventTypeListDTO(BaseModel):

    event_types: list[EventTypeDTO]


class SubscriptionDTO(BaseModel):

    event_type: str
    handler_id: str
    queue_maxsize: int


class SubscriptionListDTO(BaseModel):

    subscriptions: list[SubscriptionDTO]


class AgentTaskSubmitDTO(BaseModel):

    task_description: str
    tools: list[dict]
    context: str | None = None


class AgentTaskResponseDTO(BaseModel):

    task_id: str
    status: str
    output: str | None = None
    error: str | None = None
    trace: list[str] = []


class AgentStepDTO(BaseModel):

    step_number: int
    thought: str | None = None
    action: str | None = None
    observation: str | None = None


class DepartmentListDTO(BaseModel):

    departments: list[dict]


class DepartmentTaskSubmitDTO(BaseModel):

    task_description: str


class DepartmentTaskResponseDTO(BaseModel):

    task_id: str
    status: str
    output: str | None = None
    error: str | None = None


class SymbolMapResponseDTO(BaseModel):

    status: str
    health: str
    symbols: list[dict] = []
    error: str | None = None


class OptionsGetResponseDTO(BaseModel):

    key: str
    value: str | int | float | bool | dict | list | None


class OptionsListResponseDTO(BaseModel):

    options: dict[str, str | int | float | bool | dict | list | None]


class OptionsSetRequestDTO(BaseModel):

    value: str | int | float | bool | dict | list | None


class OptionsSetResponseDTO(BaseModel):

    key: str
    value: str | int | float | bool | dict | list | None


class OptionsDeleteResponseDTO(BaseModel):

    deleted: bool


# Plan 31 DTOs


class OrchestratorResponse(BaseModel):
    task_id: str
    status: str
    response_text: str
    error: str | None = None
    created_at: str  # ISO 8601


class MessageRequest(BaseModel):
    content: str
    session_id: str | None = None


class CircuitState(BaseModel):
    worker_id: str
    state: str
    error_count: int
    last_error: str | None = None


class CircuitStateList(BaseModel):
    circuits: list[CircuitState]


class SubsystemHealth(BaseModel):
    name: str
    kind: str = Field(..., pattern="^(worker|adapter|hardware|core)$")
    status: str = Field(..., pattern="^(HEALTHY|DEGRADED|UNHEALTHY)$")
    details: str | None = None


class HealthSnapshot(BaseModel):
    status: str = Field(..., pattern="^(READY|DEGRADED)$")
    subsystems: list[SubsystemHealth]
    cache_age_ms: int


class LoginRequest(BaseModel):
    username: str
    password: str
    setup_token: str | None = None


class LoginResponse(BaseModel):
    expires_at: str  # ISO 8601
    username: str


class OptionsUpdate(BaseModel):
    key: str
    value: str


class ModelQuery(BaseModel):
    model_id: str | None = None
    provider: str | None = None


class SyncTrigger(BaseModel):
    model_id: str


class TraceEvent(BaseModel):
    timestamp: str
    level: str
    source: str
    message: str
    event_type: str | None = None


class GraphNodeDTO(BaseModel):
    uuid: str
    name: str
    type: str
    attributes: dict


class GraphEdgeDTO(BaseModel):
    src_id: str
    dst_id: str
    type: str
    attributes: dict


class GraphQueryRequest(BaseModel):
    query_type: str = Field(..., pattern="^(entity_search|relation_traversal)$")
    entity_name: str | None = None
    entity_type: str | None = None
    relation_type: str | None = None
    max_depth: int = 1


class GraphQueryResponse(BaseModel):
    nodes: list[GraphNodeDTO]
    edges: list[GraphEdgeDTO]


class EpisodicEventDTO(BaseModel):
    id: int
    event_type: str
    timestamp: str
    correlation_id: str | None = None
    summary: str


class EpisodicQueryRequest(BaseModel):
    event_type: str | None = None
    since: str | None = None  # ISO 8601
    until: str | None = None  # ISO 8601
    offset: int = 0
    limit: int = 500


class EpisodicQueryResponse(BaseModel):
    events: list[EpisodicEventDTO]
    total_count: int
    offset: int
    limit: int


class TaskEventDTO(BaseModel):
    event_id: int
    task_id: str
    event_type: str
    timestamp: str
    details: dict | None = None


class TaskListResponse(BaseModel):
    events: list[TaskEventDTO]
    total_count: int
    next_event_id: int | None = None
    page_size: int


class LifecycleEventDTO(BaseModel):
    event_type: str
    timestamp: str
    server_pid: int | None = None
    instance_uuid: str | None = None
    drain_timeout_seconds: int | None = None


class TraceLogRequest(BaseModel):
    event_type: str | None = None
    since: str | None = None
    until: str | None = None
    offset: int = 0
    limit: int = 500


class TraceLogResponse(BaseModel):
    events: list[TraceEvent]
    total_count: int
    offset: int
    limit: int


class LifecycleReadyResponse(BaseModel):
    ready: bool
    server_pid: int
    instance_uuid: str


class MemoryNotReadyResponse(BaseModel):
    error_code: str = Field(default="memory_not_ready", pattern="^memory_not_ready$")
    message: str = "Memory subsystem still loading"
    retry_after_seconds: int = 5


class MergeConflictDTO(BaseModel):
    conflict_id: str
    entity_name: str
    entity_type: str
    canonical_uuid: str
    candidate_uuids: list[str]
    first_observed_at: str  # ISO 8601
    resolution_status: str = Field(..., pattern="^(unresolved|suppressed_by_dedup)$")


class MergeConflictPage(BaseModel):
    items: list[MergeConflictDTO]
    total_count: int
    offset: int
    limit: int


class ModelSummary(BaseModel):
    model_id: str
    provider: str
    sync_status: str


class ModelListResponse(BaseModel):
    models: list[ModelSummary]
    total_count: int


class MessagingAuditEntryDTO(BaseModel):
    id: str
    source_department: str
    target_department: str
    content_preview: str
    timestamp: str  # ISO 8601


class AuditEntry(BaseModel):
    id: str
    timestamp: str
    event_type: str
    details: dict


class AuditPage(BaseModel, Generic[T]):
    items: list[T]
    total_count: int
    offset: int
    limit: int


class OrchestratorStatus(BaseModel):
    state: str
    uptime_seconds: float
    tasks_completed: int
    tasks_failed: int


class CrossDepartmentMessage(BaseModel):
    source_department: str
    target_department: str
    content: str
    correlation_id: str
