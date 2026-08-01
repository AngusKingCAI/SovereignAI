from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ValidationResult:
    passed: bool
    reason: str | None = None
    details: dict[str, Any] | None = None


@dataclass(frozen=True)
class Deliverable:
    success: bool
    output: Any
    validation_failure: ValidationResult | None = None
