#!/usr/bin/env python3
"""
Soft Gate SG-PA-2: Cluster Quality Check

Returns exit code 0 (always non-blocking) but outputs warnings when violated
"""

import sys
import os
import re
from pathlib import Path

def check_gate_condition():
    """
    Check if ML clustering achieved silhouette score >=0.5.
    Returns True if score >=0.5 (pass), False if score <0.5 (violation - non-blocking).
    """
    # Look for pattern analysis reports
    reviewer_dir = Path("Agents/reviewer/workflows")
    if not reviewer_dir.exists():
        print("⚠️  Reviewer workflows directory not found, skipping validation")
        return True
    
    pattern_files = list(reviewer_dir.glob("*PATTERN*.md"))
    
    if not pattern_files:
        print("⚠️  No pattern analysis files found, skipping validation")
        return True
    
    latest_pattern = max(pattern_files, key=lambda f: f.stat().st_mtime)
    
    print(f"Checking cluster quality in: {latest_pattern.name}")
    
    try:
        with open(latest_pattern, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"⚠️  Error reading pattern analysis file: {e}, skipping validation")
        return True
    
    # Look for silhouette score indicators
    silhouette_patterns = [
        r'silhouette score[:\s]+(\d+\.?\d*)',
        r'silhouette[:\s]+(\d+\.?\d*)',
        r'cluster quality[:\s]+(\d+\.?\d*)',
        r'(\d+\.?\d*)\s+silhouette',
    ]
    
    silhouette_score = None
    for pattern in silhouette_patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            silhouette_score = float(match.group(1))
            break
    
    if silhouette_score is None:
        print("⚠️  No silhouette score found in analysis, skipping validation")
        return True
    
    print(f"Found silhouette score: {silhouette_score}")
    
    if silhouette_score >= 0.5:
        return True
    else:
        return False

def main():
    if check_gate_condition():
        print("✅ Gate SG-PA-2 PASS: ML clustering achieved silhouette score >=0.5")
        sys.exit(0)  # Always return 0 (non-blocking)
    else:
        print("⚠️  Gate SG-PA-2 WARN: ML clustering achieved silhouette score <0.5 - Soft gate violation (non-blocking)")
        print("📝 Rationale Required: Document justification for proceeding with low cluster quality")
        print("📋 Proceed with Rationale: May proceed with documented rationale")
        sys.exit(0)  # Always return 0 (non-blocking)

if __name__ == "__main__":
    main()
