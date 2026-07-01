from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sovereignai.shared.capability_graph import ICapabilityIndex
from sovereignai.shared.trace_emitter import TraceEmitter, TraceLevel
from sovereignai.shared.types import (
    AdapterUnavailableError,
    NoHealthyAdapterError,
)

if TYPE_CHECKING:
    from sovereignai.shared.lifecycle_manager import LifecycleManager


class RoutingEngine:

    def __init__(
        self,
        capability_index: ICapabilityIndex,
        lifecycle_manager: LifecycleManager,
        trace: TraceEmitter,
    ) -> None:
        self._index = capability_index
        self._lifecycle = lifecycle_manager
        self._trace = trace

    def route(self, capability: str, method_name: str, *args: Any, **kwargs: Any) -> Any:
        adapters = self._index.adapters_by_capability(capability)

        for metadata in adapters:
            instance = self._index.get_adapter(metadata.component_id)
            if instance is None:
                self._trace.emit(
                    component="RoutingEngine",
                    level=TraceLevel.WARN,
                    message=(
                        f"component {metadata.component_id} registered but "
                        f"instance missing — skipping"
                    ),
                )
                continue

            if hasattr(instance, "health_check"):
                health = instance.health_check()
                if not health.healthy:
                    self._trace.emit(
                        component="RoutingEngine",
                        level=TraceLevel.WARN,
                        message=f"adapter {metadata.component_id} unhealthy — skipping",
                    )
                    continue

            try:
                method = getattr(instance, method_name)
                return method(*args, **kwargs)
            except AdapterUnavailableError:
                self._trace.emit(
                    component="RoutingEngine",
                    level=TraceLevel.WARN,
                    message=f"adapter {metadata.component_id} failed, trying next",
                )
                continue

        raise NoHealthyAdapterError(
            f"No healthy adapter for {capability}/{method_name} "
            f"(checked {len(adapters)} registered adapters)"
        )
