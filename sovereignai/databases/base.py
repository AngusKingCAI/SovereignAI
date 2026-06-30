"""Base class for database providers.

Database providers are external model databases that can be downloaded,
updated, and uninstalled. Examples include HuggingFace.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass

from sovereignai.shared.trace_emitter import TraceEmitter


@dataclass
class DatabaseStatus:
    """Current status of a database."""
    installed: bool
    size_bytes: int
    last_updated: str | None
    model_count: int
    error: str | None


class DatabaseBase(ABC):
    """Abstract base class for database providers.

    Each database provider implements methods for lifecycle management:
    download, update, uninstall, and status.
    """

    def __init__(self, trace: TraceEmitter | None = None) -> None:
        """Initialize the database provider.

        Args:
            trace: Optional trace emitter for logging operations.
        """
        self._trace = trace or TraceEmitter()

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the database name identifier for this provider instance."""
        pass

    @abstractmethod
    def download(self) -> None:
        """Download and install the database package to the local system."""
        pass

    @abstractmethod
    def update(self) -> None:
        """Update the database to the latest available version from the source."""
        pass

    @abstractmethod
    def uninstall(self) -> None:
        """Remove the database and all its files from the local system."""
        pass

    @abstractmethod
    def status(self) -> DatabaseStatus:
        """Return the current installation status of the database instance."""
        pass
