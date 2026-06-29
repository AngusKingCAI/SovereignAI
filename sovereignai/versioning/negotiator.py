"""Negotiate version compatibility between components at startup.

Per OR57: core components use strict versioning (incompatible versions prevent
startup). Plugins use lenient versioning (incompatible versions are disabled
with a WARN trace).

Per OR67: raises FatalIncompatibilityError for fatal incompatibilities, which
the composition root catches and exits with code 1.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from sovereignai.shared.types import ComponentId, ComponentManifest
from sovereignai.versioning.compatibility_matrix import CompatibilityMatrix
from sovereignai.versioning.semver import SemVer

if TYPE_CHECKING:
    from sovereignai.shared.capability_graph import ICapabilityIndex
    from sovereignai.shared.trace_emitter import TraceEmitter


class FatalIncompatibilityError(Exception):
    """Raised when core components have incompatible versions that prevent startup.

    Per OR67: the composition root catches this, emits an ERROR trace, prints
    the message to stderr, and exits with code 1 after a 30-second countdown
    (or immediately if --no-wait is passed).
    """

    def __init__(self, incompatibilities: list[Incompatibility]) -> None:
        """Create a fatal incompatibility error with a list of incompatibility details.

        Args:
            incompatibilities: List of Incompatibility instances describing
                each incompatible pair.
        """
        self.incompatibilities = incompatibilities
        messages = [str(inc) for inc in incompatibilities]
        super().__init__("Fatal incompatibilities detected:\n" + "\n".join(messages))


@dataclass(frozen=True)
class Incompatibility:
    """Describe a version incompatibility between two components."""

    component_a: ComponentId
    version_a: str
    component_b: ComponentId
    version_b: str
    reason: str
    compatible: bool = False  # True if compatible, False if incompatible


@dataclass(frozen=True)
class NegotiationResult:
    """Result of version negotiation across all registered components."""

    can_start: bool
    fatal_incompatibilities: list[Incompatibility]
    disabled_plugins: list[ComponentId]
    disabled_plugins_with_classes: list[tuple[ComponentId, type]]
    warnings: list[str]


class VersionNegotiator:
    """Negotiate version compatibility between components at startup.

    Per OR57: core components (those with manifest.core=true inside the
    sovereignai package) use strict versioning. Plugins use lenient
    versioning and are disabled on incompatibility.
    """

    def __init__(
        self,
        capability_graph: ICapabilityIndex,
        trace: TraceEmitter,
    ) -> None:
        """Create a version negotiator instance for checking component version compatibility.

        Args:
            capability_graph: The capability graph to query for registered components.
            trace: Trace emitter for logging negotiation events.
        """
        self._graph = capability_graph
        self._trace = trace
        self._matrix = CompatibilityMatrix(trace=trace)

    def negotiate(self) -> NegotiationResult:
        """Check compatibility between all registered component pairs.

        Record results in the matrix.

        For each pair of components:
        - If either is core, use strict checking (fatal on mismatch).
        - If both are plugins, use lenient checking (disable on mismatch).

        Per Rev9: record BOTH compatible and incompatible results to the
        compatibility matrix, then batch-write at the end.

        Returns:
            NegotiationResult with can_start=False if any fatal incompatibilities
            are found (core components that cannot coexist).
        """
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
        """Return all registered components from the capability graph for version checking.

        Returns:
            List of ComponentManifest instances.
        """
        return list(self._graph.list_all_components())

    def _check_pair(
        self, component: ComponentManifest, other: ComponentManifest
    ) -> Incompatibility:
        """Check if two components are compatible based on their version strings and core status.

        Args:
            component: First component to check.
            other: Second component to check.

        Returns:
            Incompatibility instance if incompatible, or a compatible Incompatibility
            with empty reason if compatible.
        """
        is_core_a = self._is_core(component)
        is_core_b = self._is_core(other)

        if is_core_a or is_core_b:
            # At least one is core - use strict checking
            return self._check_core_compatibility(component, other)
        else:
            # Both are plugins - use lenient checking
            return self._check_plugin_compatibility(component, other)

    def _is_core(self, manifest: ComponentManifest) -> bool:
        """Determine if a component is core based on manifest and location.

        Per OR57: a component is core if its manifest declares core=true AND
        it is installed inside the sovereignai/ package directory. The
        core=true field is ignored for components outside sovereignai/.

        Args:
            manifest: The component manifest to check.

        Returns:
            True if the component is core, False if it is a plugin.
        """
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
        """Perform strict compatibility check for core components.

        Requires exact major version match.
        A core component without a version field is an error (fatal).

        Args:
            component: First component to check.
            other: Second component to check.

        Returns:
            Incompatibility with empty reason if compatible, or with reason if incompatible.
        """
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
        """Perform lenient compatibility check for plugins that defaults missing versions to zero.

        A plugin without a version defaults to "0.0.0" and passes.

        Args:
            component: First component to check.
            other: Second component to check.

        Returns:
            Incompatibility with empty reason if compatible, or with reason if incompatible.
        """
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
