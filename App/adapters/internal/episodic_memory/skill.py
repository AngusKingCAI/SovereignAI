from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


class EpisodicMemoryAdapter:
    """Adapter for episodic memory backend."""

    def health_check(self) -> bool:
        """Check if episodic memory adapter is healthy."""
        return True
