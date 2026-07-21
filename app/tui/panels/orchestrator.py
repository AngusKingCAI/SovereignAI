from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static

from app.tui.client import TUIWebClient


class OrchestratorPanel(Vertical):
    """Orchestrator status panel showing state, uptime, and task metrics.

    Fetches from /api/orchestrator/status via REST polling (SSE disabled per DEBT-7).
    """

    def __init__(
        self,
        client: TUIWebClient,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._client = client
        self._status_data: dict[str, Any] = {}

    def compose(self) -> ComposeResult:
        yield Static("Orchestrator Status", id="orchestrator-title")
        yield Static("State: Loading...", id="orchestrator-state")
        yield Static("Uptime: --", id="orchestrator-uptime")
        yield Static("Tasks Completed: --", id="orchestrator-completed")
        yield Static("Tasks Failed: --", id="orchestrator-failed")

    def on_mount(self) -> None:
        self.call_after_refresh(self._load_data)

    async def _load_data(self) -> None:
        """Load orchestrator status from /api/orchestrator/status."""
        try:
            async with self._client as client:
                response = await client.get("/api/orchestrator/status")
                if response.status_code == 200:
                    self._status_data = response.json()
                    self._update_display()
                else:
                    self._update_error(f"HTTP {response.status_code}")
        except Exception as e:
            self._update_error(str(e))

    def _update_display(self) -> None:
        """Update display with orchestrator status data."""
        try:
            state_widget = self.query_one("#orchestrator-state", Static)
            uptime_widget = self.query_one("#orchestrator-uptime", Static)
            completed_widget = self.query_one("#orchestrator-completed", Static)
            failed_widget = self.query_one("#orchestrator-failed", Static)

            state = self._status_data.get("state", "unknown")
            uptime = self._status_data.get("uptime_seconds", 0)
            completed = self._status_data.get("tasks_completed", 0)
            failed = self._status_data.get("tasks_failed", 0)

            state_widget.update(f"State: {state}")
            uptime_widget.update(f"Uptime: {uptime}s")
            completed_widget.update(f"Tasks Completed: {completed}")
            failed_widget.update(f"Tasks Failed: {failed}")
        except Exception:
            # Widget tree not mounted (e.g., during testing)
            pass

    def _update_error(self, error_msg: str) -> None:
        """Update display with error message."""
        try:
            state_widget = self.query_one("#orchestrator-state", Static)
            state_widget.update(f"State: Error - {error_msg}")
        except Exception:
            # Widget tree not mounted (e.g., during testing)
            pass
