from __future__ import annotations

import importlib
import importlib.util
import sys
import time
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sovereignai.shared.capability_graph import CapabilityGraph
    from sovereignai.shared.trace_emitter import TraceEmitter
    from sovereignai.skills.session import SkillSession

from app.sovereignai.shared.types import CapabilityCategory, TraceLevel
from app.sovereignai.skills.runner import ISkillRunner, SkillResult


class SkillNotFoundError(Exception):
    pass


class ConcreteSkillRunner(ISkillRunner):
    def __init__(self, capability_graph: CapabilityGraph, trace: TraceEmitter) -> None:
        self._capability_graph = capability_graph
        self._trace = trace
        self._module_cache: dict[str, object] = {}
        self._trace.emit(
            component="ConcreteSkillRunner",
            level=TraceLevel.INFO,
            message="ConcreteSkillRunner initialized",
        )

    def run(self, skill_id: str, args: dict[str, object], session: SkillSession) -> SkillResult:
        providers = self._capability_graph.find_providers(CapabilityCategory.SKILL, skill_id)
        if not providers:
            raise SkillNotFoundError(f"Skill not found: {skill_id}")

        component_id, _ = providers[0]

        module = self._load_module(component_id)
        if module is None:
            return SkillResult(
                output="",
                error=f"Failed to load skill module: {skill_id}",
                execution_time_ms=0,
            )

        start_time = time.time()
        try:
            if hasattr(module, "execute"):
                output = module.execute(args)
                execution_time_ms = int((time.time() - start_time) * 1000)
                return SkillResult(
                    output=output,
                    error=None,
                    execution_time_ms=execution_time_ms,
                )
            else:
                return SkillResult(
                    output="",
                    error=f"Skill module missing execute function: {skill_id}",
                    execution_time_ms=int((time.time() - start_time) * 1000),
                )
        except Exception as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            return SkillResult(
                output="",
                error=f"Skill execution failed: {e}",
                execution_time_ms=execution_time_ms,
            )

    def _load_module(self, component_id: str) -> object | None:
        if component_id in self._module_cache:
            return self._module_cache[component_id]

        try:
            component_id_str = str(component_id)

            # Get source path from manifest metadata
            manifests = self._capability_graph.list_all_components()
            source_path = None
            for manifest in manifests:
                if str(manifest.component_id) == component_id_str:
                    source_path = manifest.metadata.get("_source_path")
                    break

            if not source_path:
                self._trace.emit(
                    component="ConcreteSkillRunner",
                    level=TraceLevel.ERROR,
                    message=f"No source path found for skill: {component_id}",
                )
                return None

            skill_module_path = Path(source_path) / "skill.py"

            if not skill_module_path.exists():
                self._trace.emit(
                    component="ConcreteSkillRunner",
                    level=TraceLevel.ERROR,
                    message=f"Skill module not found: {skill_module_path}",
                )
                return None

            spec = importlib.util.spec_from_file_location(component_id_str, skill_module_path)
            if spec is None or spec.loader is None:
                self._trace.emit(
                    component="ConcreteSkillRunner",
                    level=TraceLevel.ERROR,
                    message=f"Failed to load spec for: {skill_module_path}",
                )
                return None

            module = importlib.util.module_from_spec(spec)
            sys.modules[component_id_str] = module
            spec.loader.exec_module(module)

            self._module_cache[component_id] = module
            return module
        except Exception as e:
            self._trace.emit(
                component="ConcreteSkillRunner",
                level=TraceLevel.ERROR,
                message=f"Failed to load skill module {component_id}: {e}",
            )
            return None

    def health_check(self) -> bool:
        return True

    def list_capabilities(self) -> list[str]:
        return list(self._module_cache.keys())

    def close(self) -> None:
        if not self._module_cache:
            return

        for component_id in list(self._module_cache.keys()):
            module = self._module_cache.pop(component_id, None)
            if module and component_id in sys.modules:
                del sys.modules[component_id]

        self._trace.emit(
            component="ConcreteSkillRunner",
            level=TraceLevel.INFO,
            message=f"Cleared module cache for {len(self._module_cache)} skills",
        )
