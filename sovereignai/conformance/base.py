"""Base conformance test abstract class.

Conformance tests verify that a component implements its declared capability
correctly. Each test class inherits from BaseConformanceTest and defines
test_* methods that pytest can discover.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ConformanceResult:
    """Result of a conformance test run."""
    passed: bool
    message: str


class BaseConformanceTest(ABC):
    """Abstract base class for conformance tests.

    Subclasses define test_* methods that pytest discovers. Each method
    should assert on the component instance passed to it.
    """

    @abstractmethod
    def test_component_has_required_interface(self, instance) -> None:
        """Verify the component implements the required capability interface."""
        pass
