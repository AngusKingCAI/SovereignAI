from pydantic import BaseModel, Field, field_validator


class APIKey(BaseModel):
    """API key configuration with encrypted storage."""
    provider: str
    key: str = Field(default="")


class DisplaySettings(BaseModel):
    """Display and UI preferences."""
    theme: str = Field(default="dark")
    font_size: int = Field(default=14, ge=8, le=32)
    panel_layout: str = Field(default="default")
    language: str = Field(default="en")


class BehaviorSettings(BaseModel):
    """Behavior and operational preferences."""
    auto_save: bool = Field(default=True)
    confirm_destructive: bool = Field(default=True)
    default_department: str = Field(default="research")
    max_iterations: int = Field(default=10, ge=1, le=100)
    conversation_retention_days: int = Field(default=7, ge=1, le=365)
    model_sync_interval_hours: int = Field(default=24, ge=1, le=168)
    enabled_providers: list[str] | None = Field(default=None)
    sync_error_retention_days: int = Field(default=30, ge=1, le=365)

    @field_validator("enabled_providers")
    @classmethod
    def validate_providers(cls, v: list[str] | None) -> list[str] | None:
        if v is not None and not v:
            return None
        return v
