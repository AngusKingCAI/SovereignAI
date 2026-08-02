from __future__ import annotations

import datetime
import uuid
from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class MessageType(StrEnum):
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ERROR = "error"


@dataclass(frozen=True)
class CrossDepartmentMessage:
    sender: str
    recipient: str
    payload: dict[str, Any]
    correlation_id: uuid.UUID
    timestamp: datetime.datetime
    message_type: MessageType
