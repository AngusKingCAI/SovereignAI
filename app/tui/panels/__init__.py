from __future__ import annotations

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
    ("orchestrator", "tui.panels.orchestrator", "OrchestratorPanel"),
    ("workers", "tui.panels.workers", "WorkersPanel"),
    ("tasks", "tui.panels.tasks", "TasksPanel"),
    ("skills", "tui.panels.skills", "SkillsPanel"),
    ("memory", "tui.panels.memory", "MemoryPanel"),
    ("models", "tui.panels.models", "ModelsPanel"),
    ("adapters", "tui.panels.adapters", "AdaptersPanel"),
    ("hardware", "tui.panels.hardware", "HardwarePanel"),
    ("options", "tui.panels.options", "OptionsPanel"),
    ("logs", "tui.panels.logs", "LogsPanel"),
]
