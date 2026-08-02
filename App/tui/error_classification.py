"""Error classification for TUI API responses.

Classifies API errors by error code (not just HTTP status) per Plan 32 S3.12.
Provides retry logic and UI surface behavior guidance.
"""

from __future__ import annotations

from enum import Enum
from typing import Any


class ErrorClassification(Enum):
    """Error classification categories."""
    TERMINAL = "terminal"  # Stop retry, surface login prompt
    TERMINAL_NO_LOGIN = "terminal_no_login"  # Stop retry, no login prompt
    TRANSIENT = "transient"  # Retry with backoff
    TRANSIENT_SSE_CONTROL = "transient_sse_control"  # Hold SSE connection
    OPERATOR = "operator"  # Surface to operator with retry button


class ErrorAction:
    """Recommended action for classified errors."""

    def __init__(
        self,
        classification: ErrorClassification,
        retry_after_seconds: int | None = None,
        backoff_base: float = 1.0,
        backoff_max: float = 30.0,
        message: str = "",
    ) -> None:
        self.classification = classification
        self.retry_after_seconds = retry_after_seconds
        self.backoff_base = backoff_base
        self.backoff_max = backoff_max
        self.message = message


def classify_error(response: dict[str, Any]) -> ErrorAction:
    """Classify API error by error code and HTTP status.

    Args:
        response: API response dict with status_code and optional error_code field.

    Returns:
        ErrorAction with classification and retry guidance.
    """
    status_code = response.get("status_code", 0)
    error_code = response.get("error_code", "")
    retry_after_header = response.get("retry_after")
    retry_after_envelope = response.get("retry_after_seconds")

    # Prefer header over envelope if both present
    retry_after = retry_after_header if retry_after_header is not None else retry_after_envelope

    # Terminal errors (require login)
    if error_code in ["auth_expired", "login_required", "authorization_denied", "setup_token_required", "insecure_deployment"]:
        return ErrorAction(
            classification=ErrorClassification.TERMINAL,
            message="Authentication required. Please login."
        )

    # Terminal errors (no login prompt)
    if error_code == "lockout":
        retry_after = retry_after or 300  # Default 5 minutes
        return ErrorAction(
            classification=ErrorClassification.TERMINAL_NO_LOGIN,
            retry_after_seconds=retry_after,
            message=f"Account locked. Retry after {retry_after}s."
        )

    if error_code == "idempotency_conflict":
        return ErrorAction(
            classification=ErrorClassification.TERMINAL_NO_LOGIN,
            message="Duplicate request detected."
        )

    if error_code == "not_ready_timeout":
        return ErrorAction(
            classification=ErrorClassification.TERMINAL_NO_LOGIN,
            message="Server still initializing. Please reconnect manually."
        )

    # Transient errors with explicit retry-after
    if status_code == 429:  # Rate limited
        retry_after = retry_after or 60  # Default 1 minute
        return ErrorAction(
            classification=ErrorClassification.TRANSIENT,
            retry_after_seconds=retry_after,
            message=f"Rate limited. Retry after {retry_after}s."
        )

    if status_code == 503:
        if error_code == "memory_not_ready":
            retry_after = retry_after or 10
            return ErrorAction(
                classification=ErrorClassification.TRANSIENT,
                retry_after_seconds=retry_after,
                message="Memory backend loading..."
            )

        if error_code == "service_draining":
            retry_after = retry_after or 60
            return ErrorAction(
                classification=ErrorClassification.TRANSIENT,
                retry_after_seconds=retry_after,
                message="Server shutting down. Drain rejection."
            )

        # Generic 503
        retry_after = retry_after or 5
        if retry_after > 30:
            return ErrorAction(
                classification=ErrorClassification.OPERATOR,
                message="Server shutting down."
            )
        return ErrorAction(
            classification=ErrorClassification.TRANSIENT,
            retry_after_seconds=retry_after,
            message="Service temporarily unavailable."
        )

    # SSE control errors
    if error_code == "not_ready":
        return ErrorAction(
            classification=ErrorClassification.TRANSIENT_SSE_CONTROL,
            message="Holding SSE connection..."
        )

    # Operator errors
    if status_code == 501:
        return ErrorAction(
            classification=ErrorClassification.OPERATOR,
            message="Feature not implemented."
        )

    # Generic transient errors (5xx except 501, 503 handled above)
    if status_code in [500, 502, 504]:
        return ErrorAction(
            classification=ErrorClassification.TRANSIENT,
            backoff_base=1.0,
            backoff_max=30.0,
            message="Server error. Retrying with backoff..."
        )

    if status_code == 408:  # Request timeout
        return ErrorAction(
            classification=ErrorClassification.TRANSIENT,
            backoff_base=1.0,
            backoff_max=30.0,
            message="Request timeout. Retrying..."
        )

    # Terminal 4xx (except 401, 403, 404, 408, 409, 429 handled above)
    if 400 <= status_code < 500 and status_code not in [401, 403, 404, 408, 409, 429]:
        return ErrorAction(
            classification=ErrorClassification.TERMINAL,
            message=f"Client error: HTTP {status_code}"
        )

    # Default: treat as transient
    return ErrorAction(
        classification=ErrorClassification.TRANSIENT,
        backoff_base=1.0,
        backoff_max=30.0,
        message="Unknown error. Retrying..."
    )
