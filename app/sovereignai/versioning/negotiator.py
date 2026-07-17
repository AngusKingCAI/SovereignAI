from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from app.sovereignai.shared.types import ComponentId, ComponentManifest
from app.sovereignai.versioning.compatibility_matrix import CompatibilityMatrix
from app.sovereignai.versioning.semver import SemVer

if TYPE_CHECKING:
    from sovereignai.shared.capability_graph import ICapabilityIndex
    from sovereignai.shared.trace_emitter import TraceEmitter


class FatalIncompatibilityError(Exception):

    def __init__(self, incompatibilities: list[Incompatibility]) -> None:
        self.incompatibilities = incompatibilities
        messages = [str(inc) for inc in incompatibilities]
        super().__init__("Fatal incompatibilities detected:\n" + "\n".join(messages))


@dataclass(frozen=True)
class Incompatibility:

    component_a: ComponentId
    version_a: str
    component_b: ComponentId
    version_b: str
    reason: str
    compatible: bool = False  # True if compatible, False if incompatible


@dataclass(frozen=True)
class NegotiationResult:

    can_start: bool
    fatal_incompatibilities: list[Incompatibility]
    disabled_plugins: list[ComponentId]
    disabled_plugins_with_classes: list[tuple[ComponentId, type]]
    warnings: list[str]


class VersionNegotiator:

    def __init__(
        self,
        capability_graph: ICapabilityIndex,
        trace: TraceEmitter,
    ) -> None:
        self._graph = capability_graph
        self._trace = trace
        self._matrix = CompatibilityMatrix(trace=trace)

    def negotiate(self) -> NegotiationResult:
        fatal_incompatibilities: list[Incompatibility] = []
        disabled_plugins: list[ComponentId] = []
        disabled_plugins_with_classes: list[tuple[ComponentId, type]] = []
        warnings: list[str] = []

        components = self._all_components()

        for component in components:
            for other in components:
                if component.component_id >= other.component_id:
                    continue  # Avoid duplicate pairs and self-comparison

                result = self._check_pair(component, other)

                # Rev9: record BOTH compatible and incompatible results
                self._matrix.record(
                    component_a=component.component_id,
                    version_a=component.version,
                    content_hash_a=component.content_hash,
                    component_b=other.component_id,
                    version_b=other.version,
                    content_hash_b=other.content_hash,
                    status="compatible" if result.compatible else "incompatible",
                )

                if not result.compatible:
                    # Check if either component is core
                    is_core_a = self._is_core(component)
                    is_core_b = self._is_core(other)

                    if is_core_a or is_core_b:
                        fatal_incompatibilities.append(result)
                    else:
                        # Disable the plugin with the lower component_id (deterministic)
                        disabled_id = (
                            component.component_id
                            if component.component_id < other.component_id
                            else other.component_id
                        )
                        disabled_plugins.append(disabled_id)
                        # Note: we don't have the actual class here; composition root
                        # will need to look it up from the container by component_id
                        other_id = (
                            other.component_id
                            if disabled_id == component.component_id
                            else component.component_id
                        )
                        warnings.append(
                            f"Plugin {disabled_id} disabled due to version "
                            f"incompatibility with {other_id}"
                        )

        # Rev9: batch-write all buffered entries at once
        self._matrix.flush()

        return NegotiationResult(
            can_start=not fatal_incompatibilities,
            fatal_incompatibilities=fatal_incompatibilities,
            disabled_plugins=disabled_plugins,
            disabled_plugins_with_classes=disabled_plugins_with_classes,
            warnings=warnings,
        )

    def _all_components(self) -> list[ComponentManifest]:
        return list(self._graph.list_all_components())

    def _check_pair(
        self, component: ComponentManifest, other: ComponentManifest
    ) -> Incompatibility:
        is_core_a = self._is_core(component)
        is_core_b = self._is_core(other)

        if is_core_a or is_core_b:
            # At least one is core - use strict checking
            return self._check_core_compatibility(component, other)
        else:
            # Both are plugins - use lenient checking
            return self._check_plugin_compatibility(component, other)

    def _is_core(self, manifest: ComponentManifest) -> bool:
        # Check if manifest has core field (will be added in S4)
        is_core_declared = getattr(manifest, "core", False)

        if not is_core_declared:
            return False

        # Check if component is inside sovereignai package directory
        # This requires checking the _source_path attribute (added in S4)
        source_path = getattr(manifest, "_source_path", "")
        if not source_path:
            return False

        from pathlib import Path

        import sovereignai

        sovereignai_pkg_dir = Path(sovereignai.__file__).resolve().parent
        manifest_dir = Path(source_path).resolve().parent

        return manifest_dir.is_relative_to(sovereignai_pkg_dir)

    def _check_core_compatibility(
        self, component: ComponentManifest, other: ComponentManifest
    ) -> Incompatibility:
        # Check for missing version fields
        if not component.version:
            return Incompatibility(
                component_a=component.component_id,
                version_a="",
                component_b=other.component_id,
                version_b=other.version,
                reason="core component missing version field",
                compatible=False,
            )
        if not other.version:
            return Incompatibility(
                component_a=component.component_id,
                version_a=component.version,
                component_b=other.component_id,
                version_b="",
                reason="core component missing version field",
                compatible=False,
            )

        # Parse versions
        try:
            ver_a = SemVer.parse(component.version)
            ver_b = SemVer.parse(other.version)
        except ValueError as e:
            return Incompatibility(
                component_a=component.component_id,
                version_a=component.version,
                component_b=other.component_id,
                version_b=other.version,
                reason=f"invalid version format: {e}",
                compatible=False,
            )

        # Check compatibility (same major, minor/patch >= required)
        if not ver_a.is_compatible_with(ver_b) and not ver_b.is_compatible_with(
            ver_a
        ):
            return Incompatibility(
                component_a=component.component_id,
                version_a=component.version,
                component_b=other.component_id,
                version_b=other.version,
                reason="major version mismatch or downgrade",
                compatible=False,
            )

        # Compatible
        return Incompatibility(
            component_a=component.component_id,
            version_a=component.version,
            component_b=other.component_id,
            version_b=other.version,
            reason="",
            compatible=True,
        )

    def _check_plugin_compatibility(
        self, component: ComponentManifest, other: ComponentManifest
    ) -> Incompatibility:
        # Default missing versions to 0.0.0
        version_a = component.version or "0.0.0"
        version_b = other.version or "0.0.0"

        # Parse versions
        try:
            SemVer.parse(version_a)
            SemVer.parse(version_b)
        except ValueError as e:
            # For plugins, invalid version is treated as incompatible (disable)
            return Incompatibility(
                component_a=component.component_id,
                version_a=version_a,
                component_b=other.component_id,
                version_b=version_b,
                reason=f"invalid version format: {e}",
                compatible=False,
            )

        # For plugins, we use a more lenient check: just ensure they can parse
        # No strict compatibility requirement - plugins are disabled on conflict
        # rather than blocking startup
        return Incompatibility(
            component_a=component.component_id,
            version_a=version_a,
            component_b=other.component_id,
            version_b=version_b,
            reason="",
            compatible=True,
        )
