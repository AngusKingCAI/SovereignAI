from __future__ import annotations

import asyncio
import contextlib
import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sovereignai.shared.trace_emitter import TraceEmitter


@dataclass
class HealthCheckResult:
    healthy: bool
    details: dict
    timestamp: datetime
    error: str | None = None


class HealthAggregator:
    POLL_INTERVAL_SECONDS = 5.0
    CACHE_TTL_SECONDS = 5.0
    POLLING_ERROR_DELAY_SECONDS = 10.0

    def __init__(self, trace: TraceEmitter) -> None:
        self._trace = trace
        self._health_checks: dict[str, Callable[[], dict]] = {}
        self._cache: dict[str, HealthCheckResult] = {}
        self._cache_timestamp: datetime | None = None
        self._polling_task: asyncio.Task | None = None
        self._lock = asyncio.Lock()
        self._trace.emit(
            component="HealthAggregator",
            level=logging.INFO,
            message="HealthAggregator initialized",
        )
        self._running = False

    def register(self, component_id: str, health_check_func: Callable[[], dict]) -> None:
        self._health_checks[component_id] = health_check_func
        self._trace.emit(
            component="HealthAggregator",
            level=logging.INFO,
            message=f"Registered health check for component: {component_id}",
        )

    def deregister(self, component_id: str) -> None:
        if component_id in self._health_checks:
            del self._health_checks[component_id]
            if component_id in self._cache:
                del self._cache[component_id]
            self._trace.emit(
                component="HealthAggregator",
                level=logging.INFO,
                message=f"Deregistered health check for component: {component_id}",
            )

    async def start(self) -> None:
        async with self._lock:
            if self._running:
                return

            self._running = True
            self._polling_task = asyncio.create_task(self._polling_loop())
            self._trace.emit(
                component="HealthAggregator",
                level=logging.INFO,
                message="Health aggregator polling started",
            )

    async def stop(self) -> None:
        async with self._lock:
            if not self._running:
                return

            self._running = False
            if self._polling_task:
                self._polling_task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await self._polling_task
                self._polling_task = None

            self._trace.emit(
                component="HealthAggregator",
                level=logging.INFO,
                message="Health aggregator polling stopped",
            )

    async def _polling_loop(self) -> None:
        while self._running:
            try:
                await self._poll_all_components()
                await asyncio.sleep(self.POLL_INTERVAL_SECONDS)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self._trace.emit(
                    component="HealthAggregator",
                    level=logging.ERROR,
                    message=(
                        f"Polling loop error: {e}. "
                        f"Retrying in {self.POLLING_ERROR_DELAY_SECONDS}s"
                    ),
                )
                await asyncio.sleep(self.POLLING_ERROR_DELAY_SECONDS)

    async def _poll_all_components(self) -> None:
        async with self._lock:
            for component_id, health_check_func in self._health_checks.items():
                try:
                    result = await self._run_health_check(component_id, health_check_func)
                    self._cache[component_id] = result
                except Exception as e:
                    self._trace.emit(
                        component="HealthAggregator",
                        level=logging.ERROR,
                        message=f"Health check failed for {component_id}: {e}",
                    )
                    self._cache[component_id] = HealthCheckResult(
                        healthy=False,
                        details={},
                        timestamp=datetime.now(UTC),
                        error=str(e),
                    )

            self._cache_timestamp = datetime.now(UTC)

    async def _run_health_check(
        self, component_id: str, health_check_func: Callable[[], dict]
    ) -> HealthCheckResult:
        if asyncio.iscoroutinefunction(health_check_func):
            result = await health_check_func()
        else:
            result = health_check_func()

        if not isinstance(result, dict):
            raise ValueError(f"Health check for {component_id} must return dict")

        healthy = result.get("healthy", True)
        details = result.get("details", {})

        return HealthCheckResult(
            healthy=healthy,
            details=details,
            timestamp=datetime.now(UTC),
        )

    def get_health_status(self) -> dict:
        cache_age_ms = 0
        if self._cache_timestamp:
            cache_age = datetime.now(UTC) - self._cache_timestamp
            cache_age_ms = int(cache_age.total_seconds() * 1000)

        components_health = {}
        for component_id, result in self._cache.items():
            components_health[component_id] = {
                "healthy": result.healthy,
                "details": result.details,
                "timestamp": result.timestamp.isoformat(),
                "error": result.error,
            }

        overall_status = "healthy"
        if components_health:
            unhealthy_count = sum(1 for h in components_health.values() if not h["healthy"])
            if unhealthy_count == len(components_health):
                overall_status = "unhealthy"
            elif unhealthy_count > 0:
                overall_status = "degraded"

        return {
            "status": overall_status,
            "components": components_health,
            "cache_age_ms": cache_age_ms,
        }
