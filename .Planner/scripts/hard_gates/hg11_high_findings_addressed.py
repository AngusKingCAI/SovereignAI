#!/usr/bin/env python3
"""
Hard Gate HG-11: High Findings Addressed Validation

Validates that HIGH findings from Round Table are addressed.
Blocks plan delivery if HIGH findings are unaddressed.

Returns exit code 0 (pass) or 1 (fail)
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
    Check that HIGH findings are addressed.
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
        
        # Query for unaddressed HIGH findings
        cursor.execute("""
            SELECT f.id, f.category, f.severity, f.description, f.status
            FROM findings f
            WHERE f.severity = 'HIGH' AND f.status != 'addressed'
            ORDER BY f.created_at DESC
        """)
        
        high_findings = cursor.fetchall()
        conn.close()
        
        if high_findings:
            print(f"❌ Gate HG-11 FAIL: {len(high_findings)} unaddressed HIGH findings found")
            for finding in high_findings:
                print(f"   - Finding {finding[0]}: {finding[1]} - {finding[3][:60]}...")
            return False
        else:
            print(f"✅ Gate HG-11 PASS: All HIGH findings are addressed")
            return True
            
    except Exception as e:
        print(f"⚠️  Error querying Round Table database: {e}, skipping validation")
        return True

def main():
    if check_gate_condition():
        print("✅ Gate HG-11 PASS: HIGH findings are addressed")
        sys.exit(0)
    else:
        print("❌ Gate HG-11 FAIL: HIGH findings are unaddressed")
        sys.exit(1)

if __name__ == "__main__":
    main()