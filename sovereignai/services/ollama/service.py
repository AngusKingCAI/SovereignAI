"""Ollama service provider implementation.

This service manages the Ollama local model server lifecycle:
download, update, uninstall, start, stop, restart, and status.
"""
import platform
import subprocess
import urllib.request
from pathlib import Path

from sovereignai.services.base import ServiceBase, ServiceStatus
from sovereignai.shared.trace_emitter import TraceEmitter, TraceLevel


class OllamaService(ServiceBase):
    """Ollama service provider implementation."""

    def __init__(self, trace: TraceEmitter | None = None) -> None:
        """Initialize the Ollama service.

        Args:
            trace: Trace emitter for logging operations.
        """
        self._trace = trace or TraceEmitter()
        self._install_dir = Path.home() / ".sovereignai" / "services" / "ollama"
        self._binary_path = self._install_dir / "ollama"
        if platform.system() == "Windows":
            self._binary_path = self._install_dir / "ollama.exe"

    @property
    def name(self) -> str:
        """Return the service name."""
        return "ollama"

    def download(self) -> None:
        """Download and install Ollama."""
        self._trace.emit(
            component="OllamaService",
            level=TraceLevel.INFO,
            message="Starting Ollama download",
        )
        self._install_dir.mkdir(parents=True, exist_ok=True)

        system = platform.system().lower()
        machine = platform.machine().lower()

        if system == "windows":
            url = "https://ollama.com/download/OllamaSetup.exe"
            dest = self._install_dir / "OllamaSetup.exe"
        elif system == "darwin":
            if machine == "arm64":
                url = "https://ollama.com/download/Ollama-darwin-arm64"
            else:
                url = "https://ollama.com/download/Ollama-darwin"
            dest = self._binary_path
        elif system == "linux":
            if machine == "aarch64":
                url = "https://ollama.com/download/ollama-linux-arm64"
            else:
                url = "https://ollama.com/download/ollama-linux-amd64"
            dest = self._binary_path
        else:
            raise RuntimeError(f"Unsupported platform: {system}")

        self._trace.emit(
            component="OllamaService",
            level=TraceLevel.DEBUG,
            message=f"Downloading from {url}",
        )

        try:
            urllib.request.urlretrieve(url, dest)
            if system != "windows":
                dest.chmod(0o755)
            self._trace.emit(
                component="OllamaService",
                level=TraceLevel.INFO,
                message="Ollama download completed successfully",
            )
        except Exception as exc:
            self._trace.emit(
                component="OllamaService",
                level=TraceLevel.ERROR,
                message=f"Ollama download failed: {exc}",
            )
            raise

    def update(self) -> None:
        """Update Ollama to the latest version."""
        self._trace.emit(
            component="OllamaService",
            level=TraceLevel.INFO,
            message="Starting Ollama update",
        )
        # For Ollama, update is the same as download
        self.download()

    def uninstall(self) -> None:
        """Remove Ollama from the system."""
        self._trace.emit(
            component="OllamaService",
            level=TraceLevel.INFO,
            message="Starting Ollama uninstall",
        )

        if self._install_dir.exists():
            import shutil
            shutil.rmtree(self._install_dir)

        self._trace.emit(
            component="OllamaService",
            level=TraceLevel.INFO,
            message="Ollama uninstall completed",
        )

    def start(self) -> None:
        """Start the Ollama service."""
        self._trace.emit(
            component="OllamaService",
            level=TraceLevel.INFO,
            message="Starting Ollama service",
        )

        if not self._binary_path.exists():
            raise RuntimeError("Ollama is not installed. Run download first.")

        # Pre-flight check: verify Ollama is not already running
        current_status = self.status()
        if current_status.running:
            self._trace.emit(
                component="OllamaService",
                level=TraceLevel.WARN,
                message="Ollama is already running, skipping start",
            )
            return

        try:
            subprocess.Popen(
                [str(self._binary_path), "serve"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
            )
            self._trace.emit(
                component="OllamaService",
                level=TraceLevel.INFO,
                message="Ollama service started",
            )
        except Exception as exc:
            self._trace.emit(
                component="OllamaService",
                level=TraceLevel.ERROR,
                message=f"Failed to start Ollama: {exc}",
            )
            raise

    def stop(self) -> None:
        """Stop the Ollama service."""
        self._trace.emit(
            component="OllamaService",
            level=TraceLevel.INFO,
            message="Stopping Ollama service",
        )

        try:
            if platform.system() == "Windows":
                subprocess.run(["taskkill", "/F", "/IM", "ollama.exe"], check=True)
            else:
                subprocess.run(["pkill", "ollama"], check=True)
            self._trace.emit(
                component="OllamaService",
                level=TraceLevel.INFO,
                message="Ollama service stopped",
            )
        except subprocess.CalledProcessError as exc:
            self._trace.emit(
                component="OllamaService",
                level=TraceLevel.WARN,
                message=f"Ollama may not have been running: {exc}",
            )

    def restart(self) -> None:
        """Restart the Ollama service."""
        self._trace.emit(
            component="OllamaService",
            level=TraceLevel.INFO,
            message="Restarting Ollama service",
        )
        self.stop()
        self.start()

    def status(self) -> ServiceStatus:
        """Return the current status of Ollama."""
        installed = self._binary_path.exists()
        running = False
        version = None
        pid = None
        error = None

        if installed:
            try:
                # Check if running by trying to list models
                import ollama
                ollama.list()
                running = True
            except Exception:
                running = None

            try:
                result = subprocess.run(
                    [str(self._binary_path), "--version"],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                version = result.stdout.strip()
            except Exception as exc:
                error = str(exc)

        return ServiceStatus(
            installed=installed,
            running=running,
            version=version,
            pid=pid,
            error=error,
        )
