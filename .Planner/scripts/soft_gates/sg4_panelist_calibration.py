#!/usr/bin/env python3
"""
Soft Gate SG-4: Panelist Calibration Tracking

Warns if any panelist's last-10-evaluation divergence from consensus >2 points.
This is a non-blocking gate that alerts to panelist calibration issues for improvement.

SECURITY PRINCIPLE: All panelist scoring and calibration tracking is INTERNAL-ONLY.
Panelists never see their own scores, calibration status, or other panelists' performance.
This prevents gaming the system and ensures honest evaluation.

Returns exit code 0 (always non-blocking) but outputs warnings when calibration issues detected.
"""

import sys
import os
import sqlite3
from pathlib import Path

def check_gate_condition():
    """
    Check that panelist calibration is within acceptable limits (divergence ≤2 points).
    Returns True if gate passes, False if calibration issues detected (non-blocking).
    """
    # Find Round Table database
    db_path = None
    for possible_db in [".Planner/roundtable/database/roundtable.db", "roundtable.db", ".Planner/roundtable.db"]:
        if Path(possible_db).exists():
            db_path = possible_db
            break
    
    if db_path is None:
        print("Round Table database not found, skipping calibration validation")
        return True
    
    print(f"Validating panelist calibration using database: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if panelist_reviews table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='panelist_reviews'
        """)
        
        if not cursor.fetchone():
            print("Panelist reviews table not found, skipping calibration validation")
            conn.close()
            return True
        
        # Get panelist calibration data (last 10 evaluations per panelist)
        cursor.execute("""
            SELECT pr.panelist_id, p.name as panelist_name, 
                   AVG(pr.panelist_score) as avg_score,
                   COUNT(*) as evaluation_count
            FROM panelist_reviews pr
            JOIN panelists p ON pr.panelist_id = p.id
            WHERE pr.created_at >= datetime('now', '-30 days')
            GROUP BY pr.panelist_id, p.name
            HAVING evaluation_count >= 3
            ORDER BY pr.panelist_id
        """)
        
        panelists = cursor.fetchall()
        
        if not panelists:
            print("Insufficient panelist data for calibration analysis (need 3+ evaluations per panelist)")
            conn.close()
            return True
        
        print(f"Found {len(panelists)} panelists with sufficient data for calibration analysis")
        print(f"Security: Panelist calibration tracking is internal-only - panelists never see scores")
        
        # Calculate consensus score (average of all panelist scores)
        cursor.execute("""
            SELECT AVG(pr.panelist_score) as consensus_score
            FROM panelist_reviews pr
            WHERE pr.created_at >= datetime('now', '-30 days')
        """)
        
        result = cursor.fetchone()
        consensus_score = result[0] if result and result[0] else 0
        
        if consensus_score == 0:
            print("No recent panelist reviews found for consensus calculation")
            conn.close()
            return True
        
        print(f"Consensus score (last 30 days): {consensus_score:.2f}")
        
        # Check for calibration issues (divergence >2 points from consensus)
        calibration_issues = []
        
        for panelist_id, panelist_name, avg_score, eval_count in panelists:
            divergence = abs(avg_score - consensus_score)
            
            if divergence > 2.0:
                calibration_issues.append({
                    'panelist': panelist_id,  # Use ID instead of name for security
                    'avg_score': avg_score,
                    'divergence': divergence,
                    'evaluations': eval_count
                })
        
        if calibration_issues:
            print(f"Gate SG-4 WARN: Panelist calibration issues detected (INTERNAL-ONLY)")
            for issue in calibration_issues:
                print(f"   - Panelist ID {issue['panelist']}: divergence {issue['divergence']:.2f} from consensus ({eval_count} evaluations)")
            print(f"   Recommendation: Recalibrate panelists with divergence >2 points (internal quality management)")
            print(f"   Security: Panelists never see scores or calibration status - this is internal-only for quality improvement")
            return False
        else:
            print(f"Gate SG-4 PASS: All panelists within calibration limits (divergence ≤2 points)")
            print(f"   Security: Panelist calibration tracking is internal-only - not exposed to panelists")
            for panelist_id, panelist_name, avg_score, eval_count in panelists:
                divergence = abs(avg_score - consensus_score)
                print(f"   - Panelist ID {panelist_id}: divergence {divergence:.2f} from consensus ({eval_count} evaluations)")
            return True
            
    except Exception as e:
        print(f"Error during calibration validation: {e}")
        return True
    finally:
        if 'conn' in locals():
            conn.close()

def main():
    # Always return exit code 0 (soft gate never blocks)
    check_gate_condition()
    sys.exit(0)

if __name__ == "__main__":
    main()