"""Route capability requests to the highest-priority active provider.

Per A1: the routing engine queries the Lifecycle Manager to skip
components that are degraded or circuit-broken. A router built before
the Lifecycle Manager would be a static dispatcher requiring a rewrite
when status tracking lands.

Per Q4: routing is capability-based. The caller declares what
capability it needs; the router finds the highest-priority active
provider from the capability graph.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from sovereignai.shared.capability_graph import ICapabilityIndex
from sovereignai.shared.types import (
    CapabilityCategory,
    ComponentId,
    NoActiveProviderError,
)

if TYPE_CHECKING:
    from sovereignai.shared.lifecycle_manager import LifecycleManager


class RoutingEngine:
    """Find the best active component to handle a capability request.

    The router depends on ICapabilityIndex (Plan 2) for discovery and
    on the Lifecycle Manager (S3 of this plan) for status. It never
    routes to a CIRCUIT_BROKEN or STOPPED component.
    """

    def __init__(self, capability_index: ICapabilityIndex,
                 lifecycle_manager: LifecycleManager) -> None:
        """Create a router that queries the capability graph and lifecycle manager.

        Args:
            capability_index: Protocol implementation providing
                find_providers() (Plan 2's CapabilityGraph).
            lifecycle_manager: Tracks component status; the router
                skips components that are not ACTIVE.
        """
        self._index = capability_index
        self._lifecycle = lifecycle_manager

    def route(self, category: CapabilityCategory, name: str) -> ComponentId:
        """Return the component ID of the highest-priority active provider available.

        Per Rev4 Finding 1: calls `try_recover(component_id)` before
        checking status. If the error window has expired, the component
        is recovered to ACTIVE and routing proceeds. This makes the
        routing path self-healing for components in active use.

        Args:
            category: The capability category needed.
            name: The specific capability name needed.

        Returns:
            ComponentId of the chosen provider.

        Raises:
            NoActiveProviderError: If no ACTIVE component provides the
                requested capability (after attempting recovery).
        """
        providers = self._index.find_providers(category, name)
        for component_id, _declaration in providers:
            status = self._lifecycle.try_recover(component_id)
            if status.is_available():
                return component_id
        raise NoActiveProviderError(
            f"No active provider for {category}/{name} "
            f"(checked {len(providers)} registered providers)"
        )
