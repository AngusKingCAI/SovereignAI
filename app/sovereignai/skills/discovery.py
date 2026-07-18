from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sovereignai.shared.capability_graph import CapabilityGraph
    from sovereignai.shared.trace_emitter import TraceEmitter

from sovereignai.shared.types import CapabilityCategory, TraceLevel
from sovereignai.skills.manifest import SkillManifest


class SkillDiscovery:
    def __init__(self, trace: TraceEmitter, capability_graph: CapabilityGraph) -> None:
        self._trace = trace
        self._capability_graph = capability_graph
        self._skill_index: dict[str, tuple[CapabilityCategory, str]] = {}
        self._trace.emit(
            component="SkillDiscovery",
            level=TraceLevel.INFO,
            message="SkillDiscovery initialized",
        )

    def scan(self, paths: list[Path]) -> None:
        modules_before = set(sys.modules.keys())

        for path in paths:
            if not path.exists():
                self._trace.emit(
                    component="SkillDiscovery",
                    level="debug",
                    message=f"Skill scan path does not exist: {path}",
                )
                continue

            for manifest_path in path.rglob("manifest.toml"):
                self._load_manifest(manifest_path)

        self._validate_dag_dependencies()

        modules_after = set(sys.modules.keys())
        new_modules = modules_after - modules_before
        allowlist = set(sys.stdlib_module_names) if hasattr(sys, "stdlib_module_names") else set()
        allowlist.add("defusedxml")

        unexpected_modules = new_modules - allowlist
        if unexpected_modules:
            self._trace.emit(
                component="SkillDiscovery",
                level="warn",
                message=f"Unexpected modules loaded during scan: {unexpected_modules}",
            )

    def _load_manifest(self, manifest_path: Path) -> None:
        try:
            skill_manifest = SkillManifest.from_toml(manifest_path)
            component_manifest = skill_manifest.to_component_manifest()

            # Add source path to metadata for path resolution
            updated_metadata = dict(component_manifest.metadata)
            updated_metadata["_source_path"] = str(manifest_path.parent)
            component_manifest = replace(component_manifest, metadata=updated_metadata)

            self._capability_graph.register(manifest=component_manifest, instance=None)

            self._skill_index[skill_manifest.id] = (CapabilityCategory.SKILL, skill_manifest.id)

            self._trace.emit(
                component="SkillDiscovery",
                level="info",
                message=f"Discovered skill: {skill_manifest.id} v{skill_manifest.version}",
            )
        except Exception as e:
            self._trace.emit(
                component="SkillDiscovery",
                level="error",
                message=f"Failed to load manifest {manifest_path}: {e}",
            )

    def _validate_dag_dependencies(self) -> None:
        all_skill_ids = set(self._skill_index.keys())
        dangling_deps: dict[str, list[str]] = {}

        for skill_id, (_category, _name) in self._skill_index.items():
            manifest = self._capability_graph.list_all_components()
            skill_manifest = None
            for m in manifest:
                if str(m.component_id) == skill_id:
                    skill_manifest = m
                    break

            if skill_manifest and "dependencies" in skill_manifest.metadata:
                deps = skill_manifest.metadata["dependencies"]
                for dep in deps:
                    if dep not in all_skill_ids:
                        if skill_id not in dangling_deps:
                            dangling_deps[skill_id] = []
                        dangling_deps[skill_id].append(dep)

        if dangling_deps:
            for skill_id, deps in dangling_deps.items():
                self._trace.emit(
                    component="SkillDiscovery",
                    level="warn",
                    message=f"Skill {skill_id} has dangling DAG dependencies: {deps}",
                )

    def get_skill_index(self) -> dict[str, tuple[CapabilityCategory, str]]:
        return self._skill_index.copy()
