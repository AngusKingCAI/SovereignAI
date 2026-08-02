from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Button, DataTable, Static

from app.tui.client import TUIWebClient


class AuditPanel(Vertical):
    """Audit panel showing cross-department messaging audit from /api/messaging/audit.

    Extracts AuditPage.items with source_department, target_department, content.
    Displays as paginated table with timestamp, source→target columns, content preview.
    Uses REST polling (SSE disabled per DEBT-7).
    """

    def __init__(
        self,
        client: TUIWebClient,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._client = client
        self._audit_data: dict[str, Any] = {}
        self._current_page: int = 1
        self._page_size: int = 20

    def compose(self) -> ComposeResult:
        yield Static("Messaging Audit", id="audit-title")
        yield Button("Refresh", id="btn-refresh")
        yield Button("Previous Page", id="btn-prev")
        yield Button("Next Page", id="btn-next")
        yield DataTable(id="audit-table")

    def on_mount(self) -> None:
        self.call_after_refresh(self._load_data)

    async def _load_data(self) -> None:
        """Load audit data from /api/messaging/audit."""
        try:
            params = {
                "page": self._current_page,
                "page_size": self._page_size
            }
            async with self._client as client:
                response = await client.get("/api/messaging/audit", params=params)
                if response.status_code == 200:
                    self._audit_data = response.json()
                    self._update_display()
                else:
                    self._update_error(f"HTTP {response.status_code}")
        except Exception as e:
            self._update_error(str(e))

    def _update_display(self) -> None:
        """Update display with audit entries."""
        try:
            table = self.query_one("#audit-table", DataTable)
            table.clear(columns=True)
            table.add_column("Timestamp")
            table.add_column("Source → Target")
            table.add_column("Content Preview")

            items = self._audit_data.get("items", [])
            total_count = self._audit_data.get("total_count", 0)
            page_count = self._audit_data.get("page_count", 0)

            if not items:
                table.add_row("--", "--", "--")
                return

            for item in items:
                timestamp = item.get("timestamp", "")
                source_dept = item.get("source_department", "unknown")
                target_dept = item.get("target_department", "unknown")
                content = item.get("content", "")

                # Create source→target column
                flow = f"{source_dept} → {target_dept}"

                # Truncate content preview
                content_preview = content[:50] + "..." if len(content) > 50 else content

                table.add_row(timestamp, flow, content_preview)

            # Update title with pagination info
            title = self.query_one("#audit-title", Static)
            title.update(f"Messaging Audit (Page {self._current_page}/{page_count}, Total: {total_count})")
        except Exception:
            # Widget tree not mounted (e.g., during testing)
            pass

    def _update_error(self, error_msg: str) -> None:
        """Update display with error message."""
        try:
            table = self.query_one("#audit-table", DataTable)
            table.clear(columns=True)
            table.add_column("Timestamp")
            table.add_column("Source → Target")
            table.add_column("Content Preview")
            table.add_row(f"Error: {error_msg}", "--", "--")
        except Exception:
            # Widget tree not mounted (e.g., during testing)
            pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-refresh":
            self.call_after_refresh(self._load_data)
        elif event.button.id == "btn-prev":
            if self._current_page > 1:
                self._current_page -= 1
                self.call_after_refresh(self._load_data)
        elif event.button.id == "btn-next":
            page_count = self._audit_data.get("page_count", 0)
            if self._current_page < page_count:
                self._current_page += 1
                self.call_after_refresh(self._load_data)
