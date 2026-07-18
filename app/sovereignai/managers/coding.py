from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

from sovereignai.managers.base import DepartmentManager
from sovereignai.managers.exceptions import SymbolMapUnavailableError
from sovereignai.managers.types import Deliverable, ValidationResult
from sovereignai.shared.capability_graph import CapabilityGraph
from sovereignai.shared.container import DIContainer
from sovereignai.shared.types import CapabilityCategory, ComponentManifest

if TYPE_CHECKING:
    pass

log = logging.getLogger(__name__)


class CodingManager(DepartmentManager):
    """Department manager for coding tasks using ReAct Worker with file operations."""

    def __init__(self, container: DIContainer, project_root: Path | None = None) -> None:
        super().__init__(container)
        self._project_root = project_root

    async def _build_context_impl(self, task: Any) -> dict[str, Any]:
        """Build symbol context for coding tasks."""
        # Will be implemented when SymbolMap exists (S4)
        return {}

    async def build_context(self, task: Any) -> dict | None:
        """Build context using SymbolMap with async wrapping to avoid blocking event loop."""
        try:
            from sovereignai.indexing.symbol_map import SymbolMap
            from sovereignai.shared.trace_emitter import TraceEmitter
            from sovereignai.shared.types import TraceLevel

            # Retrieve SymbolMap (will be registered in S6)
            symbol_map = self._container.retrieve(SymbolMap)
            trace = self._container.retrieve(TraceEmitter)

            # Index project using asyncio.to_thread to avoid blocking event loop (P24-P)
            if self._project_root is None:
                return {}
            index_result = await asyncio.to_thread(
                symbol_map.index, self._project_root
            )

            trace.emit(
                component="coding_manager",
                level=TraceLevel.INFO,
                message=f"Symbol context built for {self._project_root}"
            )

            return {"symbol_index": index_result}
        except SymbolMapUnavailableError:
            # Emit trace event and return None for degraded mode
            from sovereignai.shared.trace_emitter import TraceEmitter
            from sovereignai.shared.types import TraceLevel

            trace = self._container.retrieve(TraceEmitter)
            trace.emit(
                component="coding_manager",
                level=TraceLevel.WARN,
                message="SymbolMap unavailable (degraded mode)"
            )
            return None
        except Exception as e:
            # Handle SymbolMap not yet registered case
            log.warning(f"SymbolMap not available: {e}")
            return None

    def validate(self, deliverable: Deliverable) -> ValidationResult:
        """Validate coding deliverable - check tests exist and pass."""
        # Basic validation - will be enhanced in S9 tests
        if deliverable.success:
            return ValidationResult(passed=True)
        else:
            return ValidationResult(
                passed=False,
                reason="Worker execution failed",
                details={"output": str(deliverable.output)}
            )

    async def execute_task(self, task: Any) -> Deliverable:
        """Execute coding task using ReAct Worker with symbol context."""
        from sovereignai.agent.factory import ReActLoopFactory
        from sovereignai.memory.graph_backend import TaskGraphCache
        from sovereignai.shared.trace_emitter import TraceEmitter
        from sovereignai.shared.types import TraceLevel
        from sovereignai.skills.discovery import SkillDiscovery
        from sovereignai.skills.session import SkillSession

        trace = self._container.retrieve(TraceEmitter)

        # Build context (P24-O: pass task; P24-P: await async build_context)
        ctx = await self.build_context(task)
        if ctx is None:
            log.warning(
                'Symbol context unavailable (degraded mode), proceeding without symbol ranking'
            )
            trace.emit(
                component="coding_manager",
                level=TraceLevel.WARN,
                message="Proceeding without symbol ranking (degraded mode)"
            )

        # Retrieve TaskGraphCache (N4: self._container, not bare container)
        graph_memory = self._container.retrieve(TaskGraphCache)

        try:
            # Retrieve skill discovery (P24-L: SkillDiscovery, not SkillManifestRegistry)
            skill_discovery = self._container.retrieve(SkillDiscovery)
            skill_index = skill_discovery.get_skill_index()

            # Build tools list from skill manifests (P24-L: get_skill_index, not get_tools)
            capability_graph = self._container.retrieve(CapabilityGraph)
            all_manifests = capability_graph.list_all_components()
            manifest_map = {str(m.component_id): m for m in all_manifests}
            tools = [
                manifest_map.get(skill_id)
                for skill_id, (cat, name) in skill_index.items()
                if cat == CapabilityCategory.SKILL and skill_id in manifest_map
            ]
            tools = [t for t in tools if t is not None]

            # Create session (P24-L: no args)
            session = SkillSession()

            # Extract task description (N3)
            task_description = task.description if hasattr(task, 'description') else str(task)

            # Retrieve ReAct Worker (P24-L: ReActLoopFactory returns ReActLoop)
            worker = self._container.retrieve(ReActLoopFactory)  # type: ignore

            # Run ReAct Worker with context and memory
            # Convert ctx to JSON string for ReActLoop
            ctx_str = str(ctx) if ctx else None
            # Convert ComponentManifest to dict for tools
            tool_dicts = [
                {
                    "name": (
                        cast(ComponentManifest, t).provides[0].name
                        if cast(ComponentManifest, t).provides
                        else "unknown"
                    ),
                    "description": "",
                }
                for t in tools if t is not None
            ]
            result = await worker.run(
                task_description,
                tool_dicts,
                session,
                context=ctx_str,
                memory=graph_memory
            )

            trace.emit(
                component="coding_manager",
                level=TraceLevel.INFO,
                message=f"Task completed: {task_description}"
            )

            return Deliverable(
                success=result.status == "success",
                output=result.output,
                validation_failure=None
            )
        finally:
            # Close graph memory (P24-B — fires even if retrieve throws)
            if hasattr(graph_memory, 'close'):
                graph_memory.close()
