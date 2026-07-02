from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Button, DataTable, Static


class WorkersPanel(Vertical):
    def __init__(self, container: Any, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._container = container

    def compose(self) -> ComposeResult:
        yield Static("Workers", id="workers-title")
        yield Button("Refresh", id="btn-refresh")
        yield DataTable(id="workers-table")

    def on_mount(self) -> None:
        self._refresh_workers()

    def _refresh_workers(self) -> None:
        table = self.query_one("#workers-table", DataTable)
        table.clear(columns=True)
        table.add_column("Name")
        table.add_column("Department")
        table.add_column("Model")
        table.add_column("Status")
        table.add_column("Actions")

        from sovereignai.shared.lifecycle_manager import LifecycleManager

        try:
            lifecycle = self._container.retrieve(LifecycleManager)
            for component_id in lifecycle.list_components():
                status = lifecycle.get_status(component_id)
                status_text = "[green]Active[/green]" if status == "ACTIVE" else f"[yellow]{status}[/yellow]"
                table.add_row(
                    str(component_id),
                    "General",
                    "Auto-assigned",
                    status_text,
                    "[Test]"
                )
        except Exception:
            table.add_row("No workers registered", "", "", "", "")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-refresh":
            self._refresh_workers()
