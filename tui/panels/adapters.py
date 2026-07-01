from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Button, DataTable, Static

from sovereignai.shared.capability_api import CapabilityAPI


class AdaptersPanel(Vertical):
    def __init__(self, container: Any, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._container = container
        self._api = container.retrieve(CapabilityAPI)

    def compose(self) -> ComposeResult:
        yield Static("Adapters", id="adapters-title")
        yield DataTable(id="adapters-table")

    def on_mount(self) -> None:
        self._refresh_adapters()

    def _refresh_adapters(self) -> None:
        table = self.query_one("#adapters-table", DataTable)
        table.clear(columns=True)
        table.add_column("Name")
        table.add_column("Status")
        table.add_column("Capabilities")
        table.add_column("Actions")

        from sovereignai.shared.types import CapabilityCategory, CapabilityQuery

        query = CapabilityQuery(category=CapabilityCategory.MODEL_INFERENCE, name="")
        response = self._api.query_capabilities("test-token", query)

        for component_id in response.providers:
            capabilities = "model_inference"
            status = "[green]Available[/green]"

            table.add_row(
                str(component_id),
                status,
                capabilities,
                "[Health Check]"
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-refresh":
            self._refresh_adapters()
