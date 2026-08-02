# Governance/Tests/integration/test_pdp_integration.py
import json
import subprocess
import pytest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
PDP_SCRIPT = PROJECT_ROOT / "Governance" / "GovernanceScripts" / "Enforcement" / "pre_tool_pdp.py"

def run_pdp(tool_call: dict) -> dict:
    """Run the PDP script with a given tool call and return its output."""
    import os
    # Set ACTIVE_AGENT environment variable
    env = {**os.environ, "ACTIVE_AGENT": "architect"}
    
    result = subprocess.run(
        ["python", str(PDP_SCRIPT)],
        input=json.dumps(tool_call),
        capture_output=True,
        text=True,
        timeout=10,
        cwd=str(PROJECT_ROOT),
        env=env
    )
    return {
        "exit_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }

def test_destructive_command_blocked():
    """rm -rf must be denied by SHR-01."""
    result = run_pdp({"tool": "exec", "input": {"command": "rm -rf tests/"}})
    assert result["exit_code"] == 2, f"Expected exit 2 (deny), got {result['exit_code']}"
    assert "BLOCKED" in result["stdout"] or "deny" in result["stdout"]

def test_non_destructive_rm_allowed():
    """rm without -rf must be allowed."""
    result = run_pdp({"tool": "exec", "input": {"command": "rm single_file.txt"}})
    assert result["exit_code"] == 0, f"Expected exit 0 (allow), got {result['exit_code']}"

def test_git_force_push_blocked():
    """git push --force must be denied."""
    result = run_pdp({"tool": "exec", "input": {"command": "git push origin main --force"}})
    assert result["exit_code"] == 2, f"Expected exit 2 (deny), got {result['exit_code']}"

def test_safe_command_allowed():
    """Safe commands like ls should be allowed."""
    result = run_pdp({"tool": "exec", "input": {"command": "ls -la"}})
    assert result["exit_code"] == 0, f"Expected exit 0 (allow), got {result['exit_code']}"

def test_malformed_stdin_does_not_crash():
    """Malformed stdin must not crash the PDP — fail-closed when safety rules active."""
    import os
    env = {**os.environ, "ACTIVE_AGENT": "architect"}
    result = subprocess.run(
        ["python", str(PDP_SCRIPT)],
        input="this is not json {{{",
        capture_output=True,
        text=True,
        timeout=10,
        cwd=str(PROJECT_ROOT),
        env=env
    )
    # Should fail-closed (exit 2) since safety-tier rules are active (SHARED-S01)
    assert result.returncode == 2, "PDP must fail-closed on malformed stdin when safety rules active"
    assert "BLOCKED" in result.stdout, "Malformed stdin should result in deny when safety rules active"

def test_pdp_completes_within_timeout():
    """PDP must return within 5 seconds (the hook timeout)."""
    import time
    start = time.monotonic()
    run_pdp({"tool": "exec", "input": {"command": "ls"}})
    elapsed = time.monotonic() - start
    assert elapsed < 5.0, f"PDP took {elapsed:.2f}s, must be <5s"
