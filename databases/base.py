from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from sovereignai.shared.types import ModelEntry


@dataclass(frozen=True)
class DatabaseStatus:
    installed: bool
    version: str | None
    size_bytes: int | None


class DatabaseProvider(Protocol):
    name: str

    def list_models(self) -> list[ModelEntry]:
        ...

    def download_model(self, model_id: str) -> None:
        ...

    def update_model(self, model_id: str) -> None:
        ...

    def uninstall_model(self, model_id: str) -> None:
        ...

    def health_check(self) -> DatabaseStatus:
        ...


class NoCompatibleQuantError(Exception):

    def __init__(self, repo_id: str) -> None:
        self.repo_id = repo_id
        super().__init__(f"No compatible GGUF quantization found in repo {repo_id}")


class ModelNotFoundError(Exception):

    def __init__(self, model_id: str) -> None:
        self.model_id = model_id
        super().__init__(f"Model {model_id} not found")
