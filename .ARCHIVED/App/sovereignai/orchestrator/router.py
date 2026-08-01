from __future__ import annotations

from typing import TYPE_CHECKING

from sovereignai.managers.base import DepartmentManager
from sovereignai.orchestrator.classifier import ClassificationResult, Department
from sovereignai.shared.container import DIContainer
from sovereignai.shared.trace_emitter import TraceEmitter, TraceLevel

if TYPE_CHECKING:
    pass


class DepartmentRouter:

    def __init__(self, container: DIContainer) -> None:
        self._container = container
        self._manager_cache: dict[Department, DepartmentManager] = {}
        self._department_map = {
            Department.CODING: "CodingManager",
            Department.RESEARCH: "ResearchManager",
            Department.EDUCATION: "EducationManager",
            Department.COMMUNICATION: "CommunicationManager",
            Department.SECURITY: "SecurityManager",
            Department.OPERATIONS: "OperationsManager",
        }

        trace = self._container.retrieve(TraceEmitter)
        trace.emit(
            component="DepartmentRouter",
            level=TraceLevel.INFO,
            message="DepartmentRouter initialized",
        )

    async def route(self, classification: ClassificationResult) -> DepartmentManager | None:
        if classification.department == Department.UNKNOWN:
            return None

        if classification.department in self._manager_cache:
            return self._manager_cache[classification.department]

        manager = await self._init_manager(classification.department)
        if manager is not None:
            self._manager_cache[classification.department] = manager
        return manager

    async def _init_manager(self, department: Department) -> DepartmentManager | None:
        manager_name = self._department_map.get(department)
        if manager_name is None:
            return None

        try:
            from sovereignai.managers.coding import CodingManager
            from sovereignai.shared.trace_emitter import TraceEmitter, TraceLevel

            trace = self._container.retrieve(TraceEmitter)

            if department == Department.CODING:
                manager = self._container.retrieve(CodingManager)
                trace.emit(
                    component="DepartmentRouter",
                    level=TraceLevel.INFO,
                    message=f"Initialized {manager_name}"
                )
                return manager
            else:
                trace.emit(
                    component="DepartmentRouter",
                    level=TraceLevel.WARN,
                    message=f"{manager_name} not yet implemented"
                )
                return None
        except Exception:
            from sovereignai.shared.trace_emitter import TraceEmitter, TraceLevel

            trace = self._container.retrieve(TraceEmitter)
            trace.emit(
                component="DepartmentRouter",
                level=TraceLevel.ERROR,
                message=f"Failed to initialize {manager_name}"
            )
            return None

    async def shutdown(self) -> None:
        for department, manager in self._manager_cache.items():
            try:
                if hasattr(manager, 'close'):
                    await manager.close()
            except Exception:
                from sovereignai.shared.trace_emitter import TraceEmitter, TraceLevel

                trace = self._container.retrieve(TraceEmitter)
                trace.emit(
                    component="DepartmentRouter",
                    level=TraceLevel.ERROR,
                    message=f"Failed to shutdown {department.value} manager"
                )
        self._manager_cache.clear()
