"""Registry of conformance test classes by capability class.

First-party tests are registered here. Third-party tests are discovered via
Python entry points ('sovereignai.conformance' group).
"""
from typing import Type, Callable, Any
import importlib.metadata

_CONFORMANCE_TESTS: dict[str, list[Type]] = {}


def register(capability_class: str) -> Callable[[Type], Type]:
    """Decorator: register a conformance test class for a capability class."""
    def decorator(cls: Type) -> Type:
        _CONFORMANCE_TESTS.setdefault(capability_class, []).append(cls)
        return cls
    return decorator


def get_conformance_tests_for_class(capability_class: str) -> list[Type]:
    """Return all conformance test classes for a capability class.

    Combines first-party (registered via decorator) and third-party (entry points).
    """
    tests = list(_CONFORMANCE_TESTS.get(capability_class, []))
    # Discover third-party conformance tests via entry points (per Rev3 N12)
    # Rev8: EntryPoints.select() accepts 'group' and 'name', NOT 'capability_class'.
    # Third-party tests register with name=capability_class; we filter by name.
    try:
        eps: Any = importlib.metadata.entry_points()
        if hasattr(eps, "select"):  # Python 3.10+
            eps = eps.select(group="sovereignai.conformance")
        else:  # Python 3.9
            eps = eps.get("sovereignai.conformance", [])
        for ep in eps:
            if ep.name == capability_class:  # Filter by name, not capability_class
                try:
                    cls: Type = ep.load()
                    tests.append(cls)
                except Exception:
                    pass
    except Exception:
        pass
    return tests
