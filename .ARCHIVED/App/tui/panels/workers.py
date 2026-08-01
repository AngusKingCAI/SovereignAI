from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Button, DataTable, Static

from app.tui.client import TUIWebClient


class WorkersPanel(Vertical):
    """Workers panel showing worker subsystems from /api/health.

    Filters subsystems by kind="worker" and displays name + status badge.
    Uses REST polling (SSE disabled per DEBT-7).
    """

    def __init__(
        self,
        client: TUIWebClient,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._client = client
        self._health_data: dict[str, Any] = {}

    def compose(self) -> ComposeResult:
        yield Static("Workers", id="workers-title")
        yield Button("Refresh", id="btn-refresh")
        yield DataTable(id="workers-table")

    def on_mount(self) -> None:
        self.call_after_refresh(self._load_data)

    async def _load_data(self) -> None:
        """Load health data from /api/health."""
        try:
            async with self._client as client:
                response = await client.get("/api/health")
                if response.status_code == 200:
                    self._health_data = response.json()
                    self._update_display()
                else:
                    self._update_error(f"HTTP {response.status_code}")
        except Exception as e:
            self._update_error(str(e))

    def _update_display(self) -> None:
        """Update display with worker subsystems."""
        try:
            table = self.query_one("#workers-table", DataTable)
            table.clear(columns=True)
            table.add_column("Name")
            table.add_column("Status")

            subsystems = self._health_data.get("subsystems", [])
            workers = [s for s in subsystems if s.get("kind") == "worker"]

            if not workers:
                table.add_row("No workers registered", "--")
                return

            for worker in workers:
                name = worker.get("name", "unknown")
                status = worker.get("status", "unknown")

                # Color code status
                if status == "healthy":
                    status_badge = "[green]Healthy[/green]"
                elif status == "degraded":
                    status_badge = "[yellow]Degraded[/yellow]"
                elif status == "unhealthy":
                    status_badge = "[red]Unhealthy[/red]"
                else:
                    status_badge = f"[yellow]{status}[/yellow]"

                table.add_row(name, status_badge)
        except Exception:
            # Widget tree not mounted (e.g., during testing)
            pass

    def _update_error(self, error_msg: str) -> None:
        """Update display with error message."""
        try:
            table = self.query_one("#workers-table", DataTable)
            table.clear(columns=True)
            table.add_column("Name")
            table.add_column("Status")
            table.add_row(f"Error: {error_msg}", "--")
        except Exception:
            # Widget tree not mounted (e.g., during testing)
            pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-refresh":
            self.call_after_refresh(self._load_data)
