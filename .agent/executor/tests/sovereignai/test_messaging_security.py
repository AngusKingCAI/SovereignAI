from __future__ import annotations

import datetime
import sqlite3
import tempfile
import time
import uuid
from pathlib import Path

import pytest
from sovereignai.messaging.schema import CrossDepartmentMessage, MessageType
from sovereignai.messaging.security import AuditLogger, CircuitBreaker, RateLimiter
from sovereignai.shared.trace_emitter import TraceEmitter


@pytest.fixture
def trace():
    return TraceEmitter()


@pytest.fixture
def temp_db():
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as f:
        db_path = Path(f.name)
    yield db_path
    if db_path.exists():
        db_path.unlink()


def test_audit_logger_initialization(temp_db, trace):
    logger = AuditLogger(temp_db, trace)
    assert logger._db_path == temp_db


def test_audit_logger_creates_table(temp_db, trace):
    AuditLogger(temp_db, trace)
    conn = sqlite3.connect(str(temp_db))
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='messaging_audit'"
    )
    result = cursor.fetchone()
    conn.close()
    assert result is not None
    assert result[0] == "messaging_audit"


def test_audit_logger_log_message(temp_db, trace):
    logger = AuditLogger(temp_db, trace)
    msg = CrossDepartmentMessage(
        sender="coding",
        recipient="research",
        payload={"task": "implement feature"},
        correlation_id=uuid.uuid4(),
        timestamp=datetime.datetime.now(datetime.UTC),
        message_type=MessageType.REQUEST,
    )
    logger.log_message(msg, "success")

    conn = sqlite3.connect(str(temp_db))
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM messaging_audit")
    count = cursor.fetchone()[0]
    conn.close()
    assert count == 1


def test_audit_logger_log_message_with_error(temp_db, trace):
    logger = AuditLogger(temp_db, trace)
    msg = CrossDepartmentMessage(
        sender="coding",
        recipient="research",
        payload={"task": "implement feature"},
        correlation_id=uuid.uuid4(),
        timestamp=datetime.datetime.now(datetime.UTC),
        message_type=MessageType.REQUEST,
    )
    logger.log_message(msg, "error", "RuntimeError")

    conn = sqlite3.connect(str(temp_db))
    cursor = conn.cursor()
    cursor.execute("SELECT error_class FROM messaging_audit")
    error_class = cursor.fetchone()[0]
    conn.close()
    assert error_class == "RuntimeError"


def test_audit_logger_payload_redacted(temp_db, trace):
    logger = AuditLogger(temp_db, trace)
    msg = CrossDepartmentMessage(
        sender="coding",
        recipient="research",
        payload={"secret": "password123", "task": "implement feature"},
        correlation_id=uuid.uuid4(),
        timestamp=datetime.datetime.now(datetime.UTC),
        message_type=MessageType.REQUEST,
    )
    logger.log_message(msg, "success")

    conn = sqlite3.connect(str(temp_db))
    cursor = conn.cursor()
    cursor.execute("SELECT payload_byte_length FROM messaging_audit")
    byte_length = cursor.fetchone()[0]
    conn.close()
    assert byte_length > 0


def test_rate_limiter_initialization(trace):
    limiter = RateLimiter(max_messages=100, window_seconds=60, trace=trace)
    assert limiter._max_messages == 100
    assert limiter._window_seconds == 60


def test_rate_limiter_allows_within_limit(trace):
    limiter = RateLimiter(max_messages=10, window_seconds=60, trace=trace)
    for _ in range(10):
        assert limiter.is_allowed("sender", "recipient")


def test_rate_limiter_blocks_over_limit(trace):
    limiter = RateLimiter(max_messages=5, window_seconds=60, trace=trace)
    for _ in range(5):
        assert limiter.is_allowed("sender", "recipient")
    assert not limiter.is_allowed("sender", "recipient")


def test_rate_limiter_window_expiration(trace):
    limiter = RateLimiter(max_messages=5, window_seconds=1, trace=trace)
    for _ in range(5):
        assert limiter.is_allowed("sender", "recipient")
    assert not limiter.is_allowed("sender", "recipient")
    time.sleep(1.1)
    assert limiter.is_allowed("sender", "recipient")


def test_rate_limiter_separate_pairs(trace):
    limiter = RateLimiter(max_messages=3, window_seconds=60, trace=trace)
    for _ in range(3):
        assert limiter.is_allowed("sender1", "recipient1")
    assert not limiter.is_allowed("sender1", "recipient1")
    assert limiter.is_allowed("sender2", "recipient2")


def test_circuit_breaker_initialization(trace):
    breaker = CircuitBreaker(failure_threshold=5, timeout_seconds=30, trace=trace)
    assert breaker._failure_threshold == 5
    assert breaker._timeout_seconds == 30


def test_circuit_breaker_records_failure(trace):
    breaker = CircuitBreaker(failure_threshold=3, timeout_seconds=30, trace=trace)
    assert not breaker.record_failure("recipient")
    assert not breaker.record_failure("recipient")
    assert breaker.record_failure("recipient")


def test_circuit_breaker_opens_on_threshold(trace):
    breaker = CircuitBreaker(failure_threshold=3, timeout_seconds=30, trace=trace)
    assert not breaker.is_open("recipient")
    breaker.record_failure("recipient")
    breaker.record_failure("recipient")
    assert not breaker.is_open("recipient")
    breaker.record_failure("recipient")
    assert breaker.is_open("recipient")


def test_circuit_breaker_resets_on_success(trace):
    breaker = CircuitBreaker(failure_threshold=3, timeout_seconds=30, trace=trace)
    breaker.record_failure("recipient")
    breaker.record_failure("recipient")
    breaker.record_success("recipient")
    assert not breaker.is_open("recipient")


def test_circuit_breaker_timeout_reset(trace):
    breaker = CircuitBreaker(failure_threshold=3, timeout_seconds=1, trace=trace)
    breaker.record_failure("recipient")
    breaker.record_failure("recipient")
    breaker.record_failure("recipient")
    assert breaker.is_open("recipient")
    time.sleep(1.1)
    assert not breaker.is_open("recipient")


def test_circuit_breaker_separate_recipients(trace):
    breaker = CircuitBreaker(failure_threshold=3, timeout_seconds=30, trace=trace)
    for _ in range(3):
        breaker.record_failure("recipient1")
    assert breaker.is_open("recipient1")
    assert not breaker.is_open("recipient2")


def test_circuit_breaker_should_emit_event(trace):
    breaker = CircuitBreaker(failure_threshold=3, timeout_seconds=30, trace=trace)
    assert not breaker.should_emit_circuit_event("recipient")
    assert not breaker.should_emit_circuit_event("recipient")
    assert breaker.should_emit_circuit_event("recipient")
