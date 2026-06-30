"""Base class for service providers.

Service providers are external services that can be downloaded, updated,
uninstalled, started, stopped, and restarted. Examples include Ollama.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass

from sovereignai.shared.trace_emitter import TraceEmitter


@dataclass
class ServiceStatus:
    """Current status of a service."""
    installed: bool
    running: bool
    version: str | None
    pid: int | None
    error: str | None


class ServiceBase(ABC):
    """Abstract base class for service providers.

    Each service provider implements methods for lifecycle management:
    download, update, uninstall, start, stop, restart, and status.
    """

    def __init__(self, trace: TraceEmitter | None = None) -> None:
        """Initialize the service provider.

        Args:
            trace: Optional trace emitter for logging operations.
        """
        self._trace = trace or TraceEmitter()

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the service name identifier for this provider instance."""
        pass

    @abstractmethod
    def download(self) -> None:
        """Download and install the service package to the local system."""
        pass

    @abstractmethod
    def update(self) -> None:
        """Update the service to the latest available version from the source."""
        pass

    @abstractmethod
    def uninstall(self) -> None:
        """Remove the service and all its files from the local system."""
        pass

    @abstractmethod
    def start(self) -> None:
        """Start the service process if it is not currently running."""
        pass

    @abstractmethod
    def stop(self) -> None:
        """Stop the service process if it is currently running."""
        pass

    @abstractmethod
    def restart(self) -> None:
        """Restart the service process by stopping and starting it again."""
        pass

    @abstractmethod
    def status(self) -> ServiceStatus:
        """Return the current runtime status of the service instance."""
        pass
