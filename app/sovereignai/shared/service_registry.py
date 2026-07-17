from __future__ import annotations

from app.services.base import ServiceProvider
from app.sovereignai.shared.trace_emitter import TraceEmitter
from app.sovereignai.shared.types import TraceLevel


class ServiceRegistry:
    def __init__(self, trace: TraceEmitter) -> None:
        self._trace = trace
        self._providers: dict[str, ServiceProvider] = {}
        self._trace.emit(
            component="ServiceRegistry",
            level=TraceLevel.INFO,
            message="ServiceRegistry initialized",
        )

    def register(self, name: str, provider: ServiceProvider) -> None:
        self._providers[name] = provider

    def list_services(self) -> list[str]:
        return list(self._providers.keys())

    def get_service(self, name: str) -> ServiceProvider:
        return self._providers[name]

    def start_all(self) -> None:
        for provider in self._providers.values():
            provider.start()

    def stop_all(self) -> None:
        for provider in self._providers.values():
            provider.stop()
