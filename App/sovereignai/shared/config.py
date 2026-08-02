from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    version_negotiation_enabled: bool = True
