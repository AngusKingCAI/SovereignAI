"""DEBT-7 verification spike tests for SSE cookie auth capability."""

from pathlib import Path

import pytest


class TestSpikeDecisionRecordedInLog:
    """Test that spike decision is recorded in execution log."""

    def test_spike_decision_recorded_in_log(self, request: pytest.FixtureRequest) -> None:
        """Test that spike probe writes outcome to build/execution.log.

        This test verifies that the session-scoped spike_probe fixture
        correctly appends the SPIKE_OUTCOME to build/execution.log.
        """
        build_dir = Path("build")
        log_path = build_dir / "execution.log"

        # Check that log file exists
        assert log_path.exists(), f"Execution log not found at {log_path}"

        # Read log file and check for SPIKE_OUTCOME entry
        log_content = log_path.read_text()

        # Should contain SPIKE_OUTCOME line
        assert "SPIKE_OUTCOME:" in log_content, "SPIKE_OUTCOME not found in execution log"

        # Extract the spike outcome line
        spike_lines = [line for line in log_content.split("\n") if "SPIKE_OUTCOME:" in line]
        assert len(spike_lines) > 0, "No SPIKE_OUTCOME lines found"

        # Parse the latest spike outcome
        latest_line = spike_lines[-1]
        assert "SSE_OK" in latest_line or "SSE_FAIL" in latest_line, \
            f"Invalid SPIKE_OUTCOME format: {latest_line}"

        # Verify timestamp format
        assert "timestamp=" in latest_line, f"No timestamp in SPIKE_OUTCOME: {latest_line}"

        # Check that stash was also populated
        assert hasattr(request.config, "stash"), "pytest.Stash not available"

        # The spike_probe fixture uses string key "debt7_spike_result"
        spike_key = "debt7_spike_result"

        assert spike_key in request.config.stash, \
            "Spike result not found in pytest stash"

        spike_result = request.config.stash[spike_key]  # type: ignore[index]
        assert spike_result in ["SSE_OK", "SSE_FAIL"], \
            f"Invalid spike result in stash: {spike_result}"

        # Verify log and stash match
        if spike_result == "SSE_OK":
            assert "SSE_OK" in latest_line, "Log says SSE_FAIL but stash says SSE_OK"
        else:
            assert "SSE_FAIL" in latest_line, "Log says SSE_OK but stash says SSE_FAIL"
