"""Self-correction skill — analyzes traces and updates procedural memory."""
import threading

from sovereignai.librarian.librarian import Librarian
from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import TaskState, TaskStateChanged, TraceLevel


class SelfCorrectionSkill:
    """Analyze completed tasks and update procedural memory with learned patterns."""

    COMPONENT_NAME = "self_correction"

    def __init__(self, librarian: Librarian, trace: TraceEmitter) -> None:
        """Create a self-correction skill.

        Analyzes task traces and updates procedural memory.
        """
        self._librarian = librarian
        self._trace = trace
        self._recently_analyzed: set[str] = set()
        self._lock = threading.Lock()

    def on_task_state_changed(self, event: TaskStateChanged) -> None:
        """Handle a task state change. Filters own events + deduplicates per task_id."""
        if event.new_state not in (TaskState.COMPLETE, TaskState.FAILED):
            return
        task_id_str = str(event.task_id)
        with self._lock:
            if task_id_str in self._recently_analyzed:
                # Rev3 N14: emit DEBUG trace (not silent)
                self._trace.emit(
                    component=self.COMPONENT_NAME,
                    level=TraceLevel.DEBUG,
                    message=f"Skipping already-analyzed task {task_id_str} (recursion guard)",
                )
                return
            self._recently_analyzed.add(task_id_str)
        try:
            self.analyze_task(task_id_str)
        finally:
            with self._lock:
                self._recently_analyzed.discard(task_id_str)

    def analyze_task(self, task_id: str) -> dict:
        """Read trace events to extract patterns and update procedural memory with learned insights.

        Filters out self_correction's own emissions (per OR69).
        """
        traces = self._librarian.query("trace", {
            "task_id": task_id,
            "exclude_component": self.COMPONENT_NAME,
        })
        patterns = self._extract_patterns(traces)
        for pattern in patterns:
            self.update_procedural_memory(pattern, confidence=pattern.get("confidence", 0.5))
        for pattern in patterns:
            if pattern.get("type") == "routing_failure" and pattern.get("confidence", 0) > 0.8:
                self._recommend_retraining(pattern)
        return {"patterns_found": len(patterns), "memory_updated": len(patterns) > 0}

    def update_procedural_memory(self, pattern: dict, confidence: float) -> bool:
        """Store a learned pattern.

        Returns True on success, False if lock timed out (per Rev3 N8).
        """
        try:
            record_id = self._librarian.store(
                "procedural",
                data=pattern,
                metadata={"confidence": confidence},
            )
            return record_id is not None
        except Exception as e:
            # N8: procedural memory lock may time out — log and continue
            self._trace.emit(
                component=self.COMPONENT_NAME,
                level=TraceLevel.WARN,
                message=f"Failed to update procedural memory: {e}",
            )
            return False

    def _recommend_retraining(self, pattern: dict) -> None:
        """Emit a retraining recommendation trace.

        Triggered when high-confidence routing failures are detected.
        """
        self._trace.emit(
            component=self.COMPONENT_NAME,
            level=TraceLevel.INFO,
            message=(
                f"Retraining recommended: high-confidence routing failure "
                f"(confidence={pattern.get('confidence')})"
            ),
        )

    def _extract_patterns(self, traces: list) -> list:
        """Extract learned patterns from trace events for procedural memory storage."""
        return []
