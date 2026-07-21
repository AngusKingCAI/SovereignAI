from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Button, DataTable, Static

from app.tui.client import TUIWebClient


class MemoryPanel(Vertical):
    """Memory panel showing cross-task memory graph status.

    Forward dependency on Plan 34. Shows PENDING badge until
    /api/orchestrator/memory/graph returns 200 after Plan 34 deployment.

    Memory panel state:
    - 404 → PENDING (Plan 31 not yet deployed)
    - 503 with error_code=memory_not_ready → Loading… (transient, Plan 34 backend not loaded)
    - 200 → Live (Plan 34 active)

    Poll interval for PENDING state: 30s.
    """

    def __init__(
        self,
        client: TUIWebClient,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._client = client
        self._memory_status: str = "PENDING"

    def compose(self) -> ComposeResult:
        yield Static("Memory Graph", id="memory-title")
        yield Button("Refresh", id="btn-refresh")
        yield DataTable(id="memory-table")

    def on_mount(self) -> None:
        self.call_after_refresh(self._load_data)

    async def _load_data(self) -> None:
        """Load memory status from /api/orchestrator/memory/graph."""
        try:
            async with self._client as client:
                response = await client.get("/api/orchestrator/memory/graph")

                if response.status_code == 200:
                    self._memory_status = "Live"
                    self._update_display_live(response.json())
                elif response.status_code == 503:
                    error_data = response.json()
                    error_code = error_data.get("error_code", "")
                    if error_code == "memory_not_ready":
                        self._memory_status = "Loading…"
                        self._update_display_loading()
                    else:
                        self._memory_status = "Error"
                        self._update_display_error(f"503: {error_code}")
                elif response.status_code == 404:
                    self._memory_status = "PENDING"
                    self._update_display_pending()
                else:
                    self._memory_status = "Error"
                    self._update_display_error(f"HTTP {response.status_code}")
        except Exception as e:
            self._memory_status = "Error"
            self._update_display_error(str(e))

    def _update_display_pending(self) -> None:
        """Update display for PENDING state (Plan 34 not deployed)."""
        try:
            title = self.query_one("#memory-title", Static)
            title.update("Memory Graph [yellow]PENDING[/]")

            table = self.query_one("#memory-table", DataTable)
            table.clear(columns=True)
            table.add_column("Status")
            table.add_column("Description")
            table.add_row(
                "[yellow]PENDING[/]",
                "Memory graph not yet available (Plan 34)"
            )
        except Exception:
            # Widget tree not mounted (e.g., during testing)
            pass

    def _update_display_loading(self) -> None:
        """Update display for Loading state (Plan 34 backend loading)."""
        try:
            title = self.query_one("#memory-title", Static)
            title.update("Memory Graph [blue]Loading…[/]")

            table = self.query_one("#memory-table", DataTable)
            table.clear(columns=True)
            table.add_column("Status")
            table.add_column("Description")
            table.add_row(
                "[blue]Loading…[/]",
                "Memory graph backend initializing"
            )
        except Exception:
            # Widget tree not mounted (e.g., during testing)
            pass

    def _update_display_live(self, data: dict[str, Any]) -> None:
        """Update display for Live state (Plan 34 active)."""
        try:
            title = self.query_one("#memory-title", Static)
            title.update("Memory Graph [green]Live[/]")

            table = self.query_one("#memory-table", DataTable)
            table.clear(columns=True)
            table.add_column("Metric")
            table.add_column("Value")

            # Display memory graph metrics
            nodes = data.get("nodes", 0)
            edges = data.get("edges", 0)
            table.add_row("Nodes", str(nodes))
            table.add_row("Edges", str(edges))
        except Exception:
            # Widget tree not mounted (e.g., during testing)
            pass

    def _update_display_error(self, error_msg: str) -> None:
        """Update display for error state."""
        try:
            title = self.query_one("#memory-title", Static)
            title.update("Memory Graph [red]Error[/]")

            table = self.query_one("#memory-table", DataTable)
            table.clear(columns=True)
            table.add_column("Status")
            table.add_column("Description")
            table.add_row(
                "[red]Error[/]",
                error_msg
            )
        except Exception:
            # Widget tree not mounted (e.g., during testing)
            pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-refresh":
            self.call_after_refresh(self._load_data)
