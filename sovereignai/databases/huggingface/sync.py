"""HuggingFace sync module for downloading and updating the models database.

This module handles fetching model data from HuggingFace and populating the
hierarchical browsing fields (org, family, model_version, quant_level, etc.).
"""
import json
import re
import sqlite3
import urllib.request
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

        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self._db_path))

        from sovereignai.databases.huggingface.schema import init_schema
        init_schema(conn, self._trace)

        # Fetch popular GGUF models from HuggingFace
        # Search for models with GGUF files
        search_url = "https://huggingface.co/api/models?filter=gguf&sort=downloads&limit=100"
        req = urllib.request.Request(search_url, headers={"User-Agent": "SovereignAI/0.1"})

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:  # nosec B310
                models_data = json.loads(resp.read().decode("utf-8"))

                cursor = conn.cursor()
                inserted_count = 0

                for model_info in models_data:
                    model_id = model_info.get("modelId", "")
                    if not model_id:
                        continue

                    # Parse org and family
                    org = self.parse_org(model_id)
                    family = self.map_arch_to_family(model_info.get("architecture", ""))
                    model_version = self.parse_model_version(model_id)

                    # Get model details
                    model_url = f"https://huggingface.co/api/models/{model_id}"
                    try:
                        model_req = urllib.request.Request(model_url, headers={"User-Agent": "SovereignAI/0.1"})
                        with urllib.request.urlopen(model_req, timeout=15) as model_resp:  # nosec B310
                            model_detail = json.loads(model_resp.read().decode("utf-8"))

                            # Extract siblings (files)
                            siblings = model_detail.get("siblings", [])
                            for sibling in siblings:
                                filename = sibling.get("rfilename", "")
                                if not filename.endswith(".gguf"):
                                    continue

                                # Parse quantization
                                quant_tag, quant_level = self.parse_quant_tag(filename)
                                file_type = self.parse_file_type(filename)

                                # Get pipeline tags for category
                                tags = model_detail.get("pipeline_tag", "")
                                category = tags if tags else "other"
                                category_group = self.map_category_to_group(category)

                                # Insert into database
                                cursor.execute("""
                                    INSERT OR REPLACE INTO models (
                                        repo_id, filename, quantization, org, family,
                                        model_version, quant_level, file_type, category,
                                        category_group, downloads, likes, last_modified
                                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                """, (
                                    model_id,
                                    filename,
                                    quant_tag,
                                    org,
                                    family,
                                    model_version,
                                    quant_level,
                                    file_type,
                                    category,
                                    category_group,
                                    model_detail.get("downloads", 0),
                                    model_detail.get("likes", 0),
                                    model_detail.get("lastModified", "")
                                ))
                                inserted_count += 1
                    except Exception as e:
                        self._trace.emit(
                            component="huggingface_sync",
                            level=TraceLevel.WARN,
                            message=f"Failed to fetch details for {model_id}: {e}",
                        )
                        continue

                conn.commit()
                self._trace.emit(
                    component="huggingface_sync",
                    level=TraceLevel.INFO,
                    message=f"Inserted {inserted_count} model variants",
                )

        except Exception as e:
            self._trace.emit(
                component="huggingface_sync",
                level=TraceLevel.ERROR,
                message=f"Failed to fetch models from HuggingFace: {e}",
            )
            raise

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

        # Fetch latest models and update existing entries
        search_url = "https://huggingface.co/api/models?filter=gguf&sort=downloads&limit=100"
        req = urllib.request.Request(search_url, headers={"User-Agent": "SovereignAI/0.1"})

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:  # nosec B310
                models_data = json.loads(resp.read().decode("utf-8"))

                cursor = conn.cursor()
                updated_count = 0

                for model_info in models_data:
                    model_id = model_info.get("modelId", "")
                    if not model_id:
                        continue

                    # Check if model already exists
                    cursor.execute("SELECT repo_id FROM models WHERE repo_id = ?", (model_id,))
                    if cursor.fetchone():
                        # Update existing model
                        cursor.execute("""
                            UPDATE models SET
                                downloads = ?,
                                likes = ?,
                                last_modified = ?
                            WHERE repo_id = ?
                        """, (
                            model_info.get("downloads", 0),
                            model_info.get("likes", 0),
                            model_info.get("lastModified", ""),
                            model_id
                        ))
                        updated_count += 1
                    else:
                        # Insert new model
                        org = self.parse_org(model_id)
                        family = self.map_arch_to_family(model_info.get("architecture", ""))
                        model_version = self.parse_model_version(model_id)

                        model_url = f"https://huggingface.co/api/models/{model_id}"
                        try:
                            model_req = urllib.request.Request(model_url, headers={"User-Agent": "SovereignAI/0.1"})
                            with urllib.request.urlopen(model_req, timeout=15) as model_resp:  # nosec B310
                                model_detail = json.loads(model_resp.read().decode("utf-8"))

                                siblings = model_detail.get("siblings", [])
                                for sibling in siblings:
                                    filename = sibling.get("rfilename", "")
                                    if not filename.endswith(".gguf"):
                                        continue

                                    quant_tag, quant_level = self.parse_quant_tag(filename)
                                    file_type = self.parse_file_type(filename)
                                    tags = model_detail.get("pipeline_tag", "")
                                    category = tags if tags else "other"
                                    category_group = self.map_category_to_group(category)

                                    cursor.execute("""
                                        INSERT OR REPLACE INTO models (
                                            repo_id, filename, quantization, org, family,
                                            model_version, quant_level, file_type, category,
                                            category_group, downloads, likes, last_modified
                                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                    """, (
                                        model_id,
                                        filename,
                                        quant_tag,
                                        org,
                                        family,
                                        model_version,
                                        quant_level,
                                        file_type,
                                        category,
                                        category_group,
                                        model_detail.get("downloads", 0),
                                        model_detail.get("likes", 0),
                                        model_detail.get("lastModified", "")
                                    ))
                                    updated_count += 1
                        except Exception as e:
                            self._trace.emit(
                                component="huggingface_sync",
                                level=TraceLevel.WARN,
                                message=f"Failed to fetch details for {model_id}: {e}",
                            )
                            continue

                conn.commit()
                self._trace.emit(
                    component="huggingface_sync",
                    level=TraceLevel.INFO,
                    message=f"Updated {updated_count} model variants",
                )

        except Exception as e:
            self._trace.emit(
                component="huggingface_sync",
                level=TraceLevel.ERROR,
                message=f"Failed to update models from HuggingFace: {e}",
            )
            raise

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

    def uninstall(self) -> None:
        """Delete the HuggingFace database and clear any cached data."""
        self._trace.emit(
            component="huggingface_sync",
            level=TraceLevel.INFO,
            message="Starting HuggingFace database uninstall",
        )

        if self._db_path.exists():
            self._db_path.unlink()
            self._trace.emit(
                component="huggingface_sync",
                level=TraceLevel.INFO,
                message=f"Deleted database at {self._db_path}",
            )
        else:
            self._trace.emit(
                component="huggingface_sync",
                level=TraceLevel.WARN,
                message="Database does not exist, nothing to delete",
            )

        # Clear any cached token if stored
        token_path = Path.home() / ".sovereignai" / "databases" / "huggingface" / ".token"
        if token_path.exists():
            token_path.unlink()
            self._trace.emit(
                component="huggingface_sync",
                level=TraceLevel.INFO,
                message="Cleared HuggingFace token",
            )

        self._trace.emit(
            component="huggingface_sync",
            level=TraceLevel.INFO,
            message="HuggingFace database uninstall completed",
        )
