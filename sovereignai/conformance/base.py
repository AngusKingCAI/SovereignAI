from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ConformanceResult:
    passed: bool
    message: str


class BaseConformanceTest(ABC):

    @abstractmethod
    def test_component_has_required_interface(self, instance: object) -> None:
        pass
