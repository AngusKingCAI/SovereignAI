"""HuggingFace sync module for downloading and updating the models database.

This module handles fetching model data from HuggingFace and populating the
hierarchical browsing fields (org, family, model_version, quant_level, etc.).
"""
import re
import sqlite3
from pathlib import Path

from sovereignai.shared.trace_emitter import TraceEmitter, TraceLevel


class HuggingFaceSync:
    """HuggingFace database sync handler."""

    def __init__(self, trace: TraceEmitter | None = None) -> None:
        """Initialize the sync handler.

        Args:
            trace: Optional trace emitter for logging.
        """
        self._trace = trace or TraceEmitter()
        self._db_path = Path.home() / ".sovereignai" / "databases" / "huggingface" / "models.db"

        # Architecture to family mapping
        self._arch_to_family = {
            "GemmaForCausalLM": "gemma",
            "LlamaForCausalLM": "llama",
            "MistralForCausalLM": "mistral",
            "Qwen2ForCausalLM": "qwen",
            "Phi3ForCausalLM": "phi",
            "Gemma2ForCausalLM": "gemma",
            "Llama3ForCausalLM": "llama",
        }

        # Quant tag to level mapping
        self._quant_to_level = {
            "Q2_K": 20,
            "Q3_K": 30,
            "Q4_K": 40,
            "Q5_K": 50,
            "Q8_0": 80,
            "F16": 160,
        }

        # Category to group mapping
        self._category_to_group = {
            "text-generation": "nlp",
            "text-classification": "nlp",
            "token-classification": "nlp",
            "question-answering": "nlp",
            "summarization": "nlp",
            "translation": "nlp",
            "image-text-to-text": "multimodal",
            "image-text-to-image": "multimodal",
            "text-to-image": "computer_vision",
            "image-classification": "computer_vision",
            "object-detection": "computer_vision",
            "automatic-speech-recognition": "audio",
            "text-to-speech": "audio",
        }

    def download(self) -> None:
        """Download and populate the HuggingFace database."""
        self._trace.emit(
            component="huggingface_sync",
            level=TraceLevel.INFO,
            message="Starting HuggingFace database download",
        )

        # In a real implementation, this would fetch from HuggingFace API
        # For now, create empty database with schema
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self._db_path))

        from sovereignai.databases.huggingface.schema import init_schema
        init_schema(conn, self._trace)

        # TODO: Fetch actual data from HuggingFace API
        # This is a placeholder for the actual sync logic

        conn.close()
        self._trace.emit(
            component="huggingface_sync",
            level=TraceLevel.INFO,
            message="HuggingFace database download completed",
        )

    def update(self) -> None:
        """Update the HuggingFace database with latest data."""
        self._trace.emit(
            component="huggingface_sync",
            level=TraceLevel.INFO,
            message="Starting HuggingFace database update",
        )

        if not self._db_path.exists():
            self._trace.emit(
                component="huggingface_sync",
                level=TraceLevel.WARN,
                message="Database does not exist, running download instead",
            )
            self.download()
            return

        conn = sqlite3.connect(str(self._db_path))

        # Apply schema migration
        from sovereignai.databases.huggingface.schema import migrate_to_v2
        migrate_to_v2(conn, self._trace)

        # TODO: Fetch and update data from HuggingFace API
        # This is a placeholder for the actual sync logic

        conn.close()
        self._trace.emit(
            component="huggingface_sync",
            level=TraceLevel.INFO,
            message="HuggingFace database update completed",
        )

    def parse_org(self, repo_id: str) -> str:
        """Parse organization from repo_id.

        Args:
            repo_id: HuggingFace repo ID (e.g., "lmstudio-community/gemma-4-E4B-it-GGUF")

        Returns:
            Organization name (e.g., "lmstudio-community")
        """
        parts = repo_id.split("/")
        return parts[0] if len(parts) > 1 else "unknown"

    def parse_quant_tag(self, filename: str) -> tuple[str, int]:
        """Parse quantization tag and level from filename.

        Args:
            filename: Model filename (e.g., "gemma-4-E4B-it-Q4_K_M.gguf")

        Returns:
            Tuple of (quant_tag, quant_level)
        """
        # Match patterns like "Q4_K_M", "Q5_K_M", "Q8_0", etc.
        match = re.search(r"(Q[0-9]+_[A-Z_]+|F16)", filename)
        if match:
            tag = match.group(1)
            level = self._quant_to_level.get(tag, 0)
            return tag, level
        return "", 0

    def parse_file_type(self, filename: str) -> str:
        """Parse file type from filename.

        Args:
            filename: Model filename

        Returns:
            File type: gguf, safetensors, pytorch, onnx, or other
        """
        if filename.endswith(".gguf"):
            return "gguf"
        elif filename.endswith(".safetensors"):
            return "safetensors"
        elif filename.endswith((".pt", ".bin")):
            return "pytorch"
        elif filename.endswith(".onnx"):
            return "onnx"
        else:
            return "other"

    def map_arch_to_family(self, architecture: str) -> str:
        """Map architecture string to family name.

        Args:
            architecture: Architecture string from config.json

        Returns:
            Family name (e.g., "gemma", "llama")
        """
        return self._arch_to_family.get(architecture, "unknown")

    def map_category_to_group(self, category: str) -> str:
        """Map category to top-level group.

        Args:
            category: HF pipeline-tag category

        Returns:
            Top-level group (e.g., "nlp", "multimodal")
        """
        return self._category_to_group.get(category, "other")

    def parse_model_version(self, repo_id: str, config_name: str | None = None) -> str:
        """Parse model version from repo_id or config name.

        Args:
            repo_id: HuggingFace repo ID
            config_name: Optional model name from config.json

        Returns:
            Model version string
        """
        # Try to extract from repo_id (e.g., "gemma-4-E4B-it" from "lmstudio-community/gemma-4-E4B-it-GGUF")
        parts = repo_id.split("/")
        if len(parts) > 1:
            name_part = parts[1]
            # Remove suffixes like "-GGUF", "-Instruct"
            version = re.sub(r"-(GGUF|Instruct|it)$", "", name_part, flags=re.IGNORECASE)
            return version

        # Fallback to config name
        if config_name:
            return config_name

        return "unknown"
