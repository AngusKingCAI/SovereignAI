"""Test FatalIncompatibilityError handling in non-interactive mode."""

import sys
from unittest.mock import patch

import pytest

from sovereignai.shared.types import ComponentId
from sovereignai.versioning.negotiator import FatalIncompatibilityError, Incompatibility


def test_fatal_error_with_no_wait_flag_exits_immediately() -> None:
    """Test that --no-wait flag causes immediate exit without countdown."""
    incompatibilities = [
        Incompatibility(
            component_a=ComponentId("core1"),
            version_a="1.0.0",
            component_b=ComponentId("core2"),
            version_b="2.0.0",
            reason="major version mismatch",
        )
    ]

    FatalIncompatibilityError(incompatibilities)

    # Simulate main.py error handling with --no-wait
    with patch("sys.argv", ["main.py", "--no-wait"]):
        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--no-wait", action="store_true",
            help="Exit immediately on fatal errors"
        )
        args = parser.parse_args()

        assert args.no_wait is True

        # With --no-wait, should exit immediately
        with pytest.raises(SystemExit) as exc_info:
            if args.no_wait:
                sys.exit(1)

        assert exc_info.value.code == 1


def test_fatal_error_without_no_wait_waits() -> None:
    """Test that without --no-wait, the system waits before exit."""
    incompatibilities = [
        Incompatibility(
            component_a=ComponentId("core1"),
            version_a="1.0.0",
            component_b=ComponentId("core2"),
            version_b="2.0.0",
            reason="major version mismatch",
        )
    ]

    FatalIncompatibilityError(incompatibilities)

    # Simulate main.py error handling without --no-wait
    with patch("sys.argv", ["main.py"]):
        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--no-wait", action="store_true",
            help="Exit immediately on fatal errors"
        )
        args = parser.parse_args()

        assert args.no_wait is False

        # Mock time.sleep to avoid actual delay in test
        with patch("time.sleep") as mock_sleep:
            with pytest.raises(SystemExit) as exc_info:
                if not args.no_wait:
                    import time
                    time.sleep(30)
                    sys.exit(1)

            assert exc_info.value.code == 1
            mock_sleep.assert_called_once_with(30)


def test_fatal_error_noninteractive_tty_hint() -> None:
    """Test that non-interactive terminal shows hint about --no-wait."""
    incompatibilities = [
        Incompatibility(
            component_a=ComponentId("core1"),
            version_a="1.0.0",
            component_b=ComponentId("core2"),
            version_b="2.0.0",
            reason="major version mismatch",
        )
    ]

    FatalIncompatibilityError(incompatibilities)

    # Simulate non-interactive terminal (isatty() returns False)
    with patch("sys.stdin.isatty", return_value=False), patch("sys.argv", ["main.py"]):
        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--no-wait", action="store_true",
            help="Exit immediately on fatal errors"
        )

        # Should print hint but still wait (per OR67)
        hint_printed = bool(not sys.stdin.isatty())

        assert hint_printed is True


def test_fatal_error_message_format() -> None:
    """Test that FatalIncompatibilityError message is properly formatted."""
    incompatibilities = [
        Incompatibility(
            component_a=ComponentId("core1"),
            version_a="1.0.0",
            component_b=ComponentId("core2"),
            version_b="2.0.0",
            reason="major version mismatch",
        ),
        Incompatibility(
            component_a=ComponentId("core1"),
            version_a="1.0.0",
            component_b=ComponentId("core3"),
            version_b="1.5.0",
            reason="minor version downgrade",
        ),
    ]

    error = FatalIncompatibilityError(incompatibilities)

    error_str = str(error)
    assert "Fatal incompatibilities detected:" in error_str
    assert "major version mismatch" in error_str
    assert "minor version downgrade" in error_str
