from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


class WorkingMemoryAdapter:
    """Adapter for working memory backend."""

    def health_check(self) -> bool:
        """Check if working memory adapter is healthy."""
        return True
