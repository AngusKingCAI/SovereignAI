from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import tomli

from app.sovereignai.shared.types import (
    CapabilityCategory,
    CapabilityDeclaration,
    ComponentId,
    ComponentManifest,
)


@dataclass
class SkillManifest:
    id: str
    name: str
    version: str
    capabilities: list[CapabilityDeclaration]
    runner: str
    timeout: int
    dependencies: list[str]
    memory_integration_hints: list[str]
    dag_dependencies: list[str]

    @classmethod
    def from_toml(cls, path: Path) -> SkillManifest:
        if not path.exists():
            raise FileNotFoundError(f"Manifest file not found: {path}")

        with path.open("rb") as f:
            data = tomli.load(f)

        skill_id = data.get("id")
        if not skill_id:
            raise ValueError(f"Manifest {path} missing 'id' field")

        name = data.get("name", skill_id)
        version = data.get("version", "0.1.0")

        raw_capabilities = data.get("capabilities", [])
        capabilities = []
        for cap in raw_capabilities:
            category_str = cap.get("category", "tool")
            try:
                category = CapabilityCategory(category_str)
            except ValueError:
                category = CapabilityCategory.TOOL

            capabilities.append(
                CapabilityDeclaration(
                    category=category,
                    name=cap.get("name", skill_id),
                    version=cap.get("version", "1.0.0"),
                    priority=cap.get("priority", 0),
                )
            )

        execution_config = data.get("execution", {})
        runner = execution_config.get("runner", "default")
        timeout = execution_config.get("timeout", 30)

        dependencies = data.get("dependencies", [])
        memory_integration_hints = data.get("memory_integration_hints", [])

        dag_section = data.get("dag", {})
        dag_dependencies = dag_section.get("dag_dependencies", [])

        return cls(
            id=skill_id,
            name=name,
            version=version,
            capabilities=capabilities,
            runner=runner,
            timeout=timeout,
            dependencies=dependencies,
            memory_integration_hints=memory_integration_hints,
            dag_dependencies=dag_dependencies,
        )

    def to_component_manifest(self) -> ComponentManifest:
        metadata: dict[str, Any] = {
            "dependencies": self.dependencies,
            "memory_hints": self.memory_integration_hints,
        }

        return ComponentManifest(
            component_id=ComponentId(self.id),
            version=self.version,
            provides=tuple(self.capabilities),
            requires=(),
            author="skill",
            content_hash="",
            metadata=metadata,
        )
