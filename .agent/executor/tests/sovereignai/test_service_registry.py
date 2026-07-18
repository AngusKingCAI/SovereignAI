from __future__ import annotations

from services.base import ServiceProvider, ServiceStatus
from sovereignai.shared.service_registry import ServiceRegistry
from sovereignai.shared.trace_emitter import TraceEmitter


class MockServiceProvider(ServiceProvider):
    def __init__(self, name: str) -> None:
        self.name = name
        self.started = False

    def start(self) -> None:
        self.started = True

    def stop(self) -> None:
        self.started = False

    def health_check(self) -> ServiceStatus:
        return ServiceStatus(running=self.started, pid=1234, port=8080)


def test_register_and_retrieve() -> None:
    trace = TraceEmitter()
    registry = ServiceRegistry(trace)
    provider = MockServiceProvider("test_service")
    registry.register("test_service", provider)
    assert registry.get_service("test_service") is provider


def test_list_services() -> None:
    trace = TraceEmitter()
    registry = ServiceRegistry(trace)
    registry.register("svc1", MockServiceProvider("svc1"))
    registry.register("svc2", MockServiceProvider("svc2"))
    assert set(registry.list_services()) == {"svc1", "svc2"}


def test_start_all() -> None:
    trace = TraceEmitter()
    registry = ServiceRegistry(trace)
    svc1 = MockServiceProvider("svc1")
    svc2 = MockServiceProvider("svc2")
    registry.register("svc1", svc1)
    registry.register("svc2", svc2)
    registry.start_all()
    assert svc1.started
    assert svc2.started


def test_stop_all() -> None:
    trace = TraceEmitter()
    registry = ServiceRegistry(trace)
    svc1 = MockServiceProvider("svc1")
    svc2 = MockServiceProvider("svc2")
    registry.register("svc1", svc1)
    registry.register("svc2", svc2)
    svc1.started = True
    svc2.started = True
    registry.stop_all()
    assert not svc1.started
    assert not svc2.started
