from __future__ import annotations

import time
from typing import TYPE_CHECKING

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
        self._health_check_cache: dict[str, tuple[bool, float]] = {}
        self._health_check_ttl = 30.0
        self._trace.emit(
            component="RoutingEngine",
            level=TraceLevel.DEBUG,
            message="RoutingEngine initialized with health_check caching (TTL=30s)",
        )

    def route(self, capability: str, method_name: str, *args: object) -> object:
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
                healthy = self._get_cached_health(metadata.component_id, instance)
                if not healthy:
                    self._trace.emit(
                        component="RoutingEngine",
                        level=TraceLevel.WARN,
                        message=f"adapter {metadata.component_id} unhealthy — skipping",
                    )
                    continue

            try:
                method = getattr(instance, method_name)
                return method(*args)
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

    def _get_cached_health(self, component_id: str, instance: object) -> bool:
        current_time = time.time()
        if component_id in self._health_check_cache:
            healthy, timestamp = self._health_check_cache[component_id]
            if current_time - timestamp < self._health_check_ttl:
                return healthy

        health = instance.health_check()
        self._health_check_cache[component_id] = (health.healthy, current_time)
        return health.healthy

    def invalidate_health_cache(self, component_id: str) -> None:
        if component_id in self._health_check_cache:
            del self._health_check_cache[component_id]
