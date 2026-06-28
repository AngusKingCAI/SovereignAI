"""Core domain types shared across all SovereignAI components.

This module is the single source of truth for domain types. All other
modules import from here — never define duplicate types elsewhere.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import NewType
from uuid import UUID, uuid4

# ============================================================================
# Trace types (used by TraceEmitter in S3)
# ============================================================================

class TraceLevel(StrEnum):
    """Severity level for trace events, ordered from least to most severe."""
    TRACE = "trace"
    DEBUG = "debug"
    INFO = "info"
    WARN = "warn"
    ERROR = "error"


@dataclass(frozen=True)
class TraceEvent:
    """Single observability event emitted by a component via TraceEmitter.

    Immutable so events can be safely shared across threads and stored in
    trace memory without risk of mutation.
    """
    component: str          # e.g. "EventBus", "TraceEmitter", "main"
    level: TraceLevel
    message: str            # plain-English description of what happened
    timestamp: datetime     # UTC, timezone-aware (per OR20)
    correlation_id: UUID    # groups events from the same task or request


# ============================================================================
# Event bus types (used by EventBus in S2)
# ============================================================================

# Typed channel identifier — NewType prevents passing a raw string where a
# Channel is expected. Channels are per-type: each event type has its own
# channel, and the bus guarantees in-order delivery per channel (per A9).
Channel = NewType("Channel", str)


@dataclass(frozen=True)
class Event:
    """Base type for all events published on the event bus.

    Subclasses (defined in Plans 2-4) add payload fields. The base type
    carries only routing metadata. Frozen so events are immutable once
    published — a subscriber cannot modify an event before another
    subscriber sees it.
    """
    channel: Channel
    correlation_id: UUID
    timestamp: datetime     # UTC, timezone-aware (per OR20)


# ============================================================================
# Component identity (used by DI container in S4, capability graph in Plan 2)
# ============================================================================

ComponentId = NewType("ComponentId", str)  # e.g. "EventBus", "TraceEmitter"


# ============================================================================
# Helper functions
# ============================================================================

def now_utc() -> datetime:
    """Return the current time in UTC with timezone awareness to avoid naive datetime issues.

    Use this instead of datetime.now() or datetime.utcnow() — both are
    forbidden per OR20 (naive/aware datetime mixing caused L6).
    """
    return datetime.now(UTC)


def new_correlation_id() -> UUID:
    """Generate a fresh UUID4 for correlating events across components in the system."""
    return uuid4()
