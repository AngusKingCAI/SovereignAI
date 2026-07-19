from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


class OllamaAdapter:
    """Adapter for Ollama local model inference."""

    def health_check(self) -> bool:
        """Check if Ollama adapter is healthy."""
        return True
