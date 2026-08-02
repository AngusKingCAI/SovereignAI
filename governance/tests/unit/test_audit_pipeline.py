# Governance/Tests/unit/test_audit_pipeline.py
import json
import pytest
from pathlib import Path
from datetime import datetime, timedelta

PROJECT_ROOT = Path(__file__).resolve().parent.parent
AUDIT_LOG = PROJECT_ROOT / "Governance" / "Audit" / "violations.jsonl"

def test_log_decision_writes_valid_jsonl(tmp_path):
    """Test that log_decision writes valid JSONL entries."""
    import sys
    sys.path.insert(0, str(PROJECT_ROOT / "Governance" / "GovernanceScripts"))
    from Enforcement.pre_tool_pdp import log_decision
    
    # Override AUDIT_LOG to use temp directory
    import Enforcement.pre_tool_pdp as pdp_module
    original_log = pdp_module.AUDIT_LOG
    pdp_module.AUDIT_LOG = tmp_path / "test_violations.jsonl"
    
    try:
        tool_call = {"tool": "exec", "input": {"command": "ls"}}
        result = {"decision": "allow", "rule_id": "TEST-001", "reason": ""}
        
        log_decision(tool_call, result)
        
        # Verify file was created and contains valid JSON
        assert pdp_module.AUDIT_LOG.exists()
        lines = pdp_module.AUDIT_LOG.read_text().splitlines()
        assert len(lines) == 1
        
        entry = json.loads(lines[0])
        assert entry["decision"] == "allow"
        assert entry["rule_id"] == "TEST-001"
        assert "timestamp" in entry
    finally:
        pdp_module.AUDIT_LOG = original_log

def test_weekly_report_aggregates_correctly(tmp_path):
    """Test that weekly report aggregates deny counts by rule ID."""
    import sys
    sys.path.insert(0, str(PROJECT_ROOT / "Governance" / "GovernanceScripts"))
    from Audit.weekly_review_report import REPORT_DIR, AUDIT_LOG
    
    # Override paths
    import Audit.weekly_review_report as report_module
    original_report_dir = report_module.REPORT_DIR
    original_audit_log = report_module.AUDIT_LOG
    
    report_module.REPORT_DIR = tmp_path / "weekly-reviews"
    report_module.AUDIT_LOG = tmp_path / "violations.jsonl"
    
    try:
        # Create test violation log
        violations = [
            {"timestamp": datetime.utcnow().isoformat() + "Z", "tool": "exec", "input_summary": "rm -rf", "decision": "deny", "rule_id": "SHR-01", "reason": "destructive"},
            {"timestamp": datetime.utcnow().isoformat() + "Z", "tool": "exec", "input_summary": "rm -rf", "decision": "deny", "rule_id": "SHR-01", "reason": "destructive"},
            {"timestamp": datetime.utcnow().isoformat() + "Z", "tool": "write", "input_summary": "file.txt", "decision": "allow", "rule_id": "SHR-04", "reason": ""},
        ]
        
        report_module.AUDIT_LOG.write_text("\n".join(json.dumps(v) for v in violations))
        
        # Run weekly report
        report_module.main()
        
        # Verify report was created
        assert report_module.REPORT_DIR.exists()
        report_files = list(report_module.REPORT_DIR.glob("*.md"))
        assert len(report_files) == 1
        
        report_content = report_files[0].read_text()
        assert "SHR-01: 2 denials" in report_content
        assert "Total PDP decisions this week: 3" in report_content
    finally:
        report_module.REPORT_DIR = original_report_dir
        report_module.AUDIT_LOG = original_audit_log

def test_weekly_report_handles_empty_log(tmp_path):
    """Test that weekly report handles empty violation log gracefully."""
    import sys
    sys.path.insert(0, str(PROJECT_ROOT / "Governance" / "GovernanceScripts"))
    from Audit.weekly_review_report import REPORT_DIR, AUDIT_LOG
    
    import Audit.weekly_review_report as report_module
    original_report_dir = report_module.REPORT_DIR
    original_audit_log = report_module.AUDIT_LOG
    
    report_module.REPORT_DIR = tmp_path / "weekly-reviews"
    report_module.AUDIT_LOG = tmp_path / "violations.jsonl"
    
    try:
        # Create empty log
        report_module.AUDIT_LOG.write_text("")
        
        # Should not crash
        report_module.main()
        
        # Verify report was created
        assert report_module.REPORT_DIR.exists()
        report_files = list(report_module.REPORT_DIR.glob("*.md"))
        assert len(report_files) == 1
    finally:
        report_module.REPORT_DIR = original_report_dir
        report_module.AUDIT_LOG = original_audit_log
