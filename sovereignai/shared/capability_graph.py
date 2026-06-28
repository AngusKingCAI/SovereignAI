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
from typing import Protocol, runtime_checkable

from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import (
    CapabilityCategory,
    CapabilityDeclaration,
    ComponentId,
    ComponentManifest,
    TraceLevel,
)


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

    def __init__(self, trace: TraceEmitter) -> None:
        """Create an empty capability graph instance with no registered components yet.

        Args:
            trace: Trace emitter for logging registration events (per P9
                observability — every registration emits a DEBUG trace).
        """
        self._trace = trace
        # Map (category, name) -> list of (component_id, declaration)
        self._index: dict[tuple[CapabilityCategory, str],
                          list[tuple[ComponentId, CapabilityDeclaration]]] = {}
        # Map component_id -> manifest (for list_all_components)
        self._manifests: dict[ComponentId, ComponentManifest] = {}
        self._lock = Lock()

    def register(self, manifest: ComponentManifest) -> None:
        """Add a component's manifest to the graph so its capabilities become discoverable.

        Args:
            manifest: Frozen ComponentManifest parsed from the
                component's manifest.toml file.
        """
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
