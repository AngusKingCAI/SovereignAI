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
