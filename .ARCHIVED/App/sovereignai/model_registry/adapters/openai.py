from datetime import datetime

from sovereignai.model_registry.schema import NormalizedModelData
from sovereignai.model_registry.sync import (
    ProviderAuthError,
)


class OpenAIAdapter:
    """Adapter for OpenAI provider."""

    async def fetch_models(self, api_key: str) -> list[NormalizedModelData]:
        """Fetch models from OpenAI API."""
        # This is a placeholder implementation
        # In a real implementation, this would make HTTP requests to OpenAI's API
        # For now, return mock data for testing

        if not api_key:
            raise ProviderAuthError("API key is required")

        # Mock response for testing
        return [
            NormalizedModelData(
                provider_id="openai",
                model_id="gpt-4-turbo",
                model_name="GPT-4 Turbo",
                version_string="2024-04-09",
                release_date=datetime(2024, 4, 9),
                context_window=128000,
                supports_vision=True,
                supports_tools=True,
                capabilities={"function_calling": True, "json_mode": True},
            ),
            NormalizedModelData(
                provider_id="openai",
                model_id="gpt-3.5-turbo",
                model_name="GPT-3.5 Turbo",
                version_string="2024-04-09",
                release_date=datetime(2024, 4, 9),
                context_window=16385,
                supports_vision=False,
                supports_tools=True,
                capabilities={"function_calling": True},
            ),
        ]
