from __future__ import annotations

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Static

from sovereignai.main import build_container
from tui.panels.adapters import AdaptersPanel
from tui.panels.hardware import HardwarePanel
from tui.panels.logs import LogsPanel
from tui.panels.memory import MemoryPanel
from tui.panels.models import ModelsPanel
from tui.panels.options import OptionsPanel
from tui.panels.orchestrator import OrchestratorPanel
from tui.panels.skills import SkillsPanel
from tui.panels.tasks import TasksPanel
from tui.panels.workers import WorkersPanel


class SovereignTUI(App):
    def __init__(self) -> None:
        super().__init__()
        self.container = build_container()

    def compose(self) -> ComposeResult:
        with Horizontal(id="sidebar"):
            yield Static("SovereignAI TUI", id="location-bar")
            yield Button("Orchestrator", id="btn-orchestrator")
            yield Button("Workers", id="btn-workers")
            yield Button("Tasks", id="btn-tasks")
            yield Button("Skills", id="btn-skills")
            yield Button("Memory", id="btn-memory")
            yield Button("Models", id="btn-models")
            yield Button("Adapters", id="btn-adapters")
            yield Button("Hardware", id="btn-hardware")
            yield Button("Options", id="btn-options")
            yield Button("Logs", id="btn-logs")

        with Vertical(id="main-content"):
            yield OrchestratorPanel(self.container, id="panel-orchestrator")
            yield WorkersPanel(self.container, id="panel-workers")
            yield TasksPanel(self.container, id="panel-tasks")
            yield SkillsPanel(self.container, id="panel-skills")
            yield MemoryPanel(self.container, id="panel-memory")
            yield ModelsPanel(self.container, id="panel-models")
            yield AdaptersPanel(self.container, id="panel-adapters")
            yield HardwarePanel(self.container, id="panel-hardware")
            yield OptionsPanel(self.container, id="panel-options")
            yield LogsPanel(self.container, id="panel-logs")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        panel_map = {
            "btn-orchestrator": OrchestratorPanel,
            "btn-workers": WorkersPanel,
            "btn-tasks": TasksPanel,
            "btn-skills": SkillsPanel,
            "btn-memory": MemoryPanel,
            "btn-models": ModelsPanel,
            "btn-adapters": AdaptersPanel,
            "btn-hardware": HardwarePanel,
            "btn-options": OptionsPanel,
            "btn-logs": LogsPanel,
        }
        if button_id in panel_map:
            for panel_id, panel_class in panel_map.items():
                panel = self.query_one(f"panel-{panel_id.replace('btn-', '')}", panel_class)
                if panel_id == button_id:
                    panel.remove_class("hidden")
                else:
                    panel.add_class("hidden")

            location_bar = self.query_one("#location-bar", Static)
            location_bar.update(f"Localhost:{button_id.replace('btn-', '').capitalize()}")


if __name__ == "__main__":
    app = SovereignTUI()
    app.run()
