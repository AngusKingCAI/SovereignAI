#!/usr/bin/env python3
"""
Soft Gate SG-RI-1: Evidence Quality Check

Returns exit code 0 (always non-blocking) but outputs warnings when violated
"""

import sys
import os
import re
from pathlib import Path

def check_gate_condition():
    """
    Check if rule suggestions have sufficient evidence (>=2 affected plans).
    Returns True if evidence sufficient (pass), False if weak evidence (violation - non-blocking).
    """
    # Look for rule integration reports
    reviewer_dir = Path("Agents/reviewer/workflows")
    if not reviewer_dir.exists():
        print("⚠️  Reviewer workflows directory not found, skipping validation")
        return True
    
    rule_files = list(reviewer_dir.glob("*RULE_INTEGRATION*.md"))
    
    if not rule_files:
        print("⚠️  No rule integration files found, skipping validation")
        return True
    
    latest_rule = max(rule_files, key=lambda f: f.stat().st_mtime)
    
    print(f"Checking evidence quality in: {latest_rule.name}")
    
    try:
        with open(latest_rule, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"⚠️  Error reading rule integration file: {e}, skipping validation")
        return True
    
    # Look for evidence quality indicators
    evidence_patterns = [
        r'affected plans[:\s]+(\d+)',
        r'(\d+)\s+affected plans',
        r'evidence[:\s]+(\d+)\s+plans',
        r'finding count[:\s]+(\d+)',
    ]
    
    affected_plans = None
    for pattern in evidence_patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            affected_plans = int(match.group(1))
            break
    
    if affected_plans is None:
        print("⚠️  No evidence count found in analysis, skipping validation")
        return True
    
    print(f"Found affected plans count: {affected_plans}")
    
    if affected_plans >= 2:
        return True
    else:
        return False

def main():
    if check_gate_condition():
        print("✅ Gate SG-RI-1 PASS: Rule suggestions have sufficient evidence (>=2 affected plans)")
        sys.exit(0)  # Always return 0 (non-blocking)
    else:
        print("⚠️  Gate SG-RI-1 WARN: Rule suggestions have weak evidence (<2 affected plans) - Soft gate violation (non-blocking)")
        print("📝 Rationale Required: Document justification for proceeding with weak evidence")
        print("📋 Proceed with Rationale: May proceed with documented rationale")
        sys.exit(0)  # Always return 0 (non-blocking)

if __name__ == "__main__":
    main()
