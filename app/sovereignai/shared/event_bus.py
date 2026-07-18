from __future__ import annotations

import asyncio
import contextlib
import inspect
import shutil
import sqlite3
import tempfile
from collections import defaultdict
from collections.abc import Callable
from pathlib import Path
from threading import Lock
from typing import Literal

from sovereignai.shared.event_registry import EventRegistry, HandlerRegistration
from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import Channel, Event, TraceLevel

Subscriber = Callable[[Event], None]


class EventBus:

    def __init__(
        self,
        trace: TraceEmitter,
        registry: EventRegistry,
        overflow_dir: Path | None = None,
    ) -> None:
        self._trace = trace
        self._registry = registry
        self._state: Literal["INIT", "RUNNING", "STOPPING", "STOPPED"] = "INIT"
        self._subscribers: dict[Channel, list[Subscriber]] = defaultdict(list)
        self._lock = Lock()
        self._loop: asyncio.AbstractEventLoop | None = None
        self._loop_thread: any | None = None
        self._overflow_dir: Path
        self._owns_overflow_dir: bool

        if overflow_dir is None:
            self._overflow_dir = Path(tempfile.mkdtemp(prefix="eventbus_"))
            self._owns_overflow_dir = True
        else:
            self._overflow_dir = overflow_dir
            self._owns_overflow_dir = False

        self._instance_id = id(self)
        self._critical_overflow_db = (
            self._overflow_dir / f"critical_overflow_{self._instance_id}.sqlite"
        )

        self._pre_start_buffer: list[Event] = []
        self._pre_start_critical_buffer: list[Event] = []

        self._drain_tasks: dict[str, asyncio.Task] = {}
        self._queues: dict[str, asyncio.Queue] = {}
        self._error_counters: dict[str, int] = defaultdict(int)
        self._drop_counters: dict[str, int] = defaultdict(int)
        self._error_timestamps: dict[str, list[float]] = defaultdict(list)
        self._last_dropped_emission: dict[str, float] = defaultdict(float)

    @property
    def is_started(self) -> bool:
        return self._state == "RUNNING"

    def subscribe(self, channel: Channel, subscriber: Subscriber) -> None:
        with self._lock:
            self._subscribers[channel].append(subscriber)
        self._trace.emit(
            component="EventBus",
            level=TraceLevel.DEBUG,
            message=f"Subscriber registered for channel {channel}",
        )

    def publish(self, event: Event) -> None:
        if self._state == "INIT":
            is_critical = (
                event.trace_level == TraceLevel.ERROR
                or event.event_type.endswith((".error", ".completed"))
            )
            if is_critical:
                self._pre_start_critical_buffer.append(event)
            else:
                self._pre_start_buffer.append(event)
            return

        if self._state in ("STOPPING", "STOPPED"):
            raise RuntimeError(f"Cannot publish when EventBus is {self._state}")

        with self._lock:
            subscribers = list(self._subscribers.get(event.channel, []))
        for subscriber in subscribers:
            try:
                subscriber(event)
            except Exception as exc:
                self._trace.emit(
                    component="EventBus",
                    level=TraceLevel.ERROR,
                    message=(
                        f"Subscriber {subscriber!r} raised {type(exc).__name__} "
                        f"on channel {event.channel}: {exc}"
                    ),
                )

    async def publish_async(self, event: Event) -> None:
        if self._state == "INIT":
            is_critical = (
                event.trace_level == TraceLevel.ERROR
                or event.event_type.endswith((".error", ".completed"))
            )
            if is_critical:
                self._pre_start_critical_buffer.append(event)
            else:
                self._pre_start_buffer.append(event)
            return

        if self._state in ("STOPPING", "STOPPED"):
            raise RuntimeError(f"Cannot publish when EventBus is {self._state}")

        if self._loop is None or not self._loop.is_running():
            raise RuntimeError("Event loop not available")

        handlers = self._registry.handlers_for(event.event_type)
        for registration in handlers:
            queue_key = f"{registration.event_type}_{id(registration.handler)}"
            if queue_key not in self._queues:
                queue_maxsize = registration.queue_maxsize
                is_critical = (
                    event.trace_level == TraceLevel.ERROR
                    or event.event_type.endswith((".error", ".completed"))
                )
                if is_critical:
                    queue_maxsize = min(queue_maxsize, 100)
                self._queues[queue_key] = asyncio.Queue(maxsize=queue_maxsize)

            try:
                self._queues[queue_key].put_nowait(event)
            except asyncio.QueueFull:
                self._drop_counters[queue_key] += 1
                now = asyncio.get_event_loop().time()
                if now - self._last_dropped_emission[queue_key] > 1.0:
                    self._last_dropped_emission[queue_key] = now
                    await self._emit_queue_dropped(event, registration)

                if event.trace_level == TraceLevel.ERROR or event.event_type.endswith(
                    (".error", ".completed")
                ):
                    await self._write_critical_overflow(event)

    async def _emit_queue_dropped(self, event: Event, registration: HandlerRegistration) -> None:
        try:
            from sovereignai.shared.types import new_correlation_id

            trace_event = Event(
                channel=Channel("queue.dropped"),
                correlation_id=new_correlation_id(),
                timestamp=self._now_utc(),
                version=1,
                trace_level=TraceLevel.INFO,
            )
            await self._safe_publish_internal(trace_event)
        except Exception:
            pass

    async def _write_critical_overflow(self, event: Event) -> None:
        def write_to_sqlite():
            try:
                conn = sqlite3.connect(str(self._critical_overflow_db))
                cursor = conn.cursor()
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS critical_events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        channel TEXT,
                        correlation_id TEXT,
                        timestamp TEXT,
                        version INTEGER,
                        trace_level TEXT,
                        event_data TEXT
                    )
                """
                )
                import json

                cursor.execute(
                    """
                    INSERT INTO critical_events
                    (channel, correlation_id, timestamp, version, trace_level, event_data)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        event.channel,
                        str(event.correlation_id),
                        event.timestamp.isoformat(),
                        event.version,
                        event.trace_level,
                        json.dumps({}),
                    ),
                )
                conn.commit()
                conn.close()
            except Exception:
                pass

        with contextlib.suppress(Exception):
            await asyncio.to_thread(write_to_sqlite, timeout=5.0)

        with contextlib.suppress(Exception):
            if self._loop and self._loop.is_running():
                with contextlib.suppress(RuntimeError):
                    self._loop.call_soon_threadsafe(
                        self._safe_publish_internal, event
                    )

    def _now_utc(self):
        from datetime import UTC, datetime

        return datetime.now(UTC)

    async def _safe_publish_internal(self, event: Event) -> None:
        if self._state in ("STOPPING", "STOPPED"):
            return

        try:
            current_loop = asyncio.get_running_loop()
            if current_loop is not self._loop or self._state != "RUNNING":
                return
        except RuntimeError:
            return

        with contextlib.suppress(Exception):
            await self.publish_async(event)

    def start(self) -> None:
        if self._state != "INIT":
            raise RuntimeError(f"EventBus already {self._state}")

        self._state = "RUNNING"
        self._loop = asyncio.new_event_loop()
        self._loop_thread = asyncio.Thread(target=self._run_loop, daemon=True)
        self._loop_thread.start()

        self._registry.mark_started()

        async def drain_buffers():
            for event in self._pre_start_buffer:
                await self.publish_async(event)
            self._pre_start_buffer.clear()
            for event in self._pre_start_critical_buffer:
                await self.publish_async(event)
            self._pre_start_critical_buffer.clear()

        def schedule_drain():
            asyncio.run_coroutine_threadsafe(drain_buffers(), self._loop)

        schedule_drain()

        async def start_drain_tasks():
            handlers = self._registry.handlers_for("*")
            for registration in handlers:
                queue_key = f"{registration.event_type}_{id(registration.handler)}"
                self._drain_tasks[queue_key] = asyncio.create_task(
                    self._drain_task(registration)
                )

        def schedule_start():
            asyncio.run_coroutine_threadsafe(start_drain_tasks(), self._loop)

        schedule_start()

    def _run_loop(self) -> None:
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    async def _drain_task(self, registration: HandlerRegistration) -> None:
        queue_key = f"{registration.event_type}_{id(registration.handler)}"
        queue_maxsize = registration.queue_maxsize

        self._queues[queue_key] = asyncio.Queue(maxsize=queue_maxsize)
        queue = self._queues[queue_key]

        while self._state == "RUNNING":
            try:
                event = await asyncio.wait_for(queue.get(), timeout=1.0)
            except TimeoutError:
                continue

            try:
                if inspect.iscoroutinefunction(registration.handler):
                    await registration.handler(event)
                else:
                    await asyncio.to_thread(registration.handler, event)
            except Exception:
                self._error_counters[queue_key] += 1
                now = asyncio.get_event_loop().time()
                self._error_timestamps[queue_key].append(now)

                self._error_timestamps[queue_key] = [
                    ts for ts in self._error_timestamps[queue_key] if now - ts < 10.0
                ]

                if len(self._error_timestamps[queue_key]) > 50:
                    self._trace.emit(
                        component="EventBus",
                        level=TraceLevel.ERROR,
                        message=f"Circuit breaker tripped for handler {registration.handler}",
                    )
                    break

                try:
                    from sovereignai.shared.types import new_correlation_id

                    crash_event = Event(
                        channel=Channel("handler.crash"),
                        correlation_id=new_correlation_id(),
                        timestamp=self._now_utc(),
                        version=1,
                        trace_level=TraceLevel.ERROR,
                    )
                    await self._safe_publish_internal(crash_event)
                except Exception:
                    pass
            finally:
                queue.task_done()

    def stop(self) -> None:
        if self._state == "INIT":
            self._state = "STOPPED"
            if self._owns_overflow_dir:
                shutil.rmtree(self._overflow_dir, ignore_errors=True)
            return

        if self._state in ("STOPPING", "STOPPED"):
            return

        self._state = "STOPPING"

        async def cancel_tasks():
            for task in self._drain_tasks.values():
                task.cancel()
            _ = await asyncio.gather(*self._drain_tasks.values(), return_exceptions=True)
            self._drain_tasks.clear()

        asyncio.run_coroutine_threadsafe(cancel_tasks(), self._loop).result()

        self._loop.call_soon_threadsafe(self._loop.stop)
        self._loop_thread.join(timeout=5.0)

        self._state = "STOPPED"

        if self._owns_overflow_dir:
            shutil.rmtree(self._overflow_dir, ignore_errors=True)
