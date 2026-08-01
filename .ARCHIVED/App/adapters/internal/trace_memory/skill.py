from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


class TraceMemoryAdapter:
    """Adapter for trace memory backend."""

    def health_check(self) -> bool:
        """Check if trace memory adapter is healthy."""
        return True
