#!/usr/bin/env python3
"""
Tool: HG-5 Language Clear Validation

WHEN TO USE: Phase 4, after plan drafting, before quality gates

WHAT IT CHECKS: Plan uses clear, unambiguous language per technical writing best practices.
No vague terms, weak verbs, or ambiguous phrasing that could lead to misinterpretation.

INPUTS: None (auto-discovers latest plan in plans/ directory)

OUTPUTS:
- Exit 0: Gate HG-5 PASS: Plan language is clear and unambiguous
- Exit 1: Gate HG-5 FAIL: {list of language clarity issues}

FAILURE RECOVERY: Improve language clarity, remove vague terms, re-run this script.
Do NOT proceed to Phase 5 until exit 0.

DEPENDENCIES: plans/ directory must exist with at least one plan-*.md file
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
    Check that plan language is clear and unambiguous.
    Returns True if gate passes, False otherwise.
    """
    # Find the most recent plan file (case-insensitive for cross-platform compatibility)
    plans_dir = None
    for possible_dir in ["Plans", "plans"]:
        if Path(possible_dir).exists():
            plans_dir = Path(possible_dir)
            break
    
    if plans_dir is None:
        print("⚠️  Plans directory not found, skipping validation")
        return True
    
    # Look for plan files (excluding completed directory)
    plan_files = []
    for pattern in ["plan-*.md", "plan-*.Rev*.md"]:
        plan_files.extend(plans_dir.glob(pattern))
    
    # Filter out completed plans
    plan_files = [f for f in plan_files if "completed" not in str(f)]
    
    if not plan_files:
        print("⚠️  No plan files found, skipping validation")
        return True
    
    # Get the most recently modified plan file
    latest_plan = max(plan_files, key=lambda f: f.stat().st_mtime)
    
    print(f"Validating plan: {latest_plan.name}")
    
    try:
        with open(latest_plan, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Error reading plan file: {e}")
        return False
    
    issues = []
    
    # Check for ambiguous language patterns (per technical writing best practices)
    ambiguous_patterns = [
        r'\bmaybe\b',
        r'\bmight\b',
        r'\bcould\b(?!\s+be\b)',  # Allow "could be" but flag standalone "could"
        r'\bpossibly\b',
        r'\bperhaps\b',
        r'\bprobably\b',
        r'\bsomewhat\b',
        r'\bsomewhere\b',
        r'\bsomehow\b',
        r'\broughly\b',
        r'\bapproximately\b(?!\s+\d+)',  # Allow with numbers but flag standalone
        r'\bestimated\b(?!\s+\d+)',
    ]
    
    for pattern in ambiguous_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            issues.append(f"Found ambiguous language: {pattern} ({len(matches)} occurrences)")
    
    # Check for vague terms
    vague_patterns = [
        r'\bstuff\b',
        r'\bthings\b',
        r'\bitem\b(?!\s*\d)',  # Allow "item 1" but flag standalone "item"
        r'\bobject\b(?!\s*\w)',  # Allow specific objects but flag standalone
        r'\bmatter\b(?!\s+of)',  # Allow "matter of" but flag standalone
        r'\bthing\b',
        r'\bsomething\b',
        r'\banything\b',
        r'\beverything\b',
    ]
    
    for pattern in vague_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            issues.append(f"Found vague term: {pattern} ({len(matches)} occurrences)")
    
    # Check for weak verbs (per technical writing best practices)
    weak_verb_patterns = [
        r'\bthere\s+is\b',
        r'\bthere\s+are\b',
        r'\bthere\s+was\b',
        r'\bthere\s+were\b',
        r'\bit\s+is\b(?!\s+(important|necessary|clear|notable|worthwhile))',
        r'\boccur\b(?!\s+(in|when|where|if|after|before))',
        r'\bhappen\b(?!\s+(when|where|if|after|before|as))',
    ]
    
    for pattern in weak_verb_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            issues.append(f"Found weak verb construction: {pattern} ({len(matches)} occurrences)")
    
    # Check for empty phrases (per technical writing best practices)
    empty_phrases = [
        r'\bit\s+is\s+important\s+to\s+note\s+that\b',
        r'\bdue\s+to\s+the\s+fact\s+that\b',
        r'\bin\s+order\s+to\b',
        r'\bfor\s+the\s+purpose\s+of\b',
        r'\bin\s+the\s+event\s+that\b',
        r'\bas\s+a\s+matter\s+of\b',
        r'\bwith\s+regard\s+to\b',
        r'\bin\s+terms\s+of\b',
    ]
    
    for pattern in empty_phrases:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            issues.append(f"Found empty phrase: {pattern} ({len(matches)} occurrences)")
    
    # Check for passive voice indicators (excessive passive voice can reduce clarity)
    passive_patterns = [
        r'\bwas\s+\w+ed\b',
        r'\bwere\s+\w+ed\b',
        r'\bbeen\s+\w+ed\b',
        r'\bby\s+(?:the|a|an)\s+\w+\s+(?:is|are|was|were)\s+\w+ed\b',
    ]
    
    passive_count = sum(len(re.findall(pattern, content, re.IGNORECASE)) for pattern in passive_patterns)
    if passive_count > 10:  # Allow some passive voice but flag excessive use
        issues.append(f"Excessive passive voice detected ({passive_count} occurrences)")
    
    # Check for unclear references
    unclear_reference_patterns = [
        r'\bthe\s+(?:above|below|following|preceding)\s+(?:one|section|part)\b',
        r'\bthis\s+(?:one|thing|method|approach)\b(?!\s+is)',
        r'\bthat\s+(?:one|thing|method|approach)\b(?!\s+is)',
        r'\bthe\s+(?:same|latter|former)\b(?!\s+\w+)',
    ]
    
    for pattern in unclear_reference_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            issues.append(f"Found unclear reference: {pattern} ({len(matches)} occurrences)")
    
    # Check for non-specific quantities
    nonspecific_quantities = [
        r'\b(several|few|many|multiple|various|numerous)\b(?!\s+\w+)',
        r'\b(lots?|a\s+lot)\s+of\b',
        r'\bquite\s+a\s+(few|bit)\b',
    ]
    
    for pattern in nonspecific_quantities:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            issues.append(f"Found non-specific quantity: {pattern} ({len(matches)} occurrences)")
    
    # Calculate ambiguity score (allow some ambiguity but flag excessive)
    total_issues = len(issues)
    if total_issues > 20:  # Threshold for "excessive ambiguity"
        issues.append(f"Excessive ambiguous language detected ({total_issues} total issues)")
    
    if issues:
        print(f"❌ Gate HG-5 FAIL: Language clarity validation failed")
        for issue in issues[:10]:  # Show first 10 issues to avoid overwhelming output
            print(f"   - {issue}")
        if len(issues) > 10:
            print(f"   - ... and {len(issues) - 10} more issues")
        return False
    else:
        print(f"✅ Gate HG-5 PASS: Plan language is clear and unambiguous")
        return True

def main():
    if check_gate_condition():
        print("✅ Gate HG-5 PASS: Plan language is clear and unambiguous")
        sys.exit(0)
    else:
        print("❌ Gate HG-5 FAIL: Plan language is ambiguous or unclear")
        sys.exit(1)

if __name__ == "__main__":
    main()