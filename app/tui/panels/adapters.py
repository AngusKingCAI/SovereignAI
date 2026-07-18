from __future__ import annotations

from typing import Any

from sovereignai.shared.capability_api import CapabilityAPI
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Button, DataTable, Static


class AdaptersPanel(Vertical):
    def __init__(self, container: Any, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._container = container
        self._api = None

    def compose(self) -> ComposeResult:
        yield Static("Adapters", id="adapters-title")
        yield Button("Refresh", id="btn-refresh")
        yield DataTable(id="adapters-table")

    def on_mount(self) -> None:
        self.call_after_refresh(self._load_data)

    def _load_data(self) -> None:
        try:
            self._api = self._container.retrieve(CapabilityAPI)
            self._refresh_adapters()
        except Exception as e:
            import traceback
            print(f"AdaptersPanel load error: {e}")
            traceback.print_exc()

    def _refresh_adapters(self) -> None:
        if self._api is None:
            return
        table = self.query_one("#adapters-table", DataTable)
        table.clear(columns=True)
        table.add_column("Name")
        table.add_column("Status")
        table.add_column("Capabilities")
        table.add_column("Actions")

        from sovereignai.shared.auth import AuthMiddleware
        from sovereignai.shared.types import CapabilityCategory, CapabilityQuery

        try:
            auth = self._container.retrieve(AuthMiddleware)
            token = auth.generate_token("test-user")

            query = CapabilityQuery(category=CapabilityCategory.MODEL_INFERENCE, name="")
            response = self._api.query_capabilities(token, query)

            for component_id in response.providers:
                capabilities = "model_inference"
                status = "[green]Available[/green]"

                table.add_row(
                    str(component_id),
                    status,
                    capabilities,
                    "[Health Check]"
                )
        except Exception:
            table.add_row("No adapters registered", "", "", "")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-refresh":
            self._refresh_adapters()
