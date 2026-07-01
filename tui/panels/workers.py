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

        table.add_row(
            "TestWorker",
            "Test",
            "Auto-assigned",
            "Ready",
            "[Test]"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-refresh":
            self._refresh_workers()
