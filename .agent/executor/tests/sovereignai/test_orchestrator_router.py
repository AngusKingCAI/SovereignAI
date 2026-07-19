from __future__ import annotations

import pytest
from sovereignai.managers.base import DepartmentManager
from sovereignai.orchestrator.classifier import ClassificationResult, Department
from sovereignai.orchestrator.router import DepartmentRouter
from sovereignai.shared.container import DIContainer
from sovereignai.shared.trace_emitter import TraceEmitter


class MockDepartmentManager(DepartmentManager):

    def __init__(self, container: DIContainer) -> None:
        super().__init__(container)
        self.closed = False

    async def _build_context_impl(self, task) -> dict:
        return {}

    async def build_context(self, task) -> dict | None:
        return await self._build_context_impl(task)

    def validate(self, deliverable):
        from sovereignai.managers.types import ValidationResult
        return ValidationResult(passed=True)

    async def execute_task(self, task):
        from sovereignai.managers.types import Deliverable
        return Deliverable(success=True, output="mock output", validation_failure=None)

    async def close(self) -> None:
        self.closed = True


@pytest.mark.asyncio
async def test_router_coding_department() -> None:
    container = DIContainer()
    trace = TraceEmitter()
    container.register_singleton(TraceEmitter, trace)

    from sovereignai.managers.coding import CodingManager
    manager = CodingManager(container)
    container.register_singleton(CodingManager, manager)

    router = DepartmentRouter(container)
    classification = ClassificationResult(
        department=Department.CODING,
        confidence=0.9,
        metadata={}
    )

    result = await router.route(classification)
    assert result is not None
    assert isinstance(result, CodingManager)


@pytest.mark.asyncio
async def test_router_unknown_department() -> None:
    container = DIContainer()
    trace = TraceEmitter()
    container.register_singleton(TraceEmitter, trace)

    router = DepartmentRouter(container)
    classification = ClassificationResult(
        department=Department.UNKNOWN,
        confidence=0.0,
        metadata={}
    )

    result = await router.route(classification)
    assert result is None


@pytest.mark.asyncio
async def test_router_unimplemented_department() -> None:
    container = DIContainer()
    trace = TraceEmitter()
    container.register_singleton(TraceEmitter, trace)

    router = DepartmentRouter(container)
    classification = ClassificationResult(
        department=Department.RESEARCH,
        confidence=0.8,
        metadata={}
    )

    result = await router.route(classification)
    assert result is None


@pytest.mark.asyncio
async def test_router_caching() -> None:
    container = DIContainer()
    trace = TraceEmitter()
    container.register_singleton(TraceEmitter, trace)

    from sovereignai.managers.coding import CodingManager
    manager = CodingManager(container)
    container.register_singleton(CodingManager, manager)

    router = DepartmentRouter(container)
    classification = ClassificationResult(
        department=Department.CODING,
        confidence=0.9,
        metadata={}
    )

    result1 = await router.route(classification)
    result2 = await router.route(classification)

    assert result1 is result2


@pytest.mark.asyncio
async def test_router_shutdown() -> None:
    container = DIContainer()
    trace = TraceEmitter()
    container.register_singleton(TraceEmitter, trace)

    mock_manager = MockDepartmentManager(container)
    from sovereignai.managers.coding import CodingManager
    container.register_singleton(CodingManager, mock_manager)

    router = DepartmentRouter(container)
    classification = ClassificationResult(
        department=Department.CODING,
        confidence=0.9,
        metadata={}
    )

    await router.route(classification)
    await router.shutdown()

    assert mock_manager.closed
