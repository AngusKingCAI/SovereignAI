from __future__ import annotations

import asyncio
import logging
import sys
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING

from sovereignai.lifecycle.types import LifecycleError

if TYPE_CHECKING:
    from sovereignai.shared.event_bus import EventBus
    from sovereignai.shared.trace_emitter import TraceEmitter


class HookPhase(Enum):
    REGISTRATION_OPEN = "REGISTRATION_OPEN"
    REGISTRATION_CLOSED = "REGISTRATION_CLOSED"
    STARTUP_RUNNING = "STARTUP_RUNNING"
    STARTUP_DONE = "STARTUP_DONE"
    SHUTDOWN_RUNNING = "SHUTDOWN_RUNNING"
    SHUTDOWN_DONE = "SHUTDOWN_DONE"


@dataclass
class HookRegistration:
    name: str
    hook: Callable[[], None]
    critical: bool
    phase: str


class LifecycleHookRegistry:
    MAX_STARTUP_HOOKS = 5
    MAX_SHUTDOWN_HOOKS = 5
    HOOK_TIMEOUT_SECONDS = 15

    def __init__(
        self,
        event_bus: EventBus,
        trace: TraceEmitter,
    ) -> None:
        self._event_bus = event_bus
        self._trace = trace
        self._phase = HookPhase.REGISTRATION_OPEN
        self._startup_hooks: list[HookRegistration] = []
        self._shutdown_hooks: list[HookRegistration] = []
        self._lock = asyncio.Lock()
        self._trace.emit(
            component="LifecycleHookRegistry",
            level=logging.INFO,
            message="LifecycleHookRegistry initialized",
        )

    def register_startup_hook(
        self, name: str, hook: Callable[[], None], critical: bool = False
    ) -> None:
        if self._phase != HookPhase.REGISTRATION_OPEN:
            raise LifecycleError(f"Cannot register startup hook in phase {self._phase}")

        if len(self._startup_hooks) >= self.MAX_STARTUP_HOOKS:
            raise LifecycleError(f"Maximum startup hooks ({self.MAX_STARTUP_HOOKS}) exceeded")

        self._startup_hooks.append(HookRegistration(name, hook, critical, "startup"))
        self._trace.emit(
            component="LifecycleHookRegistry",
            level=logging.INFO,
            message=f"Registered startup hook: {name} (critical={critical})",
        )

    def register_shutdown_hook(
        self, name: str, hook: Callable[[], None], critical: bool = False
    ) -> None:
        if self._phase != HookPhase.REGISTRATION_OPEN:
            raise LifecycleError(f"Cannot register shutdown hook in phase {self._phase}")

        if len(self._shutdown_hooks) >= self.MAX_SHUTDOWN_HOOKS:
            raise LifecycleError(f"Maximum shutdown hooks ({self.MAX_SHUTDOWN_HOOKS}) exceeded")

        self._shutdown_hooks.append(HookRegistration(name, hook, critical, "shutdown"))
        self._trace.emit(
            component="LifecycleHookRegistry",
            level=logging.INFO,
            message=f"Registered shutdown hook: {name} (critical={critical})",
        )

    async def close_registration(self) -> None:
        async with self._lock:
            if self._phase != HookPhase.REGISTRATION_OPEN:
                raise LifecycleError(f"Cannot close registration in phase {self._phase}")

            self._phase = HookPhase.REGISTRATION_CLOSED
            self._trace.emit(
                component="LifecycleHookRegistry",
                level=logging.INFO,
                message="Hook registration closed",
            )

    async def run_startup_hooks(self) -> None:
        async with self._lock:
            if self._phase != HookPhase.REGISTRATION_CLOSED:
                raise LifecycleError(f"Cannot run startup hooks in phase {self._phase}")

            self._phase = HookPhase.STARTUP_RUNNING

        critical_failed = False

        for hook_reg in self._startup_hooks:
            try:
                self._trace.emit(
                    component="LifecycleHookRegistry",
                    level=logging.INFO,
                    message=f"Running startup hook: {hook_reg.name}",
                )

                await asyncio.wait_for(
                    self._run_hook(hook_reg),
                    timeout=self.HOOK_TIMEOUT_SECONDS,
                )
            except TimeoutError:
                error_msg = (
                    f"Startup hook {hook_reg.name} timeout after "
                    f"{self.HOOK_TIMEOUT_SECONDS}s"
                )
                self._handle_hook_failure(hook_reg, error_msg)
                if hook_reg.critical:
                    critical_failed = True
            except Exception as e:
                error_msg = f"Startup hook {hook_reg.name} failed: {e}"
                self._handle_hook_failure(hook_reg, error_msg)
                if hook_reg.critical:
                    critical_failed = True

        async with self._lock:
            self._phase = HookPhase.STARTUP_DONE

        if critical_failed:
            raise LifecycleError("Critical startup hook failed")

    async def run_shutdown_hooks(self) -> None:
        async with self._lock:
            if self._phase != HookPhase.STARTUP_DONE:
                raise LifecycleError(f"Cannot run shutdown hooks in phase {self._phase}")

            self._phase = HookPhase.SHUTDOWN_RUNNING

        critical_hooks = [h for h in self._shutdown_hooks if h.critical]
        non_critical_hooks = [h for h in self._shutdown_hooks if not h.critical]

        for hook_reg in non_critical_hooks:
            try:
                self._trace.emit(
                    component="LifecycleHookRegistry",
                    level=logging.INFO,
                    message=f"Running non-critical shutdown hook: {hook_reg.name}",
                )

                await asyncio.wait_for(
                    self._run_hook(hook_reg),
                    timeout=self.HOOK_TIMEOUT_SECONDS,
                )
            except TimeoutError:
                error_msg = (
                    f"Non-critical shutdown hook {hook_reg.name} timeout after "
                    f"{self.HOOK_TIMEOUT_SECONDS}s"
                )
                self._handle_hook_failure(hook_reg, error_msg)
            except Exception as e:
                error_msg = f"Non-critical shutdown hook {hook_reg.name} failed: {e}"
                self._handle_hook_failure(hook_reg, error_msg)

        for hook_reg in critical_hooks:
            try:
                self._trace.emit(
                    component="LifecycleHookRegistry",
                    level=logging.INFO,
                    message=f"Running critical shutdown hook: {hook_reg.name}",
                )

                await asyncio.wait_for(
                    self._run_hook(hook_reg),
                    timeout=self.HOOK_TIMEOUT_SECONDS,
                )
            except TimeoutError:
                error_msg = (
                    f"Critical shutdown hook {hook_reg.name} timeout after "
                    f"{self.HOOK_TIMEOUT_SECONDS}s"
                )
                self._handle_hook_failure(hook_reg, error_msg)
            except Exception as e:
                error_msg = f"Critical shutdown hook {hook_reg.name} failed: {e}"
                self._handle_hook_failure(hook_reg, error_msg)

        async with self._lock:
            self._phase = HookPhase.SHUTDOWN_DONE

    async def _run_hook(self, hook_reg: HookRegistration) -> None:
        if asyncio.iscoroutinefunction(hook_reg.hook):
            await hook_reg.hook()
        else:
            hook_reg.hook()

    def _handle_hook_failure(self, hook_reg: HookRegistration, error_msg: str) -> None:
        self._trace.emit(
            component="LifecycleHookRegistry",
            level=logging.ERROR,
            message=error_msg,
        )

        print(f"Hook failure: {error_msg}", file=sys.stderr)

        try:
            from sovereignai.shared.types import Channel, Event, TraceLevel, new_correlation_id

            event = Event(
                channel=Channel("lifecycle.hook.failed"),
                correlation_id=new_correlation_id(),
                timestamp=self._now_utc(),
                version=1,
                trace_level=TraceLevel.ERROR,
            )
            asyncio.create_task(self._event_bus.publish_async(event))
        except Exception:
            pass

    def _now_utc(self) -> datetime:
        from datetime import datetime
        return datetime.now(UTC)

    @property
    def phase(self) -> HookPhase:
        return self._phase
