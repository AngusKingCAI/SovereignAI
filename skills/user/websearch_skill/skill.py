"""Search the web using DuckDuckGo's HTML interface.

This skill accepts a search query string and returns a list of
result snippets. It uses only the Python standard library to avoid
adding runtime dependencies per the minimal-deps philosophy.

Known risk: DuckDuckGo HTML interface may return 403, CAPTCHAs,
or change DOM structure without notice. This is a v1 limitation
documented in DEBT.md.
"""
from __future__ import annotations

import asyncio
import html.parser
import time
from dataclasses import dataclass
from typing import Optional

import httpx

from sovereignai.shared.trace_emitter import TraceEmitter, TraceLevel


@dataclass
class SearchResult:
    """Single search result from DuckDuckGo."""
    title: str
    snippet: str
    url: str


class DuckDuckGoHTMLParser(html.parser.HTMLParser):
    """Parse DuckDuckGo HTML to extract search results.

    This parser extracts titles and snippets from DuckDuckGo's
    result__title and result__snippet classes.
    """

    def __init__(self) -> None:
        """Initialize the parser with state tracking."""
        super().__init__()
        self.results: list[SearchResult] = []
        self._in_title = False
        self._in_snippet = False
        self._current_title = ""
        self._current_snippet = ""
        self._current_url = ""
        self._in_link = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        """Handle opening HTML tags to detect result containers."""
        attrs_dict = dict(attrs)
        class_attr = attrs_dict.get("class", "")

        if tag == "a" and class_attr and "result__title" in class_attr:
            self._in_title = True
            self._in_link = True
            self._current_url = attrs_dict.get("href", "") or ""
        elif tag == "div" and class_attr and "result__snippet" in class_attr:
            self._in_snippet = True

    def handle_endtag(self, tag: str) -> None:
        """Handle closing tags to finalize result extraction."""
        if tag == "a" and self._in_title:
            self._in_title = False
            self._in_link = False
        elif tag == "div" and self._in_snippet:
            self._in_snippet = False
            # Save the result when we exit the snippet
            if self._current_title or self._current_snippet:
                self.results.append(SearchResult(
                    title=self._current_title.strip(),
                    snippet=self._current_snippet.strip(),
                    url=self._current_url,
                ))
                self._current_title = ""
                self._current_snippet = ""
                self._current_url = ""

    def handle_data(self, data: str) -> None:
        """Handle text content within tags."""
        if self._in_title:
            self._current_title += data
        elif self._in_snippet:
            self._current_snippet += data


class WebSearchSkill:
    """Web search skill using DuckDuckGo HTML interface.

    This skill provides web search capability by querying DuckDuckGo's
    HTML interface and parsing the results. It includes rate limiting
    to avoid being blocked by DuckDuckGo.
    """

    def __init__(self, trace: TraceEmitter) -> None:
        """Create a web search skill with rate limiting.

        Args:
            trace: Trace emitter for logging search operations.
        """
        self._trace = trace
        self._last_request_time = 0.0
        self._min_request_interval = 2.0  # 2 seconds between requests

    async def search(self, query: str) -> list[dict]:
        """Search the web for the given query and return results.

        Args:
            query: Search query string.

        Returns:
            List of dicts with keys: title, snippet, url. Empty list on error.
        """
        # Rate limiting: wait if needed
        now = time.time()
        time_since_last = now - self._last_request_time
        if time_since_last < self._min_request_interval:
            wait_time = self._min_request_interval - time_since_last
            await asyncio.sleep(wait_time)

        self._last_request_time = time.time()

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://html.duckduckgo.com/html/",
                    params={"q": query},
                    headers={"User-Agent": "SovereignAI/0.1.0"},
                    timeout=10.0,
                )
                response.raise_for_status()

            # Parse HTML
            parser = DuckDuckGoHTMLParser()
            parser.feed(response.text)

            # Convert to dict format
            results = [
                {
                    "title": result.title,
                    "snippet": result.snippet,
                    "url": result.url,
                }
                for result in parser.results
            ]

            self._trace.emit(
                component="WebSearchSkill",
                level=TraceLevel.INFO,
                message=f"Search for '{query}' returned {len(results)} results",
            )
            return results

        except httpx.HTTPError as exc:
            self._trace.emit(
                component="WebSearchSkill",
                level=TraceLevel.ERROR,
                message=f"HTTP error during search: {exc}",
            )
            return []
        except Exception as exc:
            self._trace.emit(
                component="WebSearchSkill",
                level=TraceLevel.ERROR,
                message=f"Unexpected error during search: {exc}",
            )
            return []
