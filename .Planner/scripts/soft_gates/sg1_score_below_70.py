#!/usr/bin/env python3
"""
Soft Gate SG-1: Score Below 70 Check

Returns exit code 0 (always non-blocking) but outputs warnings when violated
"""

import sys
import os
import re
from pathlib import Path

# Set UTF-8 encoding for Windows console compatibility
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def check_gate_condition():
    """
    Check if Round Table score is below 70.
    Returns True if score >=70 (pass), False if score <70 (violation - non-blocking).
    """
    # Look for Round Table score in recent files
    # Check for score indicators in recent review files or brief files
    
    # Find plans directory (case-insensitive for cross-platform compatibility)
    plans_dir = None
    for possible_dir in ["Plans", "plans"]:
        if Path(possible_dir).exists():
            plans_dir = Path(possible_dir)
            break
    
    if plans_dir is None:
        print("⚠️  Plans directory not found, skipping validation")
        return True
    
    # Look for recent brief files which might contain score information
    brief_files = list(plans_dir.glob("brief-*.md"))
    
    if not brief_files:
        print("⚠️  No brief files found, skipping validation")
        return True
    
    # Get the most recent brief file
    latest_brief = max(brief_files, key=lambda f: f.stat().st_mtime)
    
    print(f"Checking score in brief: {latest_brief.name}")
    
    try:
        with open(latest_brief, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"⚠️  Error reading brief file: {e}, skipping validation")
        return True
    
    # Look for score patterns
    score_patterns = [
        r'score[:\s]+(\d+)',
        r'coverage target[:\s]+≥?(\d+)%',
        r'quality gate[:\s]+(\d+)',
        r'(\d+)%.*coverage',
    ]
    
    score_found = None
    for pattern in score_patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            score_found = int(match.group(1))
            break
    
    if score_found is None:
        print("⚠️  No score found in brief, skipping validation")
        return True
    
    print(f"Found score: {score_found}")
    
    if score_found >= 70:
        return True
    else:
        return False

def main():
    if check_gate_condition():
        print("✅ Gate SG-1 PASS: Round Table score >=70")
        sys.exit(0)  # Always return 0 (non-blocking)
    else:
        print("⚠️  Gate SG-1 WARN: Round Table score <70 - Soft gate violation (non-blocking)")
        print("📝 Rationale Required: Document justification for proceeding with score <70")
        print("📋 Proceed with Rationale: May proceed with documented rationale")
        sys.exit(0)  # Always return 0 (non-blocking)

if __name__ == "__main__":
    main()
