#!/usr/bin/env python3
"""
Round Table Database Manager

Provides database operations for findings tracking per SQLITE_SCHEMA.md.
Handles panelist reviews, findings, rules, and audit logging.
"""

import sqlite3
import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any
import uuid

class RoundTableDatabase:
    """Database manager for Round Table findings tracking."""
    
    def __init__(self, db_path: str = None):
        """Initialize database connection."""
        if db_path is None:
            # Use script directory for cross-platform compatibility
            script_dir = Path(__file__).parent
            db_dir = script_dir
            db_dir.mkdir(parents=True, exist_ok=True)
            db_path = db_dir / "roundtable.db"
        
        self.db_path = db_path
        self.conn = None
        
    def connect(self):
        """Establish database connection."""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            self.conn.execute("PRAGMA foreign_keys = ON")
        return self.conn
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    # Batch Operations
    def create_batch(self, batch_number: str, brief_file: str, plan_count: int) -> int:
        """Create a new batch."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO batches (batch_number, brief_file, plan_count)
            VALUES (?, ?, ?)
        """, (batch_number, brief_file, plan_count))
        conn.commit()
        return cursor.lastrowid
    
    def get_batch_by_number(self, batch_number: str) -> Optional[Dict]:
        """Get batch by batch number."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM batches WHERE batch_number = ?", (batch_number,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    # Plan Operations
    def create_plan(self, batch_id: int, plan_number: str, title: str, file_path: str) -> int:
        """Create a new plan."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO plans (batch_id, plan_number, title, file_path)
            VALUES (?, ?, ?, ?)
        """, (batch_id, plan_number, title, file_path))
        conn.commit()
        return cursor.lastrowid
    
    def update_plan_status(self, plan_id: int, status: str):
        """Update plan review status."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE plans SET review_status = ?, updated_at = strftime('%s', 'now')
            WHERE id = ?
        """, (status, plan_id))
        conn.commit()
    
    def get_plan_by_number(self, plan_number: str) -> Optional[Dict]:
        """Get plan by plan number."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM plans WHERE plan_number = ?", (plan_number,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    # Panelist Operations
    def create_panelist(self, name: str, model: str, specialty: str = None) -> int:
        """Create a new panelist."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO panelists (name, model, specialty)
            VALUES (?, ?, ?)
        """, (name, model, specialty))
        conn.commit()
        return cursor.lastrowid
    
    def get_panelist_by_name(self, name: str) -> Optional[Dict]:
        """Get panelist by name."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM panelists WHERE name = ?", (name,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_active_panelists(self) -> List[Dict]:
        """Get all active panelists."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM panelists WHERE active = 1")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    # Panelist Review Operations
    def create_panelist_review(self, plan_id: int, panelist_id: int, review_content: str,
                             summary: str = None, findings_json: str = None, verdict: str = None,
                             confidence_score: int = None, panelist_score: int = None,
                             web_search_used: bool = False, web_search_citations: str = None) -> int:
        """Create a new panelist review."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO panelist_reviews (
                plan_id, panelist_id, review_content, summary, findings_json,
                verdict, confidence_score, panelist_score, web_search_used, web_search_citations
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (plan_id, panelist_id, review_content, summary, findings_json,
              verdict, confidence_score, panelist_score, web_search_used, web_search_citations))
        conn.commit()
        return cursor.lastrowid
    
    def get_reviews_by_plan(self, plan_id: int) -> List[Dict]:
        """Get all reviews for a plan."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT pr.*, p.name as panelist_name, p.model as panelist_model
            FROM panelist_reviews pr
            JOIN panelists p ON pr.panelist_id = p.id
            WHERE pr.plan_id = ?
        """, (plan_id,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    # Findings Operations
    def create_finding(self, review_id: int, category: str, severity: str, description: str,
                      context: str = None, plan_impact: str = None) -> int:
        """Create a new finding."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO findings (review_id, category, severity, description, context, plan_impact)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (review_id, category, severity, description, context, plan_impact))
        conn.commit()
        return cursor.lastrowid
    
    def get_findings_by_review(self, review_id: int) -> List[Dict]:
        """Get all findings for a review."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM findings WHERE review_id = ?", (review_id,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def get_findings_by_status(self, status: str) -> List[Dict]:
        """Get all findings by status."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM findings WHERE status = ?", (status,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def update_finding_status(self, finding_id: int, status: str):
        """Update finding status."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE findings SET status = ?, updated_at = strftime('%s', 'now')
            WHERE id = ?
        """, (status, finding_id))
        conn.commit()
    
    # Rules Operations
    def create_rule(self, rule_id: str, title: str, description: str, category: str,
                   trigger_conditions: str = None, pattern_source: str = None,
                   enforcement_level: str = 'guideline') -> int:
        """Create a new rule."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO rules (rule_id, title, description, category, trigger_conditions, pattern_source, enforcement_level)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (rule_id, title, description, category, trigger_conditions, pattern_source, enforcement_level))
        conn.commit()
        return cursor.lastrowid
    
    def get_active_rules(self) -> List[Dict]:
        """Get all active rules."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM rules WHERE active = 1")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def get_rules_by_category(self, category: str) -> List[Dict]:
        """Get rules by category."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM rules WHERE category = ? AND active = 1", (category,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    # Export Operations
    def export_findings_json(self, batch_id: str = None) -> Dict:
        """Export findings as JSON."""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Build export metadata
        export_metadata = {
            "export_timestamp": datetime.now(datetime.timezone.utc).isoformat() + "Z",
            "export_version": "1.0",
            "batch_id": batch_id or "all"
        }
        
        # Get findings from view
        cursor.execute("SELECT finding_json FROM v_findings_export")
        rows = cursor.fetchall()
        
        findings = [json.loads(row[0]) for row in rows]
        
        export_metadata["total_findings"] = len(findings)
        
        # Calculate summary statistics
        summary = {
            "by_severity": {},
            "by_category": {},
            "by_status": {}
        }
        
        for finding in findings:
            severity = finding["severity"]
            category = finding["category"]
            status = finding["status"]
            
            summary["by_severity"][severity] = summary["by_severity"].get(severity, 0) + 1
            summary["by_category"][category] = summary["by_category"].get(category, 0) + 1
            summary["by_status"][status] = summary["by_status"].get(status, 0) + 1
        
        return {
            "export_metadata": export_metadata,
            "findings": findings,
            "summary": summary
        }
    
    def export_rules_json(self) -> Dict:
        """Export rules as JSON."""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Build export metadata
        export_metadata = {
            "export_timestamp": datetime.now(datetime.timezone.utc).isoformat() + "Z",
            "export_version": "1.0"
        }
        
        # Get rules from view
        cursor.execute("SELECT rule_json FROM v_rules_export")
        rows = cursor.fetchall()
        
        rules = [json.loads(row[0]) for row in rows]
        
        export_metadata["total_rules"] = len(rules)
        export_metadata["active_rules"] = len([r for r in rules if r.get("active", True)])
        
        # Calculate summary statistics
        summary = {
            "by_category": {},
            "by_enforcement": {}
        }
        
        for rule in rules:
            category = rule["category"]
            enforcement = rule["enforcement_level"]
            
            summary["by_category"][category] = summary["by_category"].get(category, 0) + 1
            summary["by_enforcement"][enforcement] = summary["by_enforcement"].get(enforcement, 0) + 1
        
        return {
            "export_metadata": export_metadata,
            "rules": rules,
            "summary": summary
        }
    
    # Audit Operations
    def get_audit_events(self, source: str = None, event_type: str = None, limit: int = 100) -> List[Dict]:
        """Get audit events with optional filtering."""
        conn = self.connect()
        cursor = conn.cursor()
        
        query = "SELECT * FROM audit_log"
        params = []
        
        if source:
            query += " WHERE source = ?"
            params.append(source)
        
        if event_type:
            if source:
                query += " AND event_type = ?"
            else:
                query += " WHERE event_type = ?"
            params.append(event_type)
        
        query += " ORDER BY event_time DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def main():
    """Test database operations."""
    db = RoundTableDatabase()
    
    # Test database operations
    with db:
        # Create a test panelist
        panelist_id = db.create_panelist("Test Panelist", "gpt-4", "Technical Architecture")
        print(f"✅ Created panelist with ID: {panelist_id}")
        
        # Create a test batch
        batch_id = db.create_batch("test-batch-1", "brief-test.md", 1)
        print(f"✅ Created batch with ID: {batch_id}")
        
        # Create a test plan
        plan_id = db.create_plan(batch_id, "1", "Test Plan", "Plans/plan-1.md")
        print(f"✅ Created plan with ID: {plan_id}")
        
        # Create a test review
        review_id = db.create_panelist_review(
            plan_id, panelist_id, "Test review content",
            verdict="Pass", confidence_score=8, panelist_score=85
        )
        print(f"✅ Created review with ID: {review_id}")
        
        # Create a test finding
        finding_id = db.create_finding(
            review_id, "architecture", "HIGH", "Test finding",
            context="Test context", plan_impact="Test impact"
        )
        print(f"✅ Created finding with ID: {finding_id}")
        
        # Test export
        findings_export = db.export_findings_json()
        print(f"✅ Exported {len(findings_export['findings'])} findings")
        
        # Test audit log
        audit_events = db.get_audit_events(limit=5)
        print(f"✅ Retrieved {len(audit_events)} audit events")

if __name__ == "__main__":
    main()