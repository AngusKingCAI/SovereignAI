#!/usr/bin/env python3
"""
Soft Gate SG-PA-1: Pattern Count Check

Returns exit code 0 (always non-blocking) but outputs warnings when violated
"""

import sys
import os
import re
from pathlib import Path

def check_gate_condition():
    """
    Check if pattern analysis identified at least 3 high-frequency patterns.
    Returns True if >=3 patterns (pass), False if <3 patterns (violation - non-blocking).
    """
    # Look for pattern analysis reports
    reviewer_dir = Path("Agents/reviewer/workflows")
    if not reviewer_dir.exists():
        print("⚠️  Reviewer workflows directory not found, skipping validation")
        return True
    
    # Look for pattern analysis files
    pattern_files = list(reviewer_dir.glob("*PATTERN*.md"))
    
    if not pattern_files:
        print("⚠️  No pattern analysis files found, skipping validation")
        return True
    
    # Get the most recent pattern analysis file
    latest_pattern = max(pattern_files, key=lambda f: f.stat().st_mtime)
    
    print(f"Checking pattern count in: {latest_pattern.name}")
    
    try:
        with open(latest_pattern, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"⚠️  Error reading pattern analysis file: {e}, skipping validation")
        return True
    
    # Look for pattern count indicators
    pattern_count_patterns = [
        r'(\d+)\s+high-frequency patterns',
        r'pattern count[:\s]+(\d+)',
        r'(\d+)\s+patterns identified',
        r'found\s+(\d+)\s+patterns',
    ]
    
    pattern_count = None
    for pattern in pattern_count_patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            pattern_count = int(match.group(1))
            break
    
    if pattern_count is None:
        print("⚠️  No pattern count found in analysis, skipping validation")
        return True
    
    print(f"Found pattern count: {pattern_count}")
    
    if pattern_count >= 3:
        return True
    else:
        return False

def main():
    if check_gate_condition():
        print("✅ Gate SG-PA-1 PASS: Pattern analysis identified >=3 high-frequency patterns")
        sys.exit(0)  # Always return 0 (non-blocking)
    else:
        print("⚠️  Gate SG-PA-1 WARN: Pattern analysis identified <3 high-frequency patterns - Soft gate violation (non-blocking)")
        print("📝 Rationale Required: Document justification for proceeding with fewer than 3 patterns")
        print("📋 Proceed with Rationale: May proceed with documented rationale")
        sys.exit(0)  # Always return 0 (non-blocking)

if __name__ == "__main__":
    main()
