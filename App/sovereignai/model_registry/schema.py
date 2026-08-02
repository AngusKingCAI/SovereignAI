from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class Provider(BaseModel):
    """Provider configuration and metadata."""
    id: str
    name: str
    api_base_url: str
    auth_type: str
    is_enabled: bool = True


class ModelFamily(BaseModel):
    """Model family grouping within a provider."""
    id: str
    provider_id: str
    name: str
    description: str = ""


class Model(BaseModel):
    """Model within a family."""
    id: str
    family_id: str
    name: str


class ModelVersion(BaseModel):
    """Specific version of a model."""
    id: str
    model_id: str
    version_string: str
    release_date: datetime | None = None
    is_latest: bool = False
    context_window: int | None = None
    supports_vision: bool = False
    supports_tools: bool = False
    capabilities: dict[str, Any] = Field(default_factory=dict)


class NormalizedModelData(BaseModel):
    """Normalized model data returned by all provider adapters."""
    provider_id: str
    model_id: str
    model_name: str
    version_string: str
    release_date: datetime | None = None
    context_window: int | None = None
    supports_vision: bool = False
    supports_tools: bool = False
    capabilities: dict[str, Any] = Field(default_factory=dict)
