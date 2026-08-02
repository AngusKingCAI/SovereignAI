from __future__ import annotations

import asyncio
import contextlib
import logging
import signal
import sys
from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sovereignai.lifecycle.manager import AgentLifecycleManager
    from sovereignai.shared.types import TraceEmitter


class GracefulShutdown:
    def __init__(
        self,
        lifecycle_manager: AgentLifecycleManager,
        trace: TraceEmitter,
        sentinel_path: Path | None = None,
    ) -> None:
        self._lifecycle_manager = lifecycle_manager
        self._trace = trace
        self._sentinel_path = sentinel_path or Path(".shutdown_sentinel")
        self._shutdown_requested = False
        self._shutdown_task: asyncio.Task | None = None
        self._sentinel_task: asyncio.Task | None = None
        self._trace.emit(
            component="GracefulShutdown",
            level=logging.INFO,
            message="GracefulShutdown initialized",
        )

    async def start(self) -> None:
        """Start graceful shutdown monitoring."""
        self._setup_signal_handlers()
        self._sentinel_task = asyncio.create_task(self._monitor_sentinel())

    def _setup_signal_handlers(self) -> None:
        """Setup signal handlers for SIGTERM and SIGINT."""
        try:
            loop = asyncio.get_running_loop()

            for sig in (signal.SIGTERM, signal.SIGINT):
                def make_handler(s: signal.Signals) -> Callable[[], None]:
                    def handler() -> None:
                        asyncio.create_task(self._handle_signal(s))
                    return handler
                loop.add_signal_handler(sig, make_handler(sig))
        except NotImplementedError:
            # Signal handlers not supported on this platform
            pass

    async def _handle_signal(self, sig: signal.Signals) -> None:
        """Handle shutdown signal."""
        if self._shutdown_requested:
            return

        self._shutdown_requested = True
        print(f"\nReceived signal {sig.name}, initiating graceful shutdown...")

        if self._shutdown_task is None or self._shutdown_task.done():
            self._shutdown_task = asyncio.create_task(self._perform_shutdown())

    async def _monitor_sentinel(self) -> None:
        """Monitor sentinel file for shutdown request."""
        while not self._shutdown_requested:
            try:
                if self._sentinel_path.exists():
                    print("Sentinel file detected, initiating graceful shutdown...")
                    self._shutdown_requested = True

                    if self._shutdown_task is None or self._shutdown_task.done():
                        self._shutdown_task = asyncio.create_task(self._perform_shutdown())
                    break
            except Exception:
                pass

            await asyncio.sleep(1.0)

    async def _perform_shutdown(self) -> None:
        """Perform graceful shutdown."""
        try:
            await self._lifecycle_manager.shutdown()
            print("Graceful shutdown completed")
        except Exception as e:
            print(f"Error during shutdown: {e}", file=sys.stderr)

        # Cancel sentinel monitoring
        if self._sentinel_task and not self._sentinel_task.done():
            self._sentinel_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._sentinel_task

    async def stop(self) -> None:
        """Stop graceful shutdown monitoring."""
        if self._sentinel_task and not self._sentinel_task.done():
            self._sentinel_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._sentinel_task

    def create_sentinel(self) -> None:
        """Create sentinel file to trigger shutdown."""
        try:
            self._sentinel_path.touch()
        except Exception as e:
            print(f"Failed to create sentinel file: {e}", file=sys.stderr)

    def remove_sentinel(self) -> None:
        """Remove sentinel file."""
        try:
            if self._sentinel_path.exists():
                self._sentinel_path.unlink()
        except Exception as e:
            print(f"Failed to remove sentinel file: {e}", file=sys.stderr)
