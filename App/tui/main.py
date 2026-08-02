from __future__ import annotations

import asyncio
from enum import Enum
from pathlib import Path

import platformdirs
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, ContentSwitcher, Footer, Header, Static

from app.tui.client import TUIWebClient
from app.tui.panels.adapters import AdaptersPanel
from app.tui.panels.audit import AuditPanel
from app.tui.panels.hardware import HardwarePanel
from app.tui.panels.logs import LogsPanel
from app.tui.panels.memory import MemoryPanel
from app.tui.panels.models import ModelsPanel
from app.tui.panels.options import OptionsPanel
from app.tui.panels.orchestrator import OrchestratorPanel
from app.tui.panels.tasks import TasksPanel
from app.tui.panels.workers import WorkersPanel

# File sentinel path for shutdown detection
SHUTDOWN_SENTINEL_PATH = Path(platformdirs.user_data_dir("sovereignai")) / ".shutdown_sentinel"


class LifecycleState(Enum):
    """Lifecycle state machine states."""
    LIFECYCLE_INIT = "LIFECYCLE_INIT"
    LIFECYCLE_READY = "LIFECYCLE_READY"
    LIFECYCLE_SHUTDOWN_DETECTED = "LIFECYCLE_SHUTDOWN_DETECTED"


class SovereignTUI(App):
    """SovereignAI TUI with 10-panel sidebar, auto-refresh, and shutdown detection.

    Per P8: UIs are separate processes with 10-section sidebar.
    Uses REST polling fallback (SSE disabled per DEBT-7 spike).
    Implements client-side shutdown detection with state machine.
    """

    CSS_PATH = "sovereign.tcss"

    BINDINGS = [
        ("tab", "cycle_panel", "Cycle"),
        ("q", "quit", "Quit"),
    ]

    # 10 sidebar panels per P8
    PANEL_NAMES = [
        "orchestrator",
        "workers",
        "tasks",
        "memory",
        "models",
        "adapters",
        "hardware",
        "logs",
        "options",
        "audit",
    ]

    def __init__(self) -> None:
        super().__init__()
        self._client = TUIWebClient()
        self._lifecycle_state = LifecycleState.LIFECYCLE_INIT
        self._lifecycle_baseline_pid: int | None = None
        self._lifecycle_baseline_uuid: str | None = None
        self._shutdown_detected = False
        self._refresh_task: asyncio.Task | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            with Vertical(id="sidebar"):
                yield Static("SovereignAI TUI", id="location-bar")
                for name in self.PANEL_NAMES:
                    yield Button(name.title(), id=f"btn-{name}")
            with ContentSwitcher(id="main-content"):
                for name in self.PANEL_NAMES:
                    yield Static(f"Loading {name.title()}...", id=f"placeholder-{name}")
        yield Footer()

    def on_mount(self) -> None:
        self.call_after_refresh(self._initialize_panels)
        self.call_after_refresh(self._start_lifecycle_monitoring)

    def _initialize_panels(self) -> None:
        """Initialize all 10 panels with TUIWebClient."""
        panel_classes = {
            "orchestrator": OrchestratorPanel,
            "workers": WorkersPanel,
            "tasks": TasksPanel,
            "memory": MemoryPanel,
            "models": ModelsPanel,
            "adapters": AdaptersPanel,
            "hardware": HardwarePanel,
            "logs": LogsPanel,
            "options": OptionsPanel,
            "audit": AuditPanel,
        }

        for panel_name, panel_class in panel_classes.items():
            panel_id = f"panel-{panel_name}"
            placeholder_id = f"placeholder-{panel_name}"

            panel = panel_class(client=self._client, id=panel_id)
            placeholder = self.query_one(f"#{placeholder_id}", Static)

            if isinstance(placeholder, Static):
                placeholder.remove()
                self.query_one("#main-content", ContentSwitcher).mount(panel)

    def _start_lifecycle_monitoring(self) -> None:
        """Start lifecycle monitoring with polling and shutdown detection."""
        async def monitor_lifecycle():
            while not self._shutdown_detected:
                try:
                    await self._check_lifecycle_status()
                except Exception:
                    pass  # Continue monitoring on errors

                # Check file sentinel as fallback
                if self._check_shutdown_sentinel():
                    self._trigger_shutdown("file sentinel detected")

                await asyncio.sleep(2)  # 2s polling interval per plan

        self._refresh_task = asyncio.create_task(monitor_lifecycle())

    def _check_shutdown_sentinel(self) -> bool:
        """Check if shutdown sentinel file exists (fallback mechanism)."""
        try:
            return SHUTDOWN_SENTINEL_PATH.exists()
        except Exception:
            return False

    async def _check_lifecycle_status(self) -> None:
        """Check lifecycle status and detect shutdown conditions."""
        try:
            async with self._client as client:
                response = await client.get("/api/lifecycle/ready")

                if response.status_code == 200:
                    data = response.json()
                    ready = data.get("ready", False)
                    pid = data.get("pid")
                    uuid = data.get("instance_uuid")

                    if self._lifecycle_state == LifecycleState.LIFECYCLE_INIT:
                        if ready:
                            # Establish baseline on first ready:true
                            self._lifecycle_baseline_pid = pid
                            self._lifecycle_baseline_uuid = uuid
                            self._lifecycle_state = LifecycleState.LIFECYCLE_READY
                        else:
                            # Update baseline even when ready:false
                            self._lifecycle_baseline_pid = pid
                            self._lifecycle_baseline_uuid = uuid
                    elif self._lifecycle_state == LifecycleState.LIFECYCLE_READY:
                        # Check for shutdown triggers
                        if not ready:
                            self._trigger_shutdown("ready: false transition")
                        elif pid != self._lifecycle_baseline_pid:
                            self._trigger_shutdown("PID change")
                        elif uuid != self._lifecycle_baseline_uuid:
                            self._trigger_shutdown("UUID change")
                elif response.status_code == 404:
                    if self._lifecycle_state == LifecycleState.LIFECYCLE_READY:
                        self._trigger_shutdown("HTTP 404")
                else:
                    # Connection failure during READY state
                    if self._lifecycle_state == LifecycleState.LIFECYCLE_READY:
                        self._trigger_shutdown("connection failure")
        except Exception:
            # Connection error during READY state
            if self._lifecycle_state == LifecycleState.LIFECYCLE_READY:
                self._trigger_shutdown("connection error")

    def _trigger_shutdown(self, reason: str) -> None:
        """Trigger shutdown detection and cleanup."""
        if self._shutdown_detected:
            return  # Already shutting down

        self._shutdown_detected = True
        self._lifecycle_state = LifecycleState.LIFECYCLE_SHUTDOWN_DETECTED

        # Cancel refresh task
        if self._refresh_task:
            self._refresh_task.cancel()

        # Attempt graceful logout
        asyncio.create_task(self._graceful_shutdown(reason))

    async def _graceful_shutdown(self, reason: str) -> None:
        """Perform graceful shutdown with 10s drain deadline."""
        try:
            # Attempt logout
            async with self._client as client:
                await client.post("/api/auth/logout", timeout=5.0)
        except Exception:
            pass  # Best-effort logout

        # Persist cookie state
        try:
            # Cookie persistence handled by TUIWebClient __aexit__
            pass
        except Exception:
            pass

        # Exit after 10s drain deadline
        await asyncio.sleep(10)
        self.exit()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id is None:
            return
        panel_name = button_id.replace("btn-", "")
        switcher = self.query_one("#main-content", ContentSwitcher)
        switcher.current = f"panel-{panel_name}"

    def action_cycle_panel(self) -> None:
        """Cycle through panels."""
        switcher = self.query_one("#main-content", ContentSwitcher)
        current = switcher.current
        if current is None:
            return
        current_name = current.replace("panel-", "")
        try:
            current_index = self.PANEL_NAMES.index(current_name)
            next_index = (current_index + 1) % len(self.PANEL_NAMES)
            next_name = self.PANEL_NAMES[next_index]
            switcher.current = f"panel-{next_name}"
        except ValueError:
            pass


if __name__ == "__main__":
    app = SovereignTUI()
    app.run()
