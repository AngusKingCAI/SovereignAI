"""Connect to Ollama local model server for text generation.

This adapter wraps the official Ollama Python client to provide
capability-based model inference. It registers with the capability
graph on startup and reports DEGRADED status if Ollama is not running.
"""
from __future__ import annotations

from typing import Optional

import ollama

from sovereignai.shared.trace_emitter import TraceEmitter, TraceLevel


class OllamaAdapter:
    """Adapter for Ollama local model server.

    This adapter provides text generation and chat completion capabilities
    via the Ollama Python client. It performs a health check on initialization
    to determine if Ollama is running.
    """

    def __init__(self, trace: TraceEmitter) -> None:
        """Create an Ollama adapter with health check.

        Args:
            trace: Trace emitter for logging adapter operations.
        """
        self._trace = trace
        self._healthy = self._health_check()
        if not self._healthy:
            self._trace.emit(
                component="OllamaAdapter",
                level=TraceLevel.WARN,
                message="Ollama health check failed - adapter registered as DEGRADED",
            )

    def health_check(self) -> bool:
        """Check if Ollama is running and accessible.

        Returns:
            True if Ollama is running, False otherwise.
        """
        return self._healthy

    def _health_check(self) -> bool:
        """Internal health check that queries Ollama for available models.

        Returns:
            True if Ollama responds to list() call, False otherwise.
        """
        try:
            ollama.list()
            return True
        except Exception as exc:
            self._trace.emit(
                component="OllamaAdapter",
                level=TraceLevel.ERROR,
                message=f"Health check failed: {exc}",
            )
            return False

    def generate(self, prompt: str, model: str = "llama3.2") -> str:
        """Generate text using the specified Ollama model.

        Args:
            prompt: The text prompt to generate from.
            model: The Ollama model to use (default: llama3.2).

        Returns:
            Generated text string.

        Raises:
            RuntimeError: If Ollama is not healthy or generation fails.
        """
        if not self._healthy:
            raise RuntimeError("Ollama adapter is not healthy - cannot generate text")

        try:
            response = ollama.generate(model=model, prompt=prompt)
            result = str(response.get("response", ""))  # type: ignore[no-any-return]
            self._trace.emit(
                component="OllamaAdapter",
                level=TraceLevel.DEBUG,
                message=f"Generated {len(result)} characters using model {model}",
            )
            return result
        except Exception as exc:
            self._trace.emit(
                component="OllamaAdapter",
                level=TraceLevel.ERROR,
                message=f"Generation failed: {exc}",
            )
            raise RuntimeError(f"Ollama generation failed: {exc}") from exc

    def chat(self, messages: list[dict], model: str = "llama3.2") -> dict:
        """Generate a chat completion using the specified Ollama model.

        Args:
            messages: List of message dicts with 'role' and 'content' keys.
            model: The Ollama model to use (default: llama3.2).

        Returns:
            Dict with 'role' and 'content' keys for the assistant's response.

        Raises:
            RuntimeError: If Ollama is not healthy or chat fails.
        """
        if not self._healthy:
            raise RuntimeError("Ollama adapter is not healthy - cannot complete chat")

        try:
            response = ollama.chat(model=model, messages=messages)
            message = dict(response.get("message", {}))  # type: ignore[no-any-return]
            self._trace.emit(
                component="OllamaAdapter",
                level=TraceLevel.DEBUG,
                message=f"Chat completion using model {model}",
            )
            return message
        except Exception as exc:
            self._trace.emit(
                component="OllamaAdapter",
                level=TraceLevel.ERROR,
                message=f"Chat completion failed: {exc}",
            )
            raise RuntimeError(f"Ollama chat completion failed: {exc}") from exc
