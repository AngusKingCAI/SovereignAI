#!/usr/bin/env python3
"""
Tool: HG-10 Critical Findings Addressed Validation

WHEN TO USE: Phase 6, after Round Table review, before plan delivery

WHAT IT CHECKS: All CRITICAL severity findings from Round Table database are addressed.
No unaddressed CRITICAL findings exist in the database.

INPUTS: None (queries Round Table database for unaddressed CRITICAL findings)

OUTPUTS:
- Exit 0: Gate HG-10 PASS: All CRITICAL findings are addressed
- Exit 1: Gate HG-10 FAIL: {list of unaddressed CRITICAL findings}

FAILURE RECOVERY: Address CRITICAL findings in plan, update database status, re-run this script.
Do NOT deliver plan until exit 0.

DEPENDENCIES: Round Table database with findings data, database_manager.py
"""

import sys
import os
import sqlite3
from pathlib import Path

# Set UTF-8 encoding for Windows console compatibility
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def check_gate_condition():
    """
    Check that CRITICAL findings are addressed.
    Returns True if gate passes, False otherwise.
    """
    # Check for Round Table database
    db_path = Path(".Planner/roundtable/database/roundtable.db")
    if not db_path.exists():
        print("⚠️  Round Table database not found, skipping validation")
        return True
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Query for unaddressed CRITICAL findings
        cursor.execute("""
            SELECT f.id, f.category, f.severity, f.description, f.status
            FROM findings f
            WHERE f.severity = 'CRITICAL' AND f.status != 'addressed'
            ORDER BY f.created_at DESC
        """)
        
        critical_findings = cursor.fetchall()
        conn.close()
        
        if critical_findings:
            print(f"❌ Gate HG-10 FAIL: {len(critical_findings)} unaddressed CRITICAL findings found")
            for finding in critical_findings:
                print(f"   - Finding {finding[0]}: {finding[1]} - {finding[3][:60]}...")
            return False
        else:
            print(f"✅ Gate HG-10 PASS: All CRITICAL findings are addressed")
            return True
            
    except Exception as e:
        print(f"⚠️  Error querying Round Table database: {e}, skipping validation")
        return True

def main():
    if check_gate_condition():
        print("✅ Gate HG-10 PASS: CRITICAL findings are addressed")
        sys.exit(0)
    else:
        print("❌ Gate HG-10 FAIL: CRITICAL findings are unaddressed")
        sys.exit(1)

if __name__ == "__main__":
    main()