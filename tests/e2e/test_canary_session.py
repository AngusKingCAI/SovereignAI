# tests/e2e/test_canary_session.py
"""
End-to-end canary session: runs a scripted sequence of tool calls
through the actual hook system and verifies outcomes.
Runs nightly via GitHub Actions scheduled workflow.
"""
import subprocess
import pytest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Each canary case is: (name, tool_call, expected_exit_code, expected_stdout_contains)
CANARY_CASES = [
    ("destructive_rm_rf", {"tool": "exec", "input": {"command": "rm -rf tests/"}}, 2, "BLOCKED"),
    ("safe_rm", {"tool": "exec", "input": {"command": "rm file.txt"}}, 0, None),
    ("git_force_push", {"tool": "exec", "input": {"command": "git push origin main --force"}}, 2, "BLOCKED"),
    ("safe_ls", {"tool": "exec", "input": {"command": "ls -la"}}, 0, None),
]

@pytest.mark.parametrize("name,tool_call,expected_exit,expected_stdout", CANARY_CASES)
def test_canary(name, tool_call, expected_exit, expected_stdout):
    """Each canary case must produce the expected outcome."""
    import os
    import json
    
    env = {**os.environ, "ACTIVE_AGENT": "architect"}
    
    result = subprocess.run(
        ["python", str(PROJECT_ROOT / "scripts" / "enforcement" / "pre_tool_pdp.py")],
        input=json.dumps(tool_call),
        capture_output=True,
        text=True,
        timeout=10,
        cwd=str(PROJECT_ROOT),
        env=env
    )
    assert result.returncode == expected_exit, \
        f"{name}: expected exit {expected_exit}, got {result.returncode}. stdout: {result.stdout}"
    if expected_stdout:
        assert expected_stdout in result.stdout, \
            f"{name}: expected '{expected_stdout}' in stdout, got: {result.stdout}"
