from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Button, DataTable, Static

from app.tui.client import TUIWebClient


class ModelsPanel(Vertical):
    """Models panel showing model registry from /api/models.

    Extracts ModelQuery response fields and displays model ID, provider, sync status.
    Uses REST polling (SSE disabled per DEBT-7).
    """

    def __init__(
        self,
        client: TUIWebClient,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._client = client
        self._models_data: list[dict[str, Any]] = []

    def compose(self) -> ComposeResult:
        yield Static("Models", id="models-title")
        yield Button("Refresh", id="btn-refresh")
        yield DataTable(id="models-table")

    def on_mount(self) -> None:
        self.call_after_refresh(self._load_data)

    async def _load_data(self) -> None:
        """Load models from /api/models."""
        try:
            async with self._client as client:
                response = await client.get("/api/models")
                if response.status_code == 200:
                    self._models_data = response.json()
                    self._update_display()
                else:
                    self._update_error(f"HTTP {response.status_code}")
        except Exception as e:
            self._update_error(str(e))

    def _update_display(self) -> None:
        """Update display with model list."""
        try:
            table = self.query_one("#models-table", DataTable)
            table.clear(columns=True)
            table.add_column("Model ID")
            table.add_column("Provider")
            table.add_column("Sync Status")

            if not self._models_data:
                table.add_row("--", "--", "--")
                return

            for model in self._models_data[:20]:  # Limit to 20 models for display
                model_id = model.get("model_id", "unknown")
                provider = model.get("provider", "unknown")
                sync_status = model.get("sync_status", "unknown")

                # Color code sync status
                if sync_status == "synced":
                    status_badge = "[green]Synced[/green]"
                elif sync_status == "syncing":
                    status_badge = "[blue]Syncing…[/blue]"
                elif sync_status == "error":
                    status_badge = "[red]Error[/red]"
                else:
                    status_badge = f"[yellow]{sync_status}[/yellow]"

                table.add_row(model_id, provider, status_badge)
        except Exception:
            # Widget tree not mounted (e.g., during testing)
            pass

    def _update_error(self, error_msg: str) -> None:
        """Update display with error message."""
        try:
            table = self.query_one("#models-table", DataTable)
            table.clear(columns=True)
            table.add_column("Model ID")
            table.add_column("Provider")
            table.add_column("Sync Status")
            table.add_row(f"Error: {error_msg}", "--", "--")
        except Exception:
            # Widget tree not mounted (e.g., during testing)
            pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-refresh":
            self.call_after_refresh(self._load_data)
