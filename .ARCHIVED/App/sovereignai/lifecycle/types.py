from __future__ import annotations

from enum import Enum


class LifecycleState(Enum):
    INITIALIZING = "INITIALIZING"
    HEALTH_CHECKING = "HEALTH_CHECKING"
    READY = "READY"
    DEGRADED = "DEGRADED"
    SHUTTING_DOWN = "SHUTTING_DOWN"
    STOPPED = "STOPPED"


class LifecycleError(Exception):
    pass
