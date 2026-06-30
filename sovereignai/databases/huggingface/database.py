"""HuggingFace database provider implementation.

This database manages the HuggingFace models catalog:
download, update, uninstall, and status.
"""
from pathlib import Path

from sovereignai.databases.base import DatabaseBase, DatabaseStatus
from sovereignai.shared.trace_emitter import TraceEmitter, TraceLevel


class HuggingFaceDatabase(DatabaseBase):
    """HuggingFace database provider implementation."""

    def __init__(self, trace: TraceEmitter | None = None) -> None:
        """Initialize the HuggingFace database.

        Args:
            trace: Trace emitter for logging operations.
        """
        self._trace = trace or TraceEmitter()
        self._db_path = Path.home() / ".sovereignai" / "databases" / "huggingface" / "models.db"

    @property
    def name(self) -> str:
        """Return the database name."""
        return "huggingface"

    def download(self) -> None:
        """Download and install the HuggingFace database."""
        self._trace.emit(
            component="HuggingFaceDatabase",
            level=TraceLevel.INFO,
            message="Starting HuggingFace database download",
        )
        self._db_path.parent.mkdir(parents=True, exist_ok=True)

        # Import sync module to perform the actual download
        try:
            from sovereignai.databases.huggingface.sync import HuggingFaceSync
            sync = HuggingFaceSync(self._trace)
            sync.download()
            self._trace.emit(
                component="HuggingFaceDatabase",
                level=TraceLevel.INFO,
                message="HuggingFace database download completed",
            )
        except Exception as exc:
            self._trace.emit(
                component="HuggingFaceDatabase",
                level=TraceLevel.ERROR,
                message=f"HuggingFace database download failed: {exc}",
            )
            raise

    def update(self) -> None:
        """Update the HuggingFace database to the latest version."""
        self._trace.emit(
            component="HuggingFaceDatabase",
            level=TraceLevel.INFO,
            message="Starting HuggingFace database update",
        )

        try:
            from sovereignai.databases.huggingface.sync import HuggingFaceSync
            sync = HuggingFaceSync(self._trace)
            sync.update()
            self._trace.emit(
                component="HuggingFaceDatabase",
                level=TraceLevel.INFO,
                message="HuggingFace database update completed",
            )
        except Exception as exc:
            self._trace.emit(
                component="HuggingFaceDatabase",
                level=TraceLevel.ERROR,
                message=f"HuggingFace database update failed: {exc}",
            )
            raise

    def uninstall(self) -> None:
        """Remove the HuggingFace database from the system."""
        self._trace.emit(
            component="HuggingFaceDatabase",
            level=TraceLevel.INFO,
            message="Starting HuggingFace database uninstall",
        )

        if self._db_path.exists():
            self._db_path.unlink()

        self._trace.emit(
            component="HuggingFaceDatabase",
            level=TraceLevel.INFO,
            message="HuggingFace database uninstall completed",
        )

    def status(self) -> DatabaseStatus:
        """Return the current status of the HuggingFace database."""
        installed = self._db_path.exists()
        size_bytes = self._db_path.stat().st_size if installed else 0
        last_updated = None
        model_count = 0
        error = None

        if installed:
            try:
                import sqlite3
                conn = sqlite3.connect(str(self._db_path))
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM models")
                model_count = cursor.fetchone()[0]
                cursor.execute("SELECT MAX(last_modified) FROM models")
                last_modified = cursor.fetchone()[0]
                if last_modified:
                    last_updated = last_modified
                conn.close()
            except Exception as exc:
                error = str(exc)

        return DatabaseStatus(
            installed=installed,
            size_bytes=size_bytes,
            last_updated=last_updated,
            model_count=model_count,
            error=error,
        )
