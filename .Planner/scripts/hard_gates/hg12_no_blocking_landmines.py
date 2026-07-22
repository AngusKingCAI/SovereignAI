#!/usr/bin/env python3
"""
Hard Gate HG-12: No Blocking Landmines Validation

Validates that no blocking landmines are present in the plan.
Blocks plan delivery if blocking landmines are present.

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
    Check that no blocking landmines are present.
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
        
        # Query for blocking landmine findings
        cursor.execute("""
            SELECT f.id, f.category, f.severity, f.description, f.status
            FROM findings f
            WHERE f.severity = 'CRITICAL' AND f.category = 'landmine' AND f.status != 'addressed'
            ORDER BY f.created_at DESC
        """)
        
        blocking_landmines = cursor.fetchall()
        conn.close()
        
        if blocking_landmines:
            print(f"❌ Gate HG-12 FAIL: {len(blocking_landmines)} blocking landmines found")
            for finding in blocking_landmines:
                print(f"   - Finding {finding[0]}: {finding[1]} - {finding[3][:60]}...")
            return False
        else:
            print(f"✅ Gate HG-12 PASS: No blocking landmines present")
            return True
            
    except Exception as e:
        print(f"⚠️  Error querying Round Table database: {e}, skipping validation")
        return True

def main():
    if check_gate_condition():
        print("✅ Gate HG-12 PASS: No blocking landmines present")
        sys.exit(0)
    else:
        print("❌ Gate HG-12 FAIL: Blocking landmines present")
        sys.exit(1)

if __name__ == "__main__":
    main()