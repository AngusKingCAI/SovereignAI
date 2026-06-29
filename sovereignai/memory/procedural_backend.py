"""Procedural memory backend using JSON file for pattern storage.

Per OR87: Stores procedural memory in ~/.sovereignai/procedural_memory.json.
Per OR89: Uses atomic writes (temp file + os.replace) and file lock with timeout.
The lock is NEVER force-acquired — if held >5 seconds, write fails with WARN trace.
"""
from __future__ import annotations

import json
import os
import time
import uuid
from typing import TYPE_CHECKING

from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import TraceLevel

if TYPE_CHECKING:
    pass


MAX_PATTERNS = 1000


class ProceduralMemoryLockTimeoutError(Exception):
    """Raised when the procedural memory lock cannot be acquired within the timeout.

    Per OR89: The lock is NEVER force-acquired. If held >5 seconds, the write fails.
    """


class ProceduralMemoryBackend:
    """JSON backend for procedural memory — stores learned patterns and skills.

    Per OR89: Uses atomic writes with temp file + os.replace. Lock file is never
    force-acquired; if held >5 seconds, write fails with WARN trace.
    """

    def __init__(self, trace: TraceEmitter) -> None:
        """Create a procedural memory backend with a JSON file for pattern storage.

        Args:
            trace: Trace emitter for logging operations and errors.
        """
        self._trace = trace
        self._path = os.path.expanduser("~/.sovereignai/procedural_memory.json")
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """Create the JSON file with an empty patterns list if it does not exist."""
        if not os.path.exists(self._path):
            os.makedirs(os.path.dirname(self._path), exist_ok=True)
            self._atomic_write([])

    def _acquire_lock(self, timeout_s: float = 5.0) -> bool:
        """Try to acquire the lock file. Return True if acquired, False on timeout.

        NEVER force-acquires. If the lock is held longer than timeout_s,
        returns False (preserving mutex safety per P9).

        Args:
            timeout_s: Maximum seconds to wait for lock acquisition.

        Returns:
            True if lock acquired, False if timeout exceeded.
        """
        lock_path = self._path + ".lock"
        deadline = time.monotonic() + timeout_s
        while time.monotonic() < deadline:
            try:
                fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(fd, str(os.getpid()).encode())
                os.close(fd)
                return True
            except FileExistsError:
                time.sleep(0.1)
        return False  # Timed out — do NOT force-acquire

    def _release_lock(self) -> None:
        """Release the lock file by deleting it from the filesystem."""
        import contextlib
        lock_path = self._path + ".lock"
        with contextlib.suppress(FileNotFoundError):
            os.unlink(lock_path)

    def _atomic_write(self, patterns: list[dict]) -> None:
        """Write patterns to the JSON file using atomic temp file + os.replace pattern.

        Args:
            patterns: The list of pattern dicts to write.
        """
        tmp_path = self._path + ".tmp"
        with open(tmp_path, "w") as f:
            json.dump(patterns, f, indent=2)
        os.replace(tmp_path, self._path)

    def _read_patterns(self) -> list[dict]:
        """Read patterns from the JSON file with automatic corruption recovery handling.

        If the file is corrupted, renames it to .corrupted.{ts} and starts fresh.

        Returns:
            List of pattern dicts, or empty list if file is corrupted or missing.
        """
        try:
            with open(self._path) as f:
                return json.load(f)  # type: ignore[no-any-return]
        except (OSError, json.JSONDecodeError) as e:
            self._trace.emit(
                component="procedural_memory",
                level=TraceLevel.WARN,
                message=f"Corrupted procedural memory file: {e}. Renaming and starting fresh.",
            )
            # Rename to .corrupted.{timestamp}
            import contextlib
            ts = time.time()
            corrupted_path = f"{self._path}.corrupted.{ts}"
            with contextlib.suppress(Exception):
                os.rename(self._path, corrupted_path)
            return []  # type: ignore[no-any-return]

    def store(self, data: dict, metadata: dict | None = None) -> str:
        """Store a pattern and return the generated unique record identifier string.

        Raises ProceduralMemoryLockTimeoutError if lock acquisition fails (>5s).

        Args:
            data: Pattern fields. Must contain: pattern (str), confidence (float).
                Optional: last_used (str timestamp).
            metadata: Optional metadata dict (not used by procedural backend).

        Returns:
            The generated record id (UUID string).

        Raises:
            ProceduralMemoryLockTimeoutError: If lock cannot be acquired within 5 seconds.
        """
        if not self._acquire_lock():
            self._trace.emit(
                component="procedural_memory",
                level=TraceLevel.WARN,
                message="Procedural memory write skipped — lock held by another operation for >5s",
            )
            raise ProceduralMemoryLockTimeoutError("Lock acquisition timed out")

        try:
            patterns = self._read_patterns()
            record_id = str(uuid.uuid4())

            # Create pattern record
            pattern = {
                "id": record_id,
                "pattern": data["pattern"],
                "confidence": data["confidence"],
                "last_used": data.get("last_used", time.time()),
            }
            patterns.append(pattern)

            # Enforce hard cap with eviction
            if len(patterns) > MAX_PATTERNS:
                self.prune_low_confidence(0.3)
                # If still over cap after pruning, evict oldest by last_used
                while len(patterns) > MAX_PATTERNS:
                    patterns.sort(key=lambda p: p.get("last_used", 0))
                    patterns.pop(0)  # Evict oldest

            self._atomic_write(patterns)

            self._trace.emit(
                component="procedural_memory",
                level=TraceLevel.DEBUG,
                message=f"Stored pattern {record_id} (total patterns: {len(patterns)})",
            )
            return record_id
        finally:
            self._release_lock()

    def query(self, query: dict) -> list[dict]:
        """Query procedural memory patterns matching the specified criteria and filters.

        Args:
            query: Query parameters. Supported keys:
                - pattern: Substring match on pattern field (str)
                - min_confidence: Minimum confidence threshold (float)
                - limit: Maximum number of results (int)

        Returns:
            List of matching pattern records, sorted by confidence descending.
        """
        patterns = self._read_patterns()
        results = []

        for pattern in patterns:
            if "pattern" in query and query["pattern"] not in pattern.get("pattern", ""):
                continue
            if "min_confidence" in query and pattern.get("confidence", 0) < query["min_confidence"]:
                continue
            results.append(pattern)

        # Sort by confidence descending
        results.sort(key=lambda p: p.get("confidence", 0), reverse=True)

        if "limit" in query:
            results = results[: query["limit"]]

        self._trace.emit(
            component="procedural_memory",
            level=TraceLevel.DEBUG,
            message=f"Query returned {len(results)} patterns",
        )
        return results

    def delete(self, record_id: str) -> bool:
        """Delete a procedural memory pattern by its unique identifier string.

        Args:
            record_id: The id of the pattern to delete.

        Returns:
            True if the pattern was deleted, False if not found.
        """
        if not self._acquire_lock():
            self._trace.emit(
                component="procedural_memory",
                level=TraceLevel.WARN,
                message="Procedural memory delete skipped — lock held by another operation for >5s",
            )
            return False

        try:
            patterns = self._read_patterns()
            original_len = len(patterns)
            patterns = [p for p in patterns if p.get("id") != record_id]

            if len(patterns) < original_len:
                self._atomic_write(patterns)
                self._trace.emit(
                    component="procedural_memory",
                    level=TraceLevel.DEBUG,
                    message=f"Deleted pattern {record_id}",
                )
                return True
            return False
        finally:
            self._release_lock()

    def prune_low_confidence(self, threshold: float) -> None:
        """Remove patterns with confidence below the specified threshold value limit.

        Args:
            threshold: Confidence threshold (0.0 to 1.0). Patterns below this
                are removed.
        """
        patterns = self._read_patterns()
        original_len = len(patterns)
        patterns = [p for p in patterns if p.get("confidence", 0) >= threshold]

        if len(patterns) < original_len:
            self._atomic_write(patterns)
            self._trace.emit(
                component="procedural_memory",
                level=TraceLevel.DEBUG,
                message=f"Pruned {original_len - len(patterns)} low-confidence patterns",
            )
