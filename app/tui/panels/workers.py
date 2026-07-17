from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Button, DataTable, Static

from app.sovereignai.shared.lifecycle_manager import LifecycleManager


class WorkersPanel(Vertical):
    def __init__(self, container: Any, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._container = container
        self._lifecycle = None

    def compose(self) -> ComposeResult:
        yield Static("Workers", id="workers-title")
        yield Button("Refresh", id="btn-refresh")
        yield DataTable(id="workers-table")

    def on_mount(self) -> None:
        self.call_after_refresh(self._load_data)

    def _load_data(self) -> None:
        try:
            self._lifecycle = self._container.retrieve(LifecycleManager)
            self._refresh_workers()
        except Exception as e:
            import traceback
            print(f"WorkersPanel load error: {e}")
            traceback.print_exc()

    def _refresh_workers(self) -> None:
        if self._lifecycle is None:
            return
        table = self.query_one("#workers-table", DataTable)
        table.clear(columns=True)
        table.add_column("Name")
        table.add_column("Department")
        table.add_column("Model")
        table.add_column("Status")
        table.add_column("Actions")

        from textual import work

        @work(thread=True)
        def fetch_components():
            results = []
            for component_id in self._lifecycle.list_components():
                status = self._lifecycle.get_status(component_id)
                results.append((str(component_id), str(status)))
            return results

        components = fetch_components()
        for component_id, status in components:
            status_text = (
                "[green]Active[/green]"
                if status == "ACTIVE"
                else f"[yellow]{status}[/yellow]"
            )
            table.add_row(
                component_id,
                "General",
                "Auto-assigned",
                status_text,
                "[Test]"
            )

        if not components:
            table.add_row("No workers registered", "", "", "", "")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-refresh":
            self._refresh_workers()
