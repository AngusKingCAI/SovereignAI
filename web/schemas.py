from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    pass


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

