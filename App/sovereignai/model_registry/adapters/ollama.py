from datetime import datetime

from sovereignai.model_registry.schema import NormalizedModelData


class OllamaAdapter:
    """Adapter for Ollama provider."""

    async def fetch_models(self, api_key: str) -> list[NormalizedModelData]:
        """Fetch models from Ollama API."""
        # This is a placeholder implementation
        # In a real implementation, this would make HTTP requests to Ollama's API
        # For now, return mock data for testing

        # Ollama typically doesn't require API keys
        return [
            NormalizedModelData(
                provider_id="ollama",
                model_id="llama3",
                model_name="Llama 3",
                version_string="8b",
                release_date=datetime(2024, 4, 1),
                context_window=8192,
                supports_vision=False,
                supports_tools=False,
                capabilities={},
            ),
            NormalizedModelData(
                provider_id="ollama",
                model_id="llama3",
                model_name="Llama 3",
                version_string="70b",
                release_date=datetime(2024, 4, 1),
                context_window=8192,
                supports_vision=False,
                supports_tools=False,
                capabilities={},
            ),
        ]
