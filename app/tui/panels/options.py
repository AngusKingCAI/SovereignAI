from __future__ import annotations

from typing import Any

from sovereignai.shared.capability_api import CapabilityAPI
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import DataTable, Static


class OptionsPanel(Vertical):
    def __init__(self, container: Any, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._container = container
        self._api = None

    def compose(self) -> ComposeResult:
        yield Static("Services", id="services-title")
        yield DataTable(id="services-table")
        yield Static("Databases", id="databases-title")
        yield DataTable(id="databases-table")

    def on_mount(self) -> None:
        print("OptionsPanel on_mount called", flush=True)
        self.call_after_refresh(self._load_data)

    def _load_data(self) -> None:
        try:
            self._api = self._container.retrieve(CapabilityAPI)
            self._refresh_services()
            self._refresh_databases()
        except Exception as e:
            import traceback
            print(f"OptionsPanel mount error: {e}")
            traceback.print_exc()

    def _refresh_services(self) -> None:
        if self._api is None:
            return
        table = self.query_one("#services-table", DataTable)
        table.clear(columns=True)
        table.add_column("Name")
        table.add_column("Status")
        table.add_column("PID")
        table.add_column("Port")
        table.add_column("Actions")

        from textual import work

        @work(thread=True)
        def fetch_services():
            from sovereignai.shared.auth import AuthError
            try:
                return self._api.query_service_registry("dummy_token")
            except AuthError:
                return []

        services = fetch_services()
        for service_name, status in services:
            status_text = "[green]Running[/green]" if status.running else "[red]Stopped[/red]"
            pid_text = str(status.pid) if status.pid else "N/A"
            port_text = str(status.port) if status.port else "N/A"
            table.add_row(
                service_name,
                status_text,
                pid_text,
                port_text,
                "[Start]" if not status.running else "[Stop]"
            )

    def _refresh_databases(self) -> None:
        if self._api is None:
            return
        table = self.query_one("#databases-table", DataTable)
        table.clear(columns=True)
        table.add_column("Name")
        table.add_column("Status")
        table.add_column("Model Count")
        table.add_column("Actions")

        from textual import work

        @work(thread=True)
        def fetch_databases():
            from sovereignai.shared.auth import AuthError
            try:
                models = self._api.query_model_catalog("dummy_token")
                return len(models)
            except AuthError:
                return 0

        model_count = fetch_databases()
        table.add_row(
            "huggingface",
            "[green]Installed[/green]",
            str(model_count),
            "[Fetch] [Uninstall]"
        )
