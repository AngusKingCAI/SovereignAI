"""Store and query version compatibility test results.

Per OR59: the compatibility matrix is stored in ~/.sovereignai/compatibility.json,
updated on registration, uses atomic writes (os.replace), includes schema_version,
prunes to last 1000 entries, and records content_hash_a/content_hash_b per entry.

On startup, if a component's current content_hash differs from the hash in a
matrix entry, that entry is invalidated (treated as "unknown").

If the file is corrupted, the system restores from the last .backup file
(written on every successful record()); if no backup exists, rebuilds with
"unknown" statuses treated as permissive (startup proceeds, re-test on next
registration).
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sovereignai.shared.trace_emitter import TraceEmitter
    from sovereignai.shared.types import TraceLevel


@dataclass(frozen=True)
class MatrixEntry:
    """Single entry in the compatibility matrix."""

    component_a: str
    version_a: str
    content_hash_a: str
    component_b: str
    version_b: str
    content_hash_b: str
    tested_at: str  # ISO 8601 timestamp
    status: str  # "compatible", "incompatible"


class CompatibilityMatrix:
    """Manage the compatibility matrix storage and queries.

    Per Rev9: uses an in-memory buffer for record() calls, then batch-writes
    via flush() to avoid write-storm during startup with many plugins.
    """

    SCHEMA_VERSION = 1
    MAX_ENTRIES = 1000
    STORAGE_PATH = Path.home() / ".sovereignai" / "compatibility.json"
    BACKUP_PATH = Path.home() / ".sovereignai" / "compatibility.json.backup"

    def __init__(self, trace: TraceEmitter) -> None:
        """Create a compatibility matrix instance.

        Stores and queries version compatibility test results.

        Args:
            trace: Trace emitter for logging matrix operations.
        """
        self._trace = trace
        self._buffer: list[dict] = []
        self._ensure_storage_dir()

    def _ensure_storage_dir(self) -> None:
        """Ensure the storage directory for the compatibility matrix exists on the filesystem."""
        self.STORAGE_PATH.parent.mkdir(parents=True, exist_ok=True)

    def record(
        self,
        component_a: str,
        version_a: str,
        content_hash_a: str,
        component_b: str,
        version_b: str,
        content_hash_b: str,
        status: str,
    ) -> None:
        """Buffer a compatibility test result for later batch writing to disk.

        Per Rev9: appends to an in-memory buffer (does NOT write to disk
        immediately). The buffer is flushed by flush() to avoid write-storm.

        Args:
            component_a: First component ID.
            version_a: First component version.
            content_hash_a: First component content hash.
            component_b: Second component ID.
            version_b: Second component version.
            content_hash_b: Second component content hash.
            status: "compatible" or "incompatible".
        """
        from sovereignai.shared.trace_emitter import TraceEmitter, TraceLevel
        trace = TraceEmitter()
        trace.emit(
            component="compatibility_matrix",
            level=TraceLevel.DEBUG,
            message=f"Recording compatibility: {component_a} v{version_a} <-> {component_b} v{version_b} = {status}",
        )
        entry = {
            "component_a": component_a,
            "version_a": version_a,
            "content_hash_a": content_hash_a,
            "component_b": component_b,
            "version_b": version_b,
            "content_hash_b": content_hash_b,
            "tested_at": datetime.now(UTC).isoformat(),
            "status": status,
        }
        self._buffer.append(entry)

    def flush(self) -> None:
        """Write all buffered entries to disk atomically and validate the written file.

        Per Rev9: writes all buffered entries to compatibility.json atomically
        (temp + os.replace), then validates the loaded JSON before copying to
        .backup (per F11). Called once at the end of negotiate() after all
        pairs are checked.
        """
        if not self._buffer:
            return

        # Load existing data
        existing_data = self._load_with_recovery(self.STORAGE_PATH)

        # Append new entries
        existing_data["entries"].extend(self._buffer)

        # Prune to last MAX_ENTRIES
        if len(existing_data["entries"]) > self.MAX_ENTRIES:
            existing_data["entries"] = existing_data["entries"][-self.MAX_ENTRIES :]

        # Write to temp file then atomic replace
        temp_path = self.STORAGE_PATH.with_suffix(".json.tmp")
        with temp_path.open("w") as f:
            json.dump(existing_data, f, indent=2)

        os.replace(temp_path, self.STORAGE_PATH)

        # Validate the written file before creating backup
        try:
            with self.STORAGE_PATH.open("r") as f:
                json.load(f)
        except json.JSONDecodeError as e:
            self._trace.emit(
                component="compatibility_matrix",
                level=self._get_trace_level("ERROR"),
                message=f"Written compatibility.json is corrupted: {e}",
            )
            # Don't create backup if the main file is corrupted
            self._buffer.clear()
            return

        # Copy to backup
        with self.STORAGE_PATH.open("r") as src, self.BACKUP_PATH.open("w") as dst:
            dst.write(src.read())

        self._buffer.clear()

    def is_tested(
        self,
        component_a: str,
        version_a: str,
        content_hash_a: str,
        component_b: str,
        version_b: str,
        content_hash_b: str,
    ) -> bool:
        """Check if a combination was tested AND both content_hashes match.

        Per OR59: if content_hash differs, return False (stale entry).

        Args:
            component_a: First component ID.
            version_a: First component version.
            content_hash_a: First component content hash.
            component_b: Second component ID.
            version_b: Second component version.
            content_hash_b: Second component content hash.

        Returns:
            True if the combination was tested with matching content hashes,
            False otherwise.
        """
        data = self._load_with_recovery(self.STORAGE_PATH)

        for entry in data["entries"]:
            if (
                entry["component_a"] == component_a
                and entry["component_b"] == component_b
                and entry["version_a"] == version_a
                and entry["version_b"] == version_b
                and entry["content_hash_a"] == content_hash_a
                and entry["content_hash_b"] == content_hash_b
            ):
                return True

            # Check reverse order
            if (
                entry["component_a"] == component_b
                and entry["component_b"] == component_a
                and entry["version_a"] == version_b
                and entry["version_b"] == version_a
                and entry["content_hash_a"] == content_hash_b
                and entry["content_hash_b"] == content_hash_a
            ):
                return True

        return False

    def get_status(
        self,
        component_a: str,
        version_a: str,
        content_hash_a: str,
        component_b: str,
        version_b: str,
        content_hash_b: str,
    ) -> str:
        """Return the compatibility status for a component pair.

        Invalidates on content hash mismatch.

        Args:
            component_a: First component ID.
            version_a: First component version.
            content_hash_a: First component content hash.
            component_b: Second component ID.
            version_b: Second component version.
            content_hash_b: Second component content hash.

        Returns:
            "compatible", "incompatible", or "unknown".
        """
        data = self._load_with_recovery(self.STORAGE_PATH)

        for entry in data["entries"]:
            # Check forward order with matching content hashes
            if (
                entry["component_a"] == component_a
                and entry["component_b"] == component_b
                and entry["version_a"] == version_a
                and entry["version_b"] == version_b
            ):
                # Per OR59: invalidate if content_hash differs
                if (
                    entry["content_hash_a"] != content_hash_a
                    or entry["content_hash_b"] != content_hash_b
                ):
                    return "unknown"  # type: ignore[no-any-return]
                return entry["status"]  # type: ignore[no-any-return]

            # Check reverse order with matching content hashes
            if (
                entry["component_a"] == component_b
                and entry["component_b"] == component_a
                and entry["version_a"] == version_b
                and entry["version_b"] == version_a
            ):
                if (
                    entry["content_hash_a"] != content_hash_b
                    or entry["content_hash_b"] != content_hash_a
                ):
                    return "unknown"  # type: ignore[no-any-return]
                return entry["status"]  # type: ignore[no-any-return]

        return "unknown"  # type: ignore[no-any-return]

    def _load_with_recovery(self, path: Path) -> dict:  # type: ignore[no-any-return]
        """Load the compatibility matrix with corruption recovery and backup restoration.

        Per OR59: if json.load() raises on compatibility.json, try
        compatibility.json.backup. If backup also fails, rename corrupted
        file, log WARN, return empty matrix. When the matrix is empty
        (rebuilt), all statuses are "unknown" — the negotiator treats
        "unknown" as permissive (allows startup; re-tests on next registration).

        Args:
            path: Path to the matrix file to load.

        Returns:
            Dict with schema_version and entries list.
        """
        try:
            with path.open("r") as f:
                return json.load(f)  # type: ignore[no-any-return]
        except (json.JSONDecodeError, FileNotFoundError) as e:
            # Try backup
            try:
                with self.BACKUP_PATH.open("r") as f:
                    data = json.load(f)
                self._trace.emit(
                    component="compatibility_matrix",
                    level=self._get_trace_level("WARN"),
                    message=f"Main file corrupted, restored from backup: {e}",
                )
                return data  # type: ignore[no-any-return]
            except (json.JSONDecodeError, FileNotFoundError):
                # Both failed - rebuild with empty matrix
                self._trace.emit(
                    component="compatibility_matrix",
                    level=self._get_trace_level("WARN"),
                    message=f"Main file and backup corrupted, rebuilding empty matrix: {e}",
                )
                return {"schema_version": self.SCHEMA_VERSION, "entries": []}  # type: ignore[no-any-return]

    def _get_trace_level(self, level: str) -> TraceLevel:
        """Convert a string level name to the corresponding TraceLevel enum value.

        Args:
            level: String level name.

        Returns:
            TraceLevel enum value.
        """
        from sovereignai.shared.types import TraceLevel

        return TraceLevel(level.lower())  # type: ignore[return-value]
