"""Registry for service providers.

Services register themselves at startup and can be retrieved by name.
"""

from sovereignai.services.base import ServiceBase


class ServiceRegistry:
    """Registry for service provider classes."""

    _services: dict[str, type[ServiceBase]] = {}

    @classmethod
    def register(cls, service_class: type[ServiceBase]) -> None:
        """Register a service provider class in the registry for later retrieval."""
        instance = service_class()
        cls._services[instance.name] = service_class

    @classmethod
    def get(cls, name: str) -> type[ServiceBase] | None:
        """Get a service provider class by its registered name identifier."""
        return cls._services.get(name)

    @classmethod
    def list_all(cls) -> dict[str, type[ServiceBase]]:
        """Return a copy of all registered service providers in the registry."""
        return cls._services.copy()

    @classmethod
    def clear(cls) -> None:
        """Clear all registered services from the registry for testing purposes."""
        cls._services.clear()
