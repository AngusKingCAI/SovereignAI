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

    sequence: int          # Per Finding 16: monotonic sequence for SSE replay
    timestamp: str
    level: str
    component: str
    message: str
    trace_id: str
    task_id: str | None = None  # Per Finding 19: correlate traces with tasks
