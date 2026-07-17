from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import pytest  # noqa: F401

from sovereignai.shared.file_trace_subscriber import FileTraceSubscriber
from sovereignai.shared.types import TraceEvent, TraceLevel


def test_subscriber_writes_event(tmp_path: Path) -> None:
    subscriber = FileTraceSubscriber(log_dir=str(tmp_path))
    event = TraceEvent(
        component="test",
        level=TraceLevel.INFO,
        message="test message",
        timestamp=datetime.now(UTC),
        correlation_id=uuid4(),
    )
    subscriber(event)
    subscriber.close()

    log_files = list(tmp_path.glob("*.log"))
    assert len(log_files) == 1
    content = log_files[0].read_text()
    assert '"component": "test"' in content
    assert '"level": "info"' in content
    assert '"message": "test message"' in content


def test_subscriber_writes_multiple_events(tmp_path: Path) -> None:
    subscriber = FileTraceSubscriber(log_dir=str(tmp_path))
    event1 = TraceEvent(
        component="test",
        level=TraceLevel.INFO,
        message="message 1",
        timestamp=datetime.now(UTC),
        correlation_id=uuid4(),
    )
    event2 = TraceEvent(
        component="test",
        level=TraceLevel.WARN,
        message="message 2",
        timestamp=datetime.now(UTC),
        correlation_id=uuid4(),
    )
    subscriber(event1)
    subscriber(event2)
    subscriber.close()

    log_files = list(tmp_path.glob("*.log"))
    assert len(log_files) == 1
    content = log_files[0].read_text()
    lines = content.strip().split("\n")
    assert len(lines) == 2


def test_subscriber_handles_all_levels(tmp_path: Path) -> None:
    subscriber = FileTraceSubscriber(log_dir=str(tmp_path))
    levels = [
        TraceLevel.TRACE,
        TraceLevel.DEBUG,
        TraceLevel.INFO,
        TraceLevel.WARN,
        TraceLevel.ERROR,
    ]
    for level in levels:
        event = TraceEvent(
            component="test",
            level=level,
            message=f"{level.value} message",
            timestamp=datetime.now(UTC),
            correlation_id=uuid4(),
        )
        subscriber(event)
    subscriber.close()

    log_files = list(tmp_path.glob("*.log"))
    assert len(log_files) == 1
    content = log_files[0].read_text()
    for level in levels:
        assert f'"{level.value}"' in content


def test_subscriber_correlation_id(tmp_path: Path) -> None:
    subscriber = FileTraceSubscriber(log_dir=str(tmp_path))
    correlation_id = uuid4()
    event = TraceEvent(
        component="test",
        level=TraceLevel.INFO,
        message="test message",
        timestamp=datetime.now(UTC),
        correlation_id=correlation_id,
    )
    subscriber(event)
    subscriber.close()

    log_files = list(tmp_path.glob("*.log"))
    assert len(log_files) == 1
    content = log_files[0].read_text()
    assert str(correlation_id) in content


def test_subscriber_does_not_crash_on_bad_event(tmp_path: Path) -> None:
    subscriber = FileTraceSubscriber(log_dir=str(tmp_path))
    class BadEvent:
        pass
    bad_event = BadEvent()
    subscriber(bad_event)
    subscriber.close()

    log_files = list(tmp_path.glob("*.log"))
    assert len(log_files) == 1


def test_subscriber_filename_format(tmp_path: Path) -> None:
    subscriber = FileTraceSubscriber(log_dir=str(tmp_path))
    subscriber.close()

    log_files = list(tmp_path.glob("*.log"))
    assert len(log_files) == 1
    filename = log_files[0].name
    assert filename.endswith(".log")
    parts = filename[:-4].split("_")
    assert len(parts) == 2
    assert "-" in parts[0]
    assert "-" in parts[1]


def test_subscriber_creates_dir_if_missing(tmp_path: Path) -> None:
    log_dir = tmp_path / "nested" / "logs"
    assert not log_dir.exists()
    subscriber = FileTraceSubscriber(log_dir=str(log_dir))
    assert log_dir.exists()
    subscriber.close()

    log_files = list(log_dir.glob("*.log"))
    assert len(log_files) == 1
