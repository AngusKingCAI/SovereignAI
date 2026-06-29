"""In-memory index of registered components and their capabilities.

Per AR9: components are discovered by capability, not by hard-coded
name. The graph is the single source of truth for what the system
can do at any given moment (per AR15).

Per A5: ships ICapabilityIndex as a locked named protocol. Plan 4
imports only this protocol — never the concrete CapabilityGraph
class. This enforces AR7 (UIs are separate processes consuming the
Capability API; they never reach into core internals).
"""
from __future__ import annotations

from threading import Lock
from typing import Any, Protocol, runtime_checkable

from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import (
    CapabilityCategory,
    CapabilityDeclaration,
    ComponentId,
    ComponentManifest,
    TraceLevel,
)


class ComponentRegistrationError(Exception):
    """Raised when a component fails conformance tests and cannot be registered."""
    pass


@runtime_checkable
class ICapabilityIndex(Protocol):
    """Locked query interface for the capability graph.

    Plan 4's Capability API imports ONLY this protocol — never the
    concrete CapabilityGraph class. This enforces AR7 (UIs are
    separate processes consuming the Capability API; they never
    reach into core internals).

    Any component that needs to query capabilities should depend on
    this protocol, not on CapabilityGraph directly. The DI container
    (Plan 1) registers the concrete graph against this protocol.
    """

    def find_providers(self, category: CapabilityCategory,
                       name: str) -> tuple[tuple[ComponentId, CapabilityDeclaration], ...]:
        """Return all components that provide a given capability, sorted by priority.

        Args:
            category: The capability category to search.
            name: The specific capability name (e.g. "text_generation").

        Returns:
            Tuple of (component_id, declaration) pairs, highest priority
            first. Empty tuple if no providers registered.
        """
        ...

    def list_all_components(self) -> tuple[ComponentManifest, ...]:
        """Return manifests for every registered component in the capability graph.

        Returns:
            Tuple of ComponentManifest instances. Empty if nothing
            registered.
        """
        ...


class CapabilityGraph:
    """In-memory index mapping capabilities to the components that provide them.

    The graph is populated at startup by the Composition Root: each
    adapter/skill/backend's manifest is parsed and registered. The
    graph implements ICapabilityIndex so callers can depend on the
    protocol, not the concrete class.
    """

    def __init__(self, trace: TraceEmitter, dev_mode: bool = False) -> None:
        """Create an empty capability graph instance with no registered components yet.

        Args:
            trace: Trace emitter for logging registration events (per P9
                observability — every registration emits a DEBUG trace).
            dev_mode: If True, skip conformance gate (development only).
        """
        self._trace = trace
        self._dev_mode = dev_mode
        # Map (category, name) -> list of (component_id, declaration)
        self._index: dict[tuple[CapabilityCategory, str],
                          list[tuple[ComponentId, CapabilityDeclaration]]] = {}
        # Map component_id -> manifest (for list_all_components)
        self._manifests: dict[ComponentId, ComponentManifest] = {}
        self._lock = Lock()
        self._conformance_runner: Any = None

    def register(self, manifest: ComponentManifest, instance: Any = None) -> None:
        """Add a component's manifest to the graph so its capabilities become discoverable.

        Args:
            manifest: Frozen ComponentManifest parsed from the
                component's manifest.toml file.
            instance: Optional component instance for conformance testing.

        Raises:
            ComponentRegistrationError: If conformance tests fail.
        """
        # N18: --dev flag required (not just env var)
        # F8: dev_mode is a constructor arg (self._dev_mode), NOT os.environ
        if self._dev_mode:
            self._trace.emit(
                component="capability_graph",
                level=TraceLevel.WARN,  # F8: WARN, not ERROR (ERROR confuses monitoring)
                message=(
                    f"DEV MODE active: skipping conformance gate for "
                    f"{manifest.component_id}. DO NOT use in production."
                ),
            )
        else:
            # N1: import from sovereignai.conformance, NOT tests.conformance
            from sovereignai.conformance.runner import ConformanceRunner
            # Rev8: reuse a single ConformanceRunner instance (not fresh per call) to preserve LRU cache
            if self._conformance_runner is None:
                self._conformance_runner = ConformanceRunner(self._trace)
            runner = self._conformance_runner
            capability_class = (
                manifest.provides[0].category.value if manifest.provides else "unknown"
            )  # Per Rev5 F3: derive from first provides category
            is_first_party = (
                str(manifest.component_id).startswith("sovereignai.")
                or "adapters/internal" in str(getattr(manifest, "_source_path", ""))
                or "skills/official" in str(getattr(manifest, "_source_path", ""))
            )  # Rev7: use manifest._source_path (not undefined manifest_path)
            passed = runner.check(
                component_id=str(manifest.component_id),
                content_hash=manifest.content_hash,
                capability_class=capability_class,
                is_first_party=is_first_party,
                instance=instance,
            )
            if not passed:
                raise ComponentRegistrationError(
                    f"Component {manifest.component_id} failed conformance tests"
                )
        with self._lock:
            # Remove old capabilities if this component was previously registered
            old_manifest = self._manifests.get(manifest.component_id)
            if old_manifest is not None:
                for cap in old_manifest.provides:
                    key = (cap.category, cap.name)
                    if key in self._index:
                        self._index[key] = [
                            entry for entry in self._index[key]
                            if entry[0] != manifest.component_id
                        ]
                        if not self._index[key]:
                            del self._index[key]
                self._trace.emit(
                    component="CapabilityGraph",
                    level=TraceLevel.WARN,
                    message=f"Re-registering {manifest.component_id} - old capabilities removed",
                )
            self._manifests[manifest.component_id] = manifest
            for cap in manifest.provides:
                key = (cap.category, cap.name)
                self._index.setdefault(key, []).append(
                    (manifest.component_id, cap)
                )
        self._trace.emit(
            component="CapabilityGraph",
            level=TraceLevel.DEBUG,
            message=(
                f"Registered {manifest.component_id} v{manifest.version} "
                f"with {len(manifest.provides)} provided capabilities"
            ),
        )

    def find_providers(self, category: CapabilityCategory,
                       name: str) -> tuple[tuple[ComponentId, CapabilityDeclaration], ...]:
        """Return all components that provide a given capability, sorted by priority.

        Args:
            category: The capability category to search.
            name: The specific capability name.

        Returns:
            Tuple of (component_id, declaration) pairs, highest priority
            first. Empty tuple if no providers registered.
        """
        with self._lock:
            key = (category, name)
            providers = list(self._index.get(key, []))
        providers.sort(key=lambda x: -x[1].priority)
        return tuple(providers)

    def list_all_components(self) -> tuple[ComponentManifest, ...]:
        """Return manifests for every registered component in the capability graph.

        Returns:
            Tuple of ComponentManifest instances. Empty if nothing
            registered.
        """
        with self._lock:
            return tuple(self._manifests.values())

    def remove(self, component_id: ComponentId) -> None:
        """Remove a component from the capability graph and delete its capability entries.

        Used by the version negotiator to disable incompatible plugins.
        Removes all capability entries for the component and deletes its manifest.

        Args:
            component_id: The component ID to remove.
        """
        with self._lock:
            # Remove from manifests
            manifest = self._manifests.pop(component_id, None)
            if manifest is None:
                return

            # Remove all capability entries for this component
            for cap in manifest.provides:
                key = (cap.category, cap.name)
                if key in self._index:
                    self._index[key] = [
                        entry for entry in self._index[key]
                        if entry[0] != component_id
                    ]
                    if not self._index[key]:
                        del self._index[key]
