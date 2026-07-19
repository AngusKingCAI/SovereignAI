from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


class ProceduralMemoryAdapter:
    """Adapter for procedural memory backend."""

    def health_check(self) -> bool:
        """Check if procedural memory adapter is healthy."""
        return True
