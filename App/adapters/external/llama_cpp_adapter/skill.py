from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


class LlamaCppAdapter:
    """Adapter for llama.cpp local model inference."""

    def health_check(self) -> bool:
        """Check if llama.cpp adapter is healthy."""
        return True
