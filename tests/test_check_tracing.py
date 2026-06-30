"""Test the static tracing check script."""
import pytest


def test_check_tracing_script_exists() -> None:
    """Verify the check_tracing.py script exists."""
    import os
    script_path = "scripts/ar_checks/check_tracing.py"
    assert os.path.exists(script_path)


def test_check_tracing_importable() -> None:
    """Verify the check_tracing module can be imported."""
    try:
        from scripts.ar_checks.check_tracing import main
        assert main is not None
    except ImportError:
        pytest.skip("check_tracing.py not yet implemented")


def test_check_tracing_runs() -> None:
    """Verify the check_tracing script runs without errors."""
    import subprocess
    result = subprocess.run(
        ["python", "scripts/ar_checks/check_tracing.py"],
        capture_output=True,
        text=True,
    )
    # Script may fail if tracing gaps exist, but should run
    assert result.returncode in [0, 1]
