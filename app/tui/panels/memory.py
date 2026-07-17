from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Button, DataTable, RichLog, Static

from app.sovereignai.shared.capability_api import CapabilityAPI


class MemoryPanel(Vertical):
    def __init__(self, container: Any, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._container = container
        self._api = None

    def compose(self) -> ComposeResult:
        yield Static("Memory Backends", id="memory-title")
        yield Button("Refresh", id="btn-refresh")
        yield DataTable(id="memory-table")
        yield RichLog(id="trace-log")

    def on_mount(self) -> None:
        self.call_after_refresh(self._load_data)

    def _load_data(self) -> None:
        try:
            self._api = self._container.retrieve(CapabilityAPI)
            self._refresh_memory_table()
        except Exception as e:
            import traceback
            print(f"MemoryPanel load error: {e}")
            traceback.print_exc()

    def _refresh_memory_table(self) -> None:
        if self._api is None:
            return
        table = self.query_one("#memory-table", DataTable)
        table.clear(columns=True)
        table.add_column("Backend")
        table.add_column("Type")
        table.add_column("Status")
        table.add_column("Used MB")
        table.add_column("Capacity MB")

        from textual import work

        @work(thread=True)
        def fetch_stats():
            from sovereignai.shared.auth import AuthError
            try:
                return self._api.query_memory_backends("dummy_token")
            except AuthError:
                return []

        backends = fetch_stats()
        for backend in backends:
            table.add_row(
                backend.name,
                backend.type,
                backend.status,
                str(backend.used_mb),
                str(backend.capacity_mb),
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-refresh":
            self._refresh_memory_table()
