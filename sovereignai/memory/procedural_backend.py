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
    pass


class ProceduralMemoryBackend:

    def __init__(self, trace: TraceEmitter, file_path: str | None = None) -> None:
        self._trace = trace
        self._path = file_path
        if self._path:
            self._ensure_file_exists()
        else:
            self._patterns = {"schema_version": 1, "patterns": []}

    def _ensure_file_exists(self) -> None:
        if self._path and not os.path.exists(self._path):
            os.makedirs(os.path.dirname(self._path), exist_ok=True)
            self._atomic_write([])

    def _acquire_lock(self, timeout_s: float = 5.0) -> bool:
        if not self._path:
            return True  # In-memory mode, no lock needed
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
        if not self._path:
            return  # In-memory mode, no lock to release
        import contextlib
        lock_path = self._path + ".lock"
        with contextlib.suppress(FileNotFoundError):
            os.unlink(lock_path)

    def _atomic_write(self, patterns: list[dict]) -> None:
        if not self._path:
            self._patterns = {"schema_version": 1, "patterns": patterns}
            return
        tmp_path = self._path + ".tmp"
        with open(tmp_path, "w") as f:
            json.dump(patterns, f, indent=2)
        os.replace(tmp_path, self._path)

    def _read_patterns(self) -> list[dict]:
        if not self._path:
            result = self._patterns.get("patterns", [])
            assert isinstance(result, list)
            return result
        try:
            with open(self._path) as f:
                result = json.load(f)
                assert isinstance(result, list)
                return result
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
            return []

    def store(self, data: dict, metadata: dict | None = None) -> str:
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
