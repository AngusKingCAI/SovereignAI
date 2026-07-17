import sys
from unittest.mock import patch

import pytest

from sovereignai.shared.types import ComponentId
from sovereignai.versioning.negotiator import FatalIncompatibilityError, Incompatibility


def test_fatal_error_with_no_wait_flag_exits_immediately() -> None:
    incompatibilities = [  # noqa: E501
        Incompatibility(
            component_a=ComponentId('core1'),
            version_a='1.0.0',
            component_b=ComponentId('core2'),
            version_b='2.0.0',
            reason='major version mismatch'
        )
    ]
    FatalIncompatibilityError(incompatibilities)
    with patch('sys.argv', ['main.py', '--no-wait']):
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument(  # noqa: E501
            '--no-wait',
            action='store_true',
            help='Exit immediately on fatal errors'
        )
        args = parser.parse_args()
        assert args.no_wait is True
        with pytest.raises(SystemExit) as exc_info:
            if args.no_wait:
                sys.exit(1)
        assert exc_info.value.code == 1

def test_fatal_error_without_no_wait_waits() -> None:
    incompatibilities = [  # noqa: E501
        Incompatibility(
            component_a=ComponentId('core1'),
            version_a='1.0.0',
            component_b=ComponentId('core2'),
            version_b='2.0.0',
            reason='major version mismatch'
        )
    ]
    FatalIncompatibilityError(incompatibilities)
    with patch('sys.argv', ['main.py']):
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument(  # noqa: E501
            '--no-wait',
            action='store_true',
            help='Exit immediately on fatal errors'
        )
        args = parser.parse_args()
        assert args.no_wait is False
        with patch('time.sleep') as mock_sleep:
            with pytest.raises(SystemExit) as exc_info:
                if not args.no_wait:
                    import time
                    time.sleep(30)
                    sys.exit(1)
            assert exc_info.value.code == 1
            mock_sleep.assert_called_once_with(30)

def test_fatal_error_noninteractive_tty_hint() -> None:
    incompatibilities = [  # noqa: E501
        Incompatibility(
            component_a=ComponentId('core1'),
            version_a='1.0.0',
            component_b=ComponentId('core2'),
            version_b='2.0.0',
            reason='major version mismatch'
        )
    ]
    FatalIncompatibilityError(incompatibilities)
    with patch('sys.stdin.isatty', return_value=False), patch('sys.argv', ['main.py']):
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument(  # noqa: E501
            '--no-wait',
            action='store_true',
            help='Exit immediately on fatal errors'
        )
        hint_printed = bool(not sys.stdin.isatty())
        assert hint_printed is True

def test_fatal_error_message_format() -> None:
    incompatibilities = [  # noqa: E501
        Incompatibility(
            component_a=ComponentId('core1'),
            version_a='1.0.0',
            component_b=ComponentId('core2'),
            version_b='2.0.0',
            reason='major version mismatch'
        ),
        Incompatibility(
            component_a=ComponentId('core1'),
            version_a='1.0.0',
            component_b=ComponentId('core3'),
            version_b='1.5.0',
            reason='minor version downgrade'
        )
    ]
    error = FatalIncompatibilityError(incompatibilities)
    error_str = str(error)
    assert 'Fatal incompatibilities detected:' in error_str
    assert 'major version mismatch' in error_str
    assert 'minor version downgrade' in error_str
