"""Tests for WebSearchSkill."""
from __future__ import annotations

from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest

from skills.user.websearch_skill.skill import WebSearchSkill
from sovereignai.shared.trace_emitter import TraceEmitter


@pytest.fixture
def trace() -> TraceEmitter:
    """Create a trace emitter for testing."""
    return TraceEmitter()


@pytest.fixture
def skill(trace: TraceEmitter) -> WebSearchSkill:
    """Create a web search skill for testing."""
    return WebSearchSkill(trace=trace)


@pytest.mark.asyncio
async def test_search_success(skill: WebSearchSkill) -> None:
    """Test successful web search with mock HTTP response."""
    mock_html = """
    <html>
    <body>
        <div class="result">
            <a class="result__title" href="https://example.com">Example Title</a>
            <div class="result__snippet">Example snippet text</div>
        </div>
    </body>
    </html>
    """

    with patch("skills.user.websearch_skill.skill.httpx.AsyncClient") as mock_client:
        mock_response = Mock()
        mock_response.text = mock_html
        mock_response.raise_for_status = Mock()
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

        results = await skill.search("test query")

        assert len(results) == 1
        assert results[0]["title"] == "Example Title"
        assert results[0]["snippet"] == "Example snippet text"
        assert results[0]["url"] == "https://example.com"


@pytest.mark.asyncio
async def test_search_empty_results(skill: WebSearchSkill) -> None:
    """Test web search with no results."""
    mock_html = "<html><body>No results here</body></html>"

    with patch("skills.user.websearch_skill.skill.httpx.AsyncClient") as mock_client:
        mock_response = Mock()
        mock_response.text = mock_html
        mock_response.raise_for_status = Mock()
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

        results = await skill.search("test query")

        assert len(results) == 0


@pytest.mark.asyncio
async def test_search_network_error(skill: WebSearchSkill) -> None:
    """Test web search with network error."""
    with patch("skills.user.websearch_skill.skill.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            side_effect=httpx.HTTPError("Network error")
        )

        results = await skill.search("test query")

        assert len(results) == 0


@pytest.mark.asyncio
async def test_search_rate_limiting(skill: WebSearchSkill) -> None:
    """Test that rate limiting enforces minimum interval between requests."""
    mock_html = "<html><body>Result</body></html>"

    with patch("skills.user.websearch_skill.skill.httpx.AsyncClient") as mock_client:
        mock_response = Mock()
        mock_response.text = mock_html
        mock_response.raise_for_status = Mock()
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

        import asyncio

        # First request
        await skill.search("query1")

        # Second request immediately - should wait due to rate limiting
        start = asyncio.get_event_loop().time()
        await skill.search("query2")
        elapsed = asyncio.get_event_loop().time() - start

        # Should have waited at least 2 seconds (minus first request time)
        assert elapsed >= 1.9  # Allow small margin


@pytest.mark.asyncio
async def test_search_user_agent_header(skill: WebSearchSkill) -> None:
    """Test that User-Agent header is set correctly."""
    with patch("skills.user.websearch_skill.skill.httpx.AsyncClient") as mock_client:
        mock_response = Mock()
        mock_response.text = "<html></html>"
        mock_response.raise_for_status = Mock()
        mock_get = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value.get = mock_get

        await skill.search("test")

        # Check that get was called with User-Agent header
        call_kwargs = mock_get.call_args[1]
        assert "headers" in call_kwargs
        assert call_kwargs["headers"]["User-Agent"] == "SovereignAI/0.1.0"
