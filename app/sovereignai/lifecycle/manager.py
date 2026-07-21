from __future__ import annotations

import asyncio
import logging
import os
import sys
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

import platformdirs

from sovereignai.lifecycle.types import LifecycleError, LifecycleState
from sovereignai.shared.types import Channel, Event, TraceLevel

if TYPE_CHECKING:
    from sovereignai.shared.event_bus import EventBus
    from sovereignai.shared.trace_emitter import TraceEmitter


class AgentLifecycleManager:
    def __init__(
        self,
        event_bus: EventBus,
        trace: TraceEmitter,
        orchestrator_factory: Callable[[], object] | None = None,
        web_url: str | None = None,
    ) -> None:
        self._event_bus = event_bus
        self._trace = trace
        self._orchestrator_factory = orchestrator_factory
        self._web_url = web_url or os.getenv("SOVEREIGNAI_WEB_URL", "http://localhost:8000")

        self._state = LifecycleState.INITIALIZING
        self._health_check_count = 0
        self._consecutive_healthy = 0
        self._lock = asyncio.Lock()

        self._fallback_log_path = (
            Path(platformdirs.user_data_dir("sovereignai")) / "logs" / "lifecycle_fallback.log"
        )
        self._fallback_log_available = self._ensure_fallback_log_dir()

        self._trace.emit(
            component="AgentLifecycleManager",
            level=TraceLevel.INFO,
            message=f"AgentLifecycleManager initialized with web_url={self._web_url}",
        )

    def _ensure_fallback_log_dir(self) -> bool:
        try:
            log_dir = self._fallback_log_path.parent
            log_dir.mkdir(parents=True, exist_ok=True)
            return True
        except (OSError, PermissionError) as e:
            self._trace.emit(
                component="AgentLifecycleManager",
                level=TraceLevel.ERROR,
                message=(
                    f"Cannot create fallback log directory "
                    f"{self._fallback_log_path.parent}: {e}"
                ),
            )
            return False

    def _write_fallback_log(self, message: str) -> None:
        if not self._fallback_log_available:
            return

        try:
            from logging.handlers import RotatingFileHandler

            handler = RotatingFileHandler(
                self._fallback_log_path,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5,
            )
            handler.emit(logging.LogRecord(
                name="lifecycle_fallback",
                level=logging.ERROR,
                pathname="",
                lineno=0,
                msg=message,
                args=(),
                exc_info=None,
            ))
        except Exception as e:
            print(f"Fallback log write failed: {e}", file=sys.stderr)

    async def _emit_lifecycle_event(self, event_type: str, **kwargs: object) -> None:
        from sovereignai.shared.types import new_correlation_id

        event = Event(
            channel=Channel(f"lifecycle.{event_type}"),
            correlation_id=new_correlation_id(),
            timestamp=self._now_utc(),
            version=1,
            trace_level=TraceLevel.INFO,
        )

        try:
            await self._event_bus.publish_async(event)
        except Exception as e:
            self._trace.emit(
                component="AgentLifecycleManager",
                level=TraceLevel.ERROR,
                message=f"Failed to publish lifecycle event {event_type}: {e}",
            )
            self._write_fallback_log(f"lifecycle.{event_type}: {kwargs}")

    def _now_utc(self) -> datetime:
        from datetime import datetime
        return datetime.now(UTC)

    async def start(self) -> None:
        async with self._lock:
            if self._state != LifecycleState.INITIALIZING:
                raise LifecycleError(f"Cannot start from state {self._state}")

            await self._emit_lifecycle_event("startup.started")

            try:
                await self._run_startup_sequence()
                if self._state != LifecycleState.DEGRADED:
                    self._state = LifecycleState.READY
                await self._emit_lifecycle_event("startup.completed")
            except LifecycleError as e:
                self._state = LifecycleState.STOPPED
                await self._emit_lifecycle_event("startup.failed", error=str(e))
                raise

    async def _run_startup_sequence(self) -> None:
        from dataclasses import dataclass

        @dataclass
        class Stage:
            name: str
            func: Callable[[], Awaitable[None] | None]
            critical: bool

        stages = [
            Stage("EventBus", self._check_eventbus, True),
            Stage("OptionsBackend", self._check_options_backend, False),
            Stage("Orchestrator", self._check_orchestrator, False),
            Stage("ModelRegistry", self._check_model_registry, False),
            Stage("RouteReadinessCheck", self._check_route_readiness, False),
        ]

        for stage in stages:
            stage_name = stage.name
            stage_func = stage.func
            is_critical = stage.critical  # noqa: F841
            self._trace.emit(
                component="AgentLifecycleManager",
                level=TraceLevel.INFO,
                message=f"Starting stage: {stage_name}",
            )

            try:
                if asyncio.iscoroutinefunction(stage_func):
                    await asyncio.wait_for(stage_func(), timeout=30.0)
                else:
                    stage_func()  # Call synchronous function
                    await asyncio.sleep(0)  # Make it awaitable
                self._trace.emit(
                    component="AgentLifecycleManager",
                    level=TraceLevel.INFO,
                    message=f"Stage completed: {stage_name}",
                )
            except TimeoutError:
                error_msg = f"Stage timeout: {stage_name}"
                if stage.critical:
                    self._trace.emit(
                        component="AgentLifecycleManager",
                        level=TraceLevel.ERROR,
                        message=error_msg,
                    )
                    await self._emit_lifecycle_event(
                        "stage.failed", stage=stage_name, error="timeout"
                    )
                    raise LifecycleError(error_msg) from None
                else:
                    self._trace.emit(
                        component="AgentLifecycleManager",
                        level=TraceLevel.WARN,
                        message=error_msg + " (continuing with degraded start)",
                    )
                    await self._emit_lifecycle_event(
                        "stage.failed", stage=stage_name, error="timeout"
                    )
                    self._state = LifecycleState.DEGRADED
            except Exception as e:
                error_msg = f"Stage failed: {stage_name} - {e}"
                if stage.critical:
                    self._trace.emit(
                        component="AgentLifecycleManager",
                        level=TraceLevel.ERROR,
                        message=error_msg,
                    )
                    await self._emit_lifecycle_event(
                        "stage.failed", stage=stage_name, error=str(e)
                    )
                    raise LifecycleError(error_msg) from None
                else:
                    self._trace.emit(
                        component="AgentLifecycleManager",
                        level=TraceLevel.WARN,
                        message=error_msg + " (continuing with degraded start)",
                    )
                    await self._emit_lifecycle_event(
                        "stage.failed", stage=stage_name, error=str(e)
                    )
                    self._state = LifecycleState.DEGRADED

    async def _check_eventbus(self) -> None:
        if not self._event_bus.is_started:
            raise LifecycleError("EventBus is not started")

        self._trace.emit(
            component="AgentLifecycleManager",
            level=TraceLevel.INFO,
            message="EventBus health check passed",
        )

    async def _check_options_backend(self) -> None:
        from sovereignai.options.backend import SQLiteOptionsBackend

        try:
            backend = SQLiteOptionsBackend()
            await backend.initialize()
            self._trace.emit(
                component="AgentLifecycleManager",
                level=TraceLevel.INFO,
                message="OptionsBackend health check passed",
            )
        except Exception as e:
            self._trace.emit(
                component="AgentLifecycleManager",
                level=TraceLevel.WARN,
                message=f"OptionsBackend health check failed: {e}",
            )

    async def _check_orchestrator(self) -> None:
        self._trace.emit(
            component="AgentLifecycleManager",
            level=TraceLevel.INFO,
            message="Orchestrator health check passed (placeholder)",
        )

    async def _check_model_registry(self) -> None:
        if self._orchestrator_factory is None:
            self._trace.emit(
                component="AgentLifecycleManager",
                level=TraceLevel.WARN,
                message="ModelRegistry factory not provided, skipping check",
            )
            return

        self._trace.emit(
            component="AgentLifecycleManager",
            level=TraceLevel.INFO,
            message="ModelRegistry factory provided (not called during init per contract)",
        )

    async def _check_route_readiness(self) -> None:
        import aiohttp

        ready_url = f"{self._web_url}/api/lifecycle/ready"
        start_time = asyncio.get_event_loop().time()
        timeout = 30.0
        poll_interval = 2.0
        connection_refused_logged = False

        while True:
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed >= timeout:
                self._trace.emit(
                    component="AgentLifecycleManager",
                    level=TraceLevel.WARN,
                    message=f"Route readiness check timeout after {timeout}s",
                )
                return

            try:
                async with (
                    aiohttp.ClientSession() as session,
                    session.get(ready_url, timeout=aiohttp.ClientTimeout(total=5)) as response,
                ):
                    if response.status == 200:
                        try:
                            data = await response.json()
                            if "ready" in data:
                                self._trace.emit(
                                    component="AgentLifecycleManager",
                                    level=TraceLevel.INFO,
                                    message=f"Route readiness check passed: ready={data['ready']}",
                                )
                                return
                        except Exception:
                            pass

                        self._trace.emit(
                            component="AgentLifecycleManager",
                            level=TraceLevel.WARN,
                            message="Route readiness check returned 200 but invalid DTO",
                        )
                        return
                    else:
                        self._trace.emit(
                            component="AgentLifecycleManager",
                            level=TraceLevel.WARN,
                            message=f"Route readiness check returned status {response.status}",
                        )
                        return
            except (aiohttp.ClientConnectorError, aiohttp.ClientError) as e:
                if "connection refused" in str(e).lower() or "connection error" in str(e).lower():
                    if not connection_refused_logged:
                        self._trace.emit(
                            component="AgentLifecycleManager",
                            level=TraceLevel.INFO,
                            message=f"Web not deployed (connection refused): {ready_url}",
                        )
                        connection_refused_logged = True
                else:
                    self._trace.emit(
                        component="AgentLifecycleManager",
                        level=TraceLevel.WARN,
                        message=f"Route readiness check connection error: {e}",
                    )
            except Exception as e:
                self._trace.emit(
                    component="AgentLifecycleManager",
                    level=TraceLevel.WARN,
                    message=f"Route readiness check error: {e}",
                )

            await asyncio.sleep(poll_interval)

    async def record_health_check(self, healthy: bool) -> None:
        async with self._lock:
            self._health_check_count += 1

            if healthy:
                self._consecutive_healthy += 1
                if self._state == LifecycleState.DEGRADED and self._consecutive_healthy >= 3:
                    self._state = LifecycleState.READY
                    self._consecutive_healthy = 0
                    await self._emit_lifecycle_event("recovered")
                    self._trace.emit(
                        component="AgentLifecycleManager",
                        level=TraceLevel.INFO,
                        message="Recovered to READY after 3 consecutive healthy checks",
                    )
            else:
                self._consecutive_healthy = 0
                if self._state == LifecycleState.READY:
                    self._state = LifecycleState.DEGRADED
                    await self._emit_lifecycle_event("degraded")
                    self._trace.emit(
                        component="AgentLifecycleManager",
                        level=TraceLevel.WARN,
                        message="Transitioned to DEGRADED after unhealthy check",
                    )

    async def shutdown(self) -> None:
        async with self._lock:
            if self._state in (LifecycleState.SHUTTING_DOWN, LifecycleState.STOPPED):
                return

            previous_state = self._state
            self._state = LifecycleState.SHUTTING_DOWN

            await self._emit_lifecycle_event("shutdown.started")

            self._trace.emit(
                component="AgentLifecycleManager",
                level=TraceLevel.INFO,
                message=f"Shutdown initiated from state {previous_state}",
            )

            self._state = LifecycleState.STOPPED
            await self._emit_lifecycle_event("shutdown.completed")

            self._trace.emit(
                component="AgentLifecycleManager",
                level=TraceLevel.INFO,
                message="Shutdown completed",
            )

    @property
    def state(self) -> LifecycleState:
        return self._state
