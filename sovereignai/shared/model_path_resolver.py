from __future__ import annotations

from pathlib import Path


def default_model_path_resolver(model_id: str) -> Path:
    parts = model_id.split("/")
    base_path = Path.home() / ".sovereignai" / "models"
    for part in parts:
        base_path = base_path / part
    return base_path
