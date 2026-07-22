#!/usr/bin/env python3
"""
Hard Gate HG-6: Landmines Screened Validation

Validates that blocking landmines are addressed.
Blocks plan delivery if blocking landmines are present.

Returns exit code 0 (pass) or 1 (fail)
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
    Check that blocking landmines are addressed.
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
    
    # Define governance landmines based on common software governance issues
    security_landmines = [
        r'\bhardcoded\s+(?:password|key|secret|token)\b',
        r'\bSQL\s+injection\b',
        r'\bXSS\b(?!\s+attack)',  # Allow references but flag potential vulnerabilities
        r'\bCSRF\b(?!\s+protection)',
        r'\bplaintext\s+(?:password|credential|secret)\b',
        r'\bdisable\s+(?:SSL|TLS|HTTPS|security)\b',
        r'\b(?:admin|root)\s+password\s*=\s*["\']\w+["\']',
        r'eval\s*\(\s*\$?\w+\s*\)',  # PHP eval() patterns
        r'exec\s*\(\s*\$?\w+\s*\)',  # Python exec() patterns
    ]
    
    for pattern in security_landmines:
        if re.search(pattern, content, re.IGNORECASE):
            issues.append(f"Security landmine detected: {pattern}")
    
    # Architecture violation landmines
    architecture_landmines = [
        r'\b(?:circular|cyclic)\s+dependency\b',
        r'\btight\s+coupling\b',
        r'\bgod\s+(?:object|class|method)\b',
        r'\bspaghetti\s+code\b',
        r'\b(?:big|monolithic)\s+ball\s+of\s+mud\b',
        r'\b(?:golden|silver)\s+hammer\b',
        r'\b(?:copy|paste)\s+programming\b',
        r'\bmagic\s+(?:number|string|value)\b',
    ]
    
    for pattern in architecture_landmines:
        if re.search(pattern, content, re.IGNORECASE):
            issues.append(f"Architecture landmine detected: {pattern}")
    
    # Process violation landmines
    process_landmines = [
        r'\b(?:no|without)\s+(?:testing|tests?|verification)\b',
        r'\bskip\s+(?:tests?|testing|validation)\b',
        r'\b(?:manually|manual)\s+(?:deploy|deployment)\b',
        r'\b(?:direct|production)\s+(?:database|db)\s+access\b',
        r'\b(?:delete|drop|remove)\s+(?:all|everything|production)\b',
        r'\b(?:force|override)\s+(?:push|deploy|merge)\b',
    ]
    
    for pattern in process_landmines:
        if re.search(pattern, content, re.IGNORECASE):
            issues.append(f"Process landmine detected: {pattern}")
    
    # Compliance violation landmines
    compliance_landmines = [
        r'\b(?:skip|ignore|bypass)\s+(?:compliance|audit|review|check)\b',
        r'\b(?:workaround|hack|temporary)\s+(?:fix|solution)\b(?!\s+with\s+plan)',
        r'\btechnical\s+debt\b(?!\s+acknowledged|documented)',
        r'\b(?:without|no)\s+(?:approval|review|sign-off)\b',
        r'\b(?:break|violate|ignore)\s+(?:rule|policy|standard|guideline)\b',
    ]
    
    for pattern in compliance_landmines:
        if re.search(pattern, content, re.IGNORECASE):
            issues.append(f"Compliance landmine detected: {pattern}")
    
    # Documentation violation landmines
    documentation_landmines = [
        r'\b(?:no|without|missing)\s+(?:documentation|docs?|comments)\b',
        r'\b(?:TODO|FIXME|HACK|XXX)\b(?!\s*:)',  # Allow TODO: but flag standalone
        r'\b(?:un)?documented\s+(?:API|function|method|behavior)\b',
        r'\b(?:legacy|deprecated)\s+(?:code|function|method)\b(?!\s+with\s+plan)',
    ]
    
    for pattern in documentation_landmines:
        if re.search(pattern, content, re.IGNORECASE):
            issues.append(f"Documentation landmine detected: {pattern}")
    
    # Anti-pattern landmines
    antipattern_landmines = [
        r'\b(?:reinvent|rewrite)\s+the\s+wheel\b',
        r'\b(?:roll\s+your\s+own)\s+(?:crypto|security|auth)\b',
        r'\b(?:manual|hand)\s+(?:SQL|string)\s+(?:construction|building)\b',
        r'\b(?:global|static)\s+state\b(?!\s+with\s+justification)',
        r'\b(?:shared|mutable)\s+state\b(?!\s+with\s+synchronization)',
    ]
    
    for pattern in antipattern_landmines:
        if re.search(pattern, content, re.IGNORECASE):
            issues.append(f"Anti-pattern landmine detected: {pattern}")
    
    # Check for explicit mentions of "landmine" (self-referential)
    landmine_mentions = re.findall(r'\blandmine\b', content, re.IGNORECASE)
    if landmine_mentions:
        issues.append(f"Self-referential landmine mentions found ({len(landmine_mentions)} occurrences)")
    
    # Check for governance rule violations based on PR rules
    governance_violations = [
        r'PR[1-9]+(?!\s*(PASS|FAIL|comply))',  # PR rule references without compliance
        r'GR[1-5]+(?!\s*(PASS|FAIL|comply))',  # GR rule references without compliance
        r'gate\s+(?!pass|fail|block)',  # Gate references without compliance status
    ]
    
    for pattern in governance_violations:
        if re.search(pattern, content, re.IGNORECASE):
            issues.append(f"Governance violation detected: {pattern}")
    
    if issues:
        print(f"❌ Gate HG-6 FAIL: Governance landmines detected")
        for issue in issues[:10]:  # Show first 10 issues to avoid overwhelming output
            print(f"   - {issue}")
        if len(issues) > 10:
            print(f"   - ... and {len(issues) - 10} more landmines")
        return False
    else:
        print(f"✅ Gate HG-6 PASS: No blocking governance landmines detected")
        return True

def main():
    if check_gate_condition():
        print("✅ Gate HG-6 PASS: Blocking landmines are addressed")
        sys.exit(0)
    else:
        print("❌ Gate HG-6 FAIL: Blocking landmines are present")
        sys.exit(1)

if __name__ == "__main__":
    main()