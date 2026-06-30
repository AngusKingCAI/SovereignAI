"""Registry for database providers.

Databases register themselves at startup and can be retrieved by name.
"""

from sovereignai.databases.base import DatabaseBase


class DatabaseRegistry:
    """Registry for database provider classes."""

    _databases: dict[str, type[DatabaseBase]] = {}

    @classmethod
    def register(cls, database_class: type[DatabaseBase]) -> None:
        """Register a database provider class in the registry for later retrieval."""
        instance = database_class()
        cls._databases[instance.name] = database_class

    @classmethod
    def get(cls, name: str) -> type[DatabaseBase] | None:
        """Get a database provider class by its registered name identifier."""
        return cls._databases.get(name)

    @classmethod
    def list_all(cls) -> dict[str, type[DatabaseBase]]:
        """Return a copy of all registered database providers in the registry."""
        return cls._databases.copy()

    @classmethod
    def clear(cls) -> None:
        """Clear all registered databases from the registry for testing purposes."""
        cls._databases.clear()
