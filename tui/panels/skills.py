from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Button, DataTable, Static

from sovereignai.shared.capability_api import CapabilityAPI


class SkillsPanel(Vertical):
    def __init__(self, container: Any, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._container = container
        self._api = None

    def compose(self) -> ComposeResult:
        yield Static("Skills", id="skills-title")
        yield Button("Refresh", id="btn-refresh")
        yield DataTable(id="skills-table")

    def on_mount(self) -> None:
        self.call_after_refresh(self._load_data)

    def _load_data(self) -> None:
        try:
            self._api = self._container.retrieve(CapabilityAPI)
            self._refresh_skills()
        except Exception as e:
            import traceback
            print(f"SkillsPanel load error: {e}")
            traceback.print_exc()

    def _refresh_skills(self) -> None:
        if self._api is None:
            return
        table = self.query_one("#skills-table", DataTable)
        table.clear(columns=True)
        table.add_column("Name")
        table.add_column("Version")
        table.add_column("Category")
        table.add_column("Actions")

        from sovereignai.shared.auth import AuthMiddleware

        try:
            auth = self._container.retrieve(AuthMiddleware)
            token = auth.generate_token("test-user")

            skills = self._api.query_skills(token)

            for skill in skills:
                table.add_row(
                    skill["name"],
                    skill["version"],
                    "Skill",
                    "[Invoke]"
                )
        except Exception:
            table.add_row("No skills registered", "", "", "")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-refresh":
            self._refresh_skills()
