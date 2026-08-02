# Governance/Audit/weekly_review_report.py
#!/usr/bin/env python3
"""Generate weekly audit report from violation log."""
import json
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
AUDIT_LOG = PROJECT_ROOT / "Logs" / "Audit" / "violations.jsonl"
REPORT_DIR = PROJECT_ROOT / "Logs" / "Audit" / "weekly-reviews"

def main():
    week_ago = datetime.utcnow() - timedelta(days=7)
    
    # Load all violations from the past week
    violations = []
    if AUDIT_LOG.exists():
        for line in AUDIT_LOG.read_text().splitlines():
            entry = json.loads(line)
            ts = datetime.fromisoformat(entry["timestamp"].replace("Z", "+00:00"))
            if ts.replace(tzinfo=None) >= week_ago:
                violations.append(entry)
    
    # Aggregate by rule
    by_rule = Counter(v["rule_id"] for v in violations if v["decision"] == "deny")
    by_tool = Counter(v["tool"] for v in violations)
    
    report = f"""# Weekly Audit Report — {datetime.utcnow().strftime('%Y-%m-%d')}

## Summary
- Total PDP decisions this week: {len(violations)}
- Denials: {sum(1 for v in violations if v['decision'] == 'deny')}
- Allows: {sum(1 for v in violations if v['decision'] == 'allow')}

## Top 5 Most-Violated Rules (deny decisions)
"""
    for rule_id, count in by_rule.most_common(5):
        report += f"- {rule_id}: {count} denials\n"
    
    report += f"""
## Tool Call Distribution
"""
    for tool, count in by_tool.most_common():
        report += f"- {tool}: {count} calls\n"
    
    report += """
## Recommended Actions
- Rules with 0 denials this week: review for removal or downgrade to advisory
- Rules with >10 denials: review for SSOT violation or unclear statement
- New violation patterns not covered by any rule: create new Policy Card
"""
    
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_file = REPORT_DIR / f"review-{datetime.utcnow().strftime('%Y-%m-%d')}.md"
    report_file.write_text(report)
    print(f"Weekly report generated: {report_file}")

if __name__ == "__main__":
    main()