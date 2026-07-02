from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import DataTable, Static

from sovereignai.shared.database_registry import DatabaseRegistry
from sovereignai.shared.service_registry import ServiceRegistry


class OptionsPanel(Vertical):
    def __init__(self, container: Any, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._container = container
        self._service_registry = None
        self._database_registry = None

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
            self._service_registry = self._container.retrieve(ServiceRegistry)
            self._database_registry = self._container.retrieve(DatabaseRegistry)
            self._refresh_services()
            self._refresh_databases()
        except Exception as e:
            import traceback
            print(f"OptionsPanel mount error: {e}")
            traceback.print_exc()

    def _refresh_services(self) -> None:
        if self._service_registry is None:
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
            results = []
            for service_name in self._service_registry.list_services():
                provider = self._service_registry.get_service(service_name)
                status = provider.health_check()
                status_text = "[green]Running[/green]" if status.running else "[red]Stopped[/red]"
                pid_text = str(status.pid) if status.pid else "N/A"
                port_text = str(status.port) if status.port else "N/A"
                results.append((service_name, status_text, pid_text, port_text, status.running))
            return results

        services = fetch_services()
        for service_name, status_text, pid_text, port_text, is_running in services:
            table.add_row(
                service_name,
                status_text,
                pid_text,
                port_text,
                "[Start]" if not is_running else "[Stop]"
            )

    def _refresh_databases(self) -> None:
        if self._database_registry is None:
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
            results = []
            for db_name in self._database_registry.list_databases():
                provider = self._database_registry.get_database(db_name)
                status = provider.health_check()
                status_text = (
                    "[green]Installed[/green]"
                    if status.installed
                    else "[red]Not Installed[/red]"
                )
                model_count = len(provider.list_models())
                results.append((db_name, status_text, str(model_count)))
            return results

        databases = fetch_databases()
        for db_name, status_text, model_count in databases:
            table.add_row(
                db_name,
                status_text,
                model_count,
                "[Fetch] [Uninstall]"
            )
