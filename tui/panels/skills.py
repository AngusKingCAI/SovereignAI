from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Button, DataTable, Static

from sovereignai.shared.capability_api import CapabilityAPI
from sovereignai.shared.types import CapabilityCategory


class SkillsPanel(Vertical):
    def __init__(self, container: Any, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._container = container
        self._api = container.retrieve(CapabilityAPI)

    def compose(self) -> ComposeResult:
        yield Static("Skills", id="skills-title")
        yield DataTable(id="skills-table")

    def on_mount(self) -> None:
        self._refresh_skills()

    def _refresh_skills(self) -> None:
        table = self.query_one("#skills-table", DataTable)
        table.clear(columns=True)
        table.add_column("Name")
        table.add_column("Version")
        table.add_column("Category")
        table.add_column("Actions")

        from sovereignai.shared.types import CapabilityQuery

        query = CapabilityQuery(category=CapabilityCategory.TOOL, name="")
        response = self._api.query_capabilities("test-token", query)

        for component_id in response.providers:
            table.add_row(
                str(component_id),
                "unknown",
                "Tool",
                "[Invoke]"
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-refresh":
            self._refresh_skills()
