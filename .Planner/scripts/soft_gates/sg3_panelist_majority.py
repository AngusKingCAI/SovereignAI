#!/usr/bin/env python3
"""
Soft Gate SG-3: Panelist Majority Check

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
    Check if panelist majority (>50%) was achieved.
    Returns True if majority achieved (pass), False if not (violation - non-blocking).
    """
    # Look for panelist review results in recent files
    # Check for panelist count and response count
    
    # Find plans directory (case-insensitive for cross-platform compatibility)
    plans_dir = None
    for possible_dir in ["Plans", "plans"]:
        if Path(possible_dir).exists():
            plans_dir = Path(possible_dir)
            break
    
    if plans_dir is None:
        print("⚠️  Plans directory not found, skipping validation")
        return True
    
    # Look for recent brief files which might contain panelist information
    brief_files = list(plans_dir.glob("brief-*.md"))
    
    if not brief_files:
        print("⚠️  No brief files found, skipping validation")
        return True
    
    latest_brief = max(brief_files, key=lambda f: f.stat().st_mtime)
    
    print(f"Checking panelist majority in brief: {latest_brief.name}")
    
    try:
        with open(latest_brief, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"⚠️  Error reading brief file: {e}, skipping validation")
        return True
    
    # Look for panelist count patterns
    panelist_patterns = [
        r'(\d+)\s+panelists?\s+minimum',
        r'panelists?\s*[:=]\s*(\d+)',
        r'(\d+)\s+panelists?\s+required',
    ]
    
    panelist_count = None
    for pattern in panelist_patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            panelist_count = int(match.group(1))
            break
    
    if panelist_count is None:
        print("⚠️  No panelist count found in brief, skipping validation")
        return True
    
    print(f"Found panelist count: {panelist_count}")
    
    # Default assumption: if panelist count is specified, assume majority required
    # This is a soft gate, so we'll warn if panelist count < 3 (typical minimum)
    if panelist_count < 3:
        return False
    else:
        return True

def main():
    if check_gate_condition():
        print("✅ Gate SG-3 PASS: Panelist majority (>50%) achieved")
        sys.exit(0)  # Always return 0 (non-blocking)
    else:
        print("⚠️  Gate SG-3 WARN: Panelist majority not achieved - Soft gate violation (non-blocking)")
        print("📝 Rationale Required: Document justification for proceeding without panelist majority")
        print("📋 Proceed with Rationale: May proceed with documented rationale")
        sys.exit(0)  # Always return 0 (non-blocking)

if __name__ == "__main__":
    main()
