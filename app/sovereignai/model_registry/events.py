from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class SyncCompletedEvent(BaseModel):
    """Event emitted when a sync operation completes."""

    status: Literal["success", "failed"]
    provider_id: str
    timestamp: datetime
    error_class: str | None = None
    models_count: int | None = None
