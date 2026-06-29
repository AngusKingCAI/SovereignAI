"""Pytest configuration for SovereignAI tests."""
import os


def pytest_configure():
    """Set test mode environment variable before any tests run.

    This causes memory backends to use in-memory SQLite instead of file-based
    storage, avoiding Windows file locking issues during test execution.
    """
    os.environ["SOVEREIGNAI_TEST_MODE"] = "1"
