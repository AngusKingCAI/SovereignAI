from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from sovereignai.managers.exceptions import SymbolMapUnavailableError
from sovereignai.managers.types import Deliverable, ValidationResult
from sovereignai.shared.container import DIContainer

if TYPE_CHECKING:
    pass


class DepartmentManager(ABC):

    def __init__(self, container: DIContainer) -> None:
        self._container = container

    @abstractmethod
    async def build_context(self, task: Any) -> dict[str, Any] | None:
        try:
            context = await self._build_context_impl(task)
            return context
        except SymbolMapUnavailableError:
            from sovereignai.shared.trace_emitter import TraceEmitter
            from sovereignai.shared.types import TraceLevel

            trace = self._container.retrieve(TraceEmitter)
            trace.emit(
                component="department",
                level=TraceLevel.WARN,
                message="Context build failed (SymbolMap unavailable)"
            )
            return None

    @abstractmethod
    async def _build_context_impl(self, task: Any) -> dict[str, Any]:
        ...

    @abstractmethod
    def validate(self, deliverable: Deliverable) -> ValidationResult:
        ...

    @abstractmethod
    async def execute_task(self, task: Any) -> Deliverable:
        ...
