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

    def __init__(self, capability_index: ICapabilityIndex,
                 lifecycle_manager: LifecycleManager) -> None:
        self._index = capability_index
        self._lifecycle = lifecycle_manager

    def route(self, category: CapabilityCategory, name: str) -> ComponentId:
        providers = self._index.find_providers(category, name)
        for component_id, _declaration in providers:
            status = self._lifecycle.try_recover(component_id)
            if status.is_available():
                return component_id
        raise NoActiveProviderError(
            f"No active provider for {category}/{name} "
            f"(checked {len(providers)} registered providers)"
        )
