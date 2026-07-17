from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from sovereignai.skills.session import SkillSession


@dataclass
class SkillResult:
    output: str
    error: str | None
    execution_time_ms: int


@runtime_checkable
class ISkillRunner(Protocol):
    def run(
        self,
        skill_id: str,
        args: dict[str, Any],
        session: SkillSession,
    ) -> SkillResult:
        ...

    def health_check(self) -> bool:
        ...

    def list_capabilities(self) -> list[str]:
        ...

    def close(self) -> None:
        ...
