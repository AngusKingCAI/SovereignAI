from __future__ import annotations

import json
import os
import shutil
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from databases.base import (
    DatabaseStatus,
    ModelNotFoundError,
    NoCompatibleQuantError,
)
from sovereignai.shared.quant_priority import QUANT_PRIORITY, select_best_quant
from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import ModelEntry, TraceLevel

if TYPE_CHECKING:
    from huggingface_hub import HfApi


@dataclass(frozen=True)
class ModelInfo:
    model_id: str
    filename: str
    quant: str
    downloaded_at: str


class HFDatabaseProvider:
    name = "huggingface"

    def __init__(self, trace: TraceEmitter, cache_dir: Path) -> None:
        self._trace = trace
        self._cache_dir = cache_dir
        self._cached_models: list[ModelEntry] | None = None
        self._cache_time: float = 0
        self._cache_ttl: float = 3600

    def _get_hf_api(self) -> HfApi:
        from huggingface_hub import HfApi

        return HfApi()

    def list_models(self) -> list[ModelEntry]:
        import os

        if os.environ.get("SOVEREIGNAI_TEST_MODE") == "1":
            return []

        now = time.monotonic()
        if (
            self._cached_models is not None
            and now - self._cache_time < self._cache_ttl
        ):
            return self._cached_models

        api = self._get_hf_api()
        models = api.list_models(filter="gguf", sort="downloads", limit=500)

        result: list[ModelEntry] = []
        for model in models:
            model_id = model.modelId
            parts = model_id.split("/")
            if len(parts) < 2:
                continue
            org, family = parts[0], parts[1]

            try:
                card = api.model_info(model_id)
                num_layers = 32
                if card.cardData and "num_layers" in card.cardData:
                    num_layers = card.cardData["num_layers"]
            except Exception:
                num_layers = 32

            result.append(
                ModelEntry(
                    org=org,
                    family=family,
                    version="latest",
                    quant="gguf",
                    file_size_bytes=0,
                    vram_required_mb=0,
                    num_layers=num_layers,
                    category="llm",
                    source_db="huggingface",
                )
            )

        self._cached_models = result
        self._cache_time = now
        return result

    def download_model(self, model_id: str) -> None:
        from huggingface_hub import hf_hub_download

        api = self._get_hf_api()
        try:
            repo_info = api.model_info(model_id)
        except Exception:
            raise ModelNotFoundError(model_id) from None

        gguf_files = [
            f.rfilename for f in repo_info.siblings if f.rfilename.endswith(".gguf")
        ] if repo_info.siblings else []

        if not gguf_files:
            self._trace.emit(
                component="HFDatabaseProvider",
                level=TraceLevel.ERROR,
                message=f"No GGUF files found in repo {model_id}",
            )
            raise NoCompatibleQuantError(model_id)

        quants = []
        for f in gguf_files:
            for q in QUANT_PRIORITY:
                if q in f:
                    quants.append(q)
                    break

        selected_quant = select_best_quant(quants)
        if selected_quant is None:
            self._trace.emit(
                component="HFDatabaseProvider",
                level=TraceLevel.ERROR,
                message=f"No compatible quantization in repo {model_id}",
            )
            raise NoCompatibleQuantError(model_id)

        selected_file = None
        for f in gguf_files:
            if selected_quant in f:
                selected_file = f
                break

        if selected_file is None:
            raise NoCompatibleQuantError(model_id)

        parts = model_id.split("/")
        org, name = parts[0], parts[1]
        local_dir = Path.home() / ".sovereignai" / "models" / org / name

        try:
            self._trace.emit(
                component="HFDatabaseProvider",
                level=TraceLevel.INFO,
                message=f"Downloading {model_id} with quant {selected_quant}",
            )

            hf_hub_download(
                repo_id=model_id,
                filename=selected_file,
                local_dir=local_dir,
                revision="main",
            )  # nosec B615

            model_info = ModelInfo(
                model_id=model_id,
                filename=selected_file,
                quant=selected_quant,
                downloaded_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            )

            metadata_path = local_dir / "model_info.json"
            local_dir.mkdir(parents=True, exist_ok=True)
            temp_fd, temp_path = tempfile.mkstemp(
                dir=str(local_dir), suffix=".tmp", text=True
            )
            try:
                os.close(temp_fd)
                with open(temp_path, "w") as f:  # type: ignore
                    json.dump(model_info.__dict__, f)  # type: ignore
                os.replace(temp_path, metadata_path)
            except Exception:
                import contextlib
                with contextlib.suppress(Exception):
                    os.unlink(temp_path)
                raise

            self._trace.emit(
                component="HFDatabaseProvider",
                level=TraceLevel.INFO,
                message=f"Download complete for {model_id}",
            )
        except Exception as e:
            shutil.rmtree(local_dir, ignore_errors=True)
            self._trace.emit(
                component="HFDatabaseProvider",
                level=TraceLevel.ERROR,
                message=f"Download failed for {model_id}: {str(e)}",
            )
            raise

    def update_model(self, model_id: str) -> None:
        self.download_model(model_id)

    def uninstall_model(self, model_id: str) -> None:
        parts = model_id.split("/")
        org, name = parts[0], parts[1]
        local_dir = Path.home() / ".sovereignai" / "models" / org / name

        metadata_path = local_dir / "model_info.json"
        if metadata_path.exists():
            temp_fd, temp_path = tempfile.mkstemp(
                dir=str(local_dir), suffix=".tmp", text=True
            )
            try:
                os.close(temp_fd)
                os.unlink(temp_path)
            except Exception:
                pass

        shutil.rmtree(local_dir, ignore_errors=True)

    def health_check(self) -> DatabaseStatus:
        import os

        if os.environ.get("SOVEREIGNAI_TEST_MODE") == "1":
            return DatabaseStatus(
                installed=True,
                version="test-mode",
                size_bytes=0,
            )

        hf_cache = Path.home() / ".cache" / "huggingface"
        installed = hf_cache.exists()

        try:
            api = self._get_hf_api()
            api.whoami()
            version = "connected"
        except Exception:
            version = None

        size_bytes = 0
        if installed:
            import contextlib

            with contextlib.suppress(Exception):
                size_bytes = sum(
                    f.stat().st_size for f in hf_cache.rglob("*") if f.is_file()
                )

        return DatabaseStatus(
            installed=installed,
            version=version,
            size_bytes=size_bytes,
        )
