from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ServiceStatus:
    running: bool
    pid: int | None
    port: int | None


class ServiceProvider(Protocol):
    name: str

    def start(self) -> None:
        ...

    def stop(self) -> None:
        ...

    def health_check(self) -> ServiceStatus:
        ...


class ServiceNotFoundError(Exception):

    def __init__(self, message: str = "Service not found") -> None:
        super().__init__(message)


class ServiceStartError(Exception):

    def __init__(self, message: str = "Failed to start service") -> None:
        super().__init__(message)
