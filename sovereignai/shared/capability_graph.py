from __future__ import annotations

from threading import Lock
from typing import Any, Protocol, runtime_checkable

from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import (
    CapabilityCategory,
    CapabilityDeclaration,
    ComponentId,
    ComponentManifest,
    ComponentMetadata,
    TraceLevel,
)


class ComponentRegistrationError(Exception):
    pass


@runtime_checkable
class ICapabilityIndex(Protocol):

    def find_providers(self, category: CapabilityCategory,
                       name: str) -> tuple[tuple[ComponentId, CapabilityDeclaration], ...]:
        ...

    def list_all_components(self) -> tuple[ComponentManifest, ...]:
        ...

    def adapters_by_capability(self, capability: str) -> list:
        ...

    def get_adapter(self, component_id: str) -> Any:
        ...


class CapabilityGraph:

    def __init__(self, trace: TraceEmitter, dev_mode: bool = False) -> None:
        self._trace = trace
        self._dev_mode = dev_mode
        # Map (category, name) -> list of (component_id, declaration)
        self._index: dict[tuple[CapabilityCategory, str],
                          list[tuple[ComponentId, CapabilityDeclaration]]] = {}
        # Map component_id -> manifest (for list_all_components)
        self._manifests: dict[ComponentId, ComponentManifest] = {}
        # Map component_id -> instance (for O(1) lookup in routing)
        self._instances: dict[ComponentId, Any] = {}
        self._lock = Lock()
        self._conformance_runner: Any = None

    def register(self, manifest: ComponentManifest, instance: Any = None) -> None:
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
            # Rev8: reuse a single ConformanceRunner instance (not fresh per call)
            # to preserve LRU cache
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
            if instance is not None:
                self._instances[manifest.component_id] = instance
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
        with self._lock:
            key = (category, name)
            providers = list(self._index.get(key, []))
        providers.sort(key=lambda x: -x[1].priority)
        return tuple(providers)

    def list_all_components(self) -> tuple[ComponentManifest, ...]:
        with self._lock:
            return tuple(self._manifests.values())

    def remove(self, component_id: ComponentId) -> None:
        with self._lock:
            # Remove from manifests
            manifest = self._manifests.pop(component_id, None)
            if manifest is None:
                return

            # Remove from instances
            self._instances.pop(component_id, None)

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

    def adapters_by_capability(self, capability: str) -> list[ComponentMetadata]:
        from sovereignai.shared.types import ComponentMetadata

        with self._lock:
            result: list[ComponentMetadata] = []
            for manifest in self._manifests.values():
                for cap in manifest.provides:
                    if cap.category.value == capability:
                        result.append(
                            ComponentMetadata(
                                component_id=str(manifest.component_id),
                                version=manifest.version,
                                capabilities=manifest.provides,
                                routing_priority=manifest.routing_priority,
                            )
                        )
                        break
            result.sort(key=lambda x: x.routing_priority)
            return result

    def get_adapter(self, component_id: str) -> Any:
        with self._lock:
            return self._instances.get(ComponentId(component_id))
