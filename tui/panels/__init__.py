from __future__ import annotations

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

PANEL_NAMES = [
    "orchestrator",
    "workers",
    "tasks",
    "skills",
    "memory",
    "models",
    "adapters",
    "hardware",
    "options",
    "logs",
]

PANEL_REGISTRY = [
    ("orchestrator", OrchestratorPanel),
    ("workers", WorkersPanel),
    ("tasks", TasksPanel),
    ("skills", SkillsPanel),
    ("memory", MemoryPanel),
    ("models", ModelsPanel),
    ("adapters", AdaptersPanel),
    ("hardware", HardwarePanel),
    ("options", OptionsPanel),
    ("logs", LogsPanel),
]
