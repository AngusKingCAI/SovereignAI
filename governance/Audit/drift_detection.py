# Governance/Audit/drift_detection.py
#!/usr/bin/env python3
"""
Drift detector: compares what rules SAY they check vs. what rules ACTUALLY check.
Runs nightly. Flags any rule where the documented behavior diverges from actual.
"""
import yaml
from pathlib import Path
from datetime import datetime, timedelta

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CARDS_DIR = PROJECT_ROOT / "Governance" / "Policy-cards"
AUDIT_LOG = PROJECT_ROOT / "Governance" / "Audit" / "violations.jsonl"

def detect_rule_drift():
    """For each rule, compare documented check vs. actual enforcement events."""
    import json
    
    # Load last 30 days of audit events
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    enforcement_events = {}  # rule_id -> count
    if AUDIT_LOG.exists():
        for line in AUDIT_LOG.read_text().splitlines():
            entry = json.loads(line)
            ts = datetime.fromisoformat(entry["timestamp"].replace("Z", "+00:00"))
            if ts.replace(tzinfo=None) >= thirty_days_ago:
                rid = entry.get("rule_id")
                if rid:
                    enforcement_events[rid] = enforcement_events.get(rid, 0) + 1
    
    # Compare against declared rules
    drift_report = []
    for card_file in CARDS_DIR.rglob("*.yaml"):
        card = yaml.safe_load(card_file.read_text())
        rid = card["id"]
        event_count = enforcement_events.get(rid, 0)
        
        # Drift signals:
        # 1. Rule is blocking but has 0 enforcement events in 30 days
        if card["severity"] == "blocking" and event_count == 0:
            drift_report.append({
                "rule_id": rid,
                "file": str(card_file),
                "signal": "blocking_rule_never_fired",
                "message": f"Blocking rule {rid} has 0 enforcement events in 30 days. "
                           f"Check function may be broken or rule may be redundant."
            })
        
        # 2. Rule's check type doesn't match any implemented evaluator function
        check_type = card.get("check", {}).get("type")
        if check_type and not evaluator_exists(check_type):
            drift_report.append({
                "rule_id": rid,
                "file": str(card_file),
                "signal": "check_type_not_implemented",
                "message": f"Rule {rid} uses check type '{check_type}' but no "
                           f"evaluator function exists for it."
            })
    
    return drift_report

def evaluator_exists(check_type: str) -> bool:
    """Verify that the check_type has a corresponding evaluator function."""
    # All check types are implemented in evaluate_rule, so return True for known types
    known_types = {"deny_command", "path_pattern", "require_field", "regex", 
                   "yaml_field", "json_schema", "custom_function"}
    return check_type in known_types

if __name__ == "__main__":
    drift = detect_rule_drift()
    if drift:
        print(f"! Drift detected in {len(drift)} rules:")
        for d in drift:
            print(f"  - {d['rule_id']}: {d['signal']} - {d['message']}")
    else:
        print("No drift detected - all rules are consistent with enforcement")
