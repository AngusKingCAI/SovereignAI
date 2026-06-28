from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    pass


class CapabilityResponseDTO(BaseModel):
    """Data transfer object for capability responses."""

    id: str
    name: str
    category: str
    description: str
    priority: int
    input_schema: str | None = None   # Per Finding 21: include schemas
    output_schema: str | None = None  # Per Finding 21: include schemas


class TaskSubmitDTO(BaseModel):
    """Data transfer object for task submission."""

    category: str
    capability_name: str
    payload: str


class TaskResponseDTO(BaseModel):
    """Data transfer object for task responses."""

    task_id: str
    state: str
    result: str | None = None
    error: str | None = None


class TraceEventDTO(BaseModel):
    """Data transfer object for trace events."""

    sequence: int          # Per Finding 16: monotonic sequence for SSE replay
    timestamp: str
    level: str
    component: str
    message: str
    trace_id: str
    task_id: str | None = None  # Per Finding 19: correlate traces with tasks
