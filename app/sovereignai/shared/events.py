from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from sovereignai.shared.types import Channel, CorrelationId, Event, TraceLevel


@dataclass(frozen=True)
class TaskCreated:
    task_id: UUID = field(default_factory=uuid4)
    capability_name: str = ""
    capability_category: str = ""
    payload: str = ""
    submitted_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    channel: Channel = field(default_factory=lambda: Channel("task.created"))
    correlation_id: CorrelationId = field(default_factory=lambda: CorrelationId(uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    version: int = 1
    trace_level: TraceLevel = TraceLevel.INFO


@dataclass(frozen=True)
class TaskUpdated:
    task_id: UUID = field(default_factory=uuid4)
    old_state: str = ""
    new_state: str = ""
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    channel: Channel = field(default_factory=lambda: Channel("task.updated"))
    correlation_id: CorrelationId = field(default_factory=lambda: CorrelationId(uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    version: int = 1
    trace_level: TraceLevel = TraceLevel.INFO


@dataclass(frozen=True)
class AgentStep:
    agent_id: str = ""
    step_number: int = 0
    step_type: str = ""
    status: str = ""
    metadata: dict[str, Any] | None = None
    channel: Channel = field(default_factory=lambda: Channel("agent.step"))
    correlation_id: CorrelationId = field(default_factory=lambda: CorrelationId(uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    version: int = 1
    trace_level: TraceLevel = TraceLevel.INFO


@dataclass(frozen=True)
class HardwareStatus:
    cpu_percent: float = 0.0
    ram_percent: float = 0.0
    disk_usage: list[dict[str, Any]] = field(default_factory=list)
    gpu_status: list[dict[str, Any]] | None = None
    channel: Channel = field(default_factory=lambda: Channel("hardware.status"))
    correlation_id: CorrelationId = field(default_factory=lambda: CorrelationId(uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    version: int = 1
    trace_level: TraceLevel = TraceLevel.INFO
