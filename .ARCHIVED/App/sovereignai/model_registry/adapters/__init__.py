from sovereignai.model_registry.adapters.ollama import OllamaAdapter
from sovereignai.model_registry.adapters.openai import OpenAIAdapter
from sovereignai.model_registry.sync import ProviderAdapterProtocol

# Adapter registry - normalized provider IDs (lowercase, no spaces)
ADAPTER_REGISTRY: dict[str, ProviderAdapterProtocol] = {
    "openai": OpenAIAdapter(),
    "ollama": OllamaAdapter(),
}


def register_adapter(provider_id: str, adapter: ProviderAdapterProtocol) -> None:
    """Register a new adapter in the registry.

    Args:
        provider_id: Normalized provider ID (lowercase, no spaces)
        adapter: Adapter instance implementing ProviderAdapterProtocol

    Raises:
        ValueError: If provider_id already exists in registry
    """
    if provider_id in ADAPTER_REGISTRY:
        raise ValueError(f"Provider ID '{provider_id}' already registered")
    ADAPTER_REGISTRY[provider_id] = adapter


def get_adapter(provider_id: str) -> ProviderAdapterProtocol | None:
    """Get adapter by provider ID.

    Args:
        provider_id: Normalized provider ID

    Returns:
        Adapter instance if found, None otherwise
    """
    return ADAPTER_REGISTRY.get(provider_id)


def list_adapters() -> list[str]:
    """List all registered provider IDs."""
    return list(ADAPTER_REGISTRY.keys())


def filter_adapters(enabled_providers: list[str] | None) -> dict[str, ProviderAdapterProtocol]:
    """Filter registry to only include enabled providers.

    Args:
        enabled_providers: List of provider IDs to include, or None for all

    Returns:
        Filtered adapter registry
    """
    if enabled_providers is None:
        return ADAPTER_REGISTRY.copy()

    normalized_enabled = [p.lower().replace(" ", "") for p in enabled_providers]
    return {
        pid: adapter
        for pid, adapter in ADAPTER_REGISTRY.items()
        if pid in normalized_enabled
    }
