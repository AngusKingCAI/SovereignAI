#!/usr/bin/env python3
"""
Round Table Database Initialization

Initializes SQLite database with schema for findings tracking per SQLITE_SCHEMA.md.
Includes audit tables, triggers, and views for comprehensive tracking.
"""

import sqlite3
import os
import sys
from pathlib import Path
from datetime import datetime

# UTF-8 print helper for Windows console compatibility
def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        # Fallback for console encoding issues
        print(text.encode('ascii', 'ignore').decode('ascii'))

def create_database_schema(db_path):
    """
    Create database schema with all tables, indexes, triggers, and views.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # Core Tables
    create_panelists_table(cursor)
    create_batches_table(cursor)
    create_plans_table(cursor)
    create_panelist_reviews_table(cursor)
    create_findings_table(cursor)
    create_rules_table(cursor)
    create_rule_applications_table(cursor)
    
    # Audit Tables
    create_audit_log_table(cursor)
    create_history_tables(cursor)
    
    # JSON Export Views
    create_export_views(cursor)
    
    # Audit Triggers
    create_audit_triggers(cursor)
    
    conn.commit()
    conn.close()
    safe_print(f"Database schema created at {db_path}")

def create_panelists_table(cursor):
    """Create panelists table for panelist metadata and scoring information."""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS panelists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            model TEXT NOT NULL,
            specialty TEXT,
            created_at INTEGER DEFAULT (strftime('%s', 'now')),
            updated_at INTEGER DEFAULT (strftime('%s', 'now')),
            active BOOLEAN DEFAULT 1
        )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_panelists_active ON panelists (active)")

def create_batches_table(cursor):
    """Create batches table for grouping related plans."""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS batches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            batch_number TEXT NOT NULL UNIQUE,
            brief_file TEXT NOT NULL,
            plan_count INTEGER NOT NULL,
            goal_tree_json TEXT,
            created_at INTEGER DEFAULT (strftime('%s', 'now')),
            updated_at INTEGER DEFAULT (strftime('%s', 'now'))
        )
    """)

def create_plans_table(cursor):
    """Create plans table for plan metadata and review status."""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            batch_id INTEGER NOT NULL,
            plan_number TEXT NOT NULL,
            title TEXT NOT NULL,
            file_path TEXT NOT NULL,
            revision_count INTEGER DEFAULT 0,
            review_status TEXT DEFAULT 'pending',
            created_at INTEGER DEFAULT (strftime('%s', 'now')),
            updated_at INTEGER DEFAULT (strftime('%s', 'now')),
            FOREIGN KEY (batch_id) REFERENCES batches(id)
        )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_plans_batch ON plans (batch_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_plans_status ON plans (review_status)")

def create_panelist_reviews_table(cursor):
    """Create panelist_reviews table for individual panelist review responses with web search integration."""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS panelist_reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plan_id INTEGER NOT NULL,
            panelist_id INTEGER NOT NULL,
            review_content TEXT NOT NULL,
            summary TEXT,
            findings_json TEXT,
            verdict TEXT,
            confidence_score INTEGER,
            panelist_score INTEGER,
            web_search_used BOOLEAN DEFAULT 0,
            web_search_citations TEXT,
            created_at INTEGER DEFAULT (strftime('%s', 'now')),
            FOREIGN KEY (plan_id) REFERENCES plans(id),
            FOREIGN KEY (panelist_id) REFERENCES panelists(id)
        )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_reviews_plan ON panelist_reviews (plan_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_reviews_panelist ON panelist_reviews (panelist_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_reviews_web_search ON panelist_reviews (web_search_used)")

def create_findings_table(cursor):
    """Create findings table for individual findings extracted from panelist reviews."""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS findings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            review_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            severity TEXT NOT NULL,
            description TEXT NOT NULL,
            context TEXT,
            plan_impact TEXT,
            status TEXT DEFAULT 'open',
            created_at INTEGER DEFAULT (strftime('%s', 'now')),
            updated_at INTEGER DEFAULT (strftime('%s', 'now')),
            FOREIGN KEY (review_id) REFERENCES panelist_reviews(id)
        )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_findings_status ON findings (status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_findings_severity ON findings (severity)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_findings_category ON findings (category)")

def create_rules_table(cursor):
    """Create rules table for rules extracted from repeated findings patterns."""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rule_id TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            trigger_conditions TEXT,
            pattern_source TEXT,
            enforcement_level TEXT,
            created_at INTEGER DEFAULT (strftime('%s', 'now')),
            updated_at INTEGER DEFAULT (strftime('%s', 'now')),
            active BOOLEAN DEFAULT 1
        )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_rules_active ON rules (active)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_rules_category ON rules (category)")

def create_rule_applications_table(cursor):
    """Create rule_applications table to track which rules apply to which findings."""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rule_applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rule_id INTEGER NOT NULL,
            finding_id INTEGER NOT NULL,
            application_confidence REAL,
            created_at INTEGER DEFAULT (strftime('%s', 'now')),
            FOREIGN KEY (rule_id) REFERENCES rules(id),
            FOREIGN KEY (finding_id) REFERENCES findings(id)
        )
    """)

def create_audit_log_table(cursor):
    """Create audit_log table following CloudEvents spec."""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id TEXT NOT NULL UNIQUE,
            source TEXT NOT NULL,
            subject TEXT,
            event_type TEXT NOT NULL,
            event_time INTEGER NOT NULL,
            specversion TEXT DEFAULT '1.0',
            data TEXT NOT NULL
        )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_time ON audit_log (event_time)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_source ON audit_log (source)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_type ON audit_log (event_type)")

def create_history_tables(cursor):
    """Create version tracking tables for data forensics."""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS _panelists_history (
            _rowid INTEGER,
            id INTEGER,
            name TEXT,
            model TEXT,
            specialty TEXT,
            created_at INTEGER,
            updated_at INTEGER,
            active BOOLEAN,
            _version INTEGER,
            _updated INTEGER,
            _mask INTEGER
        )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_panelists_history_rowid ON _panelists_history (_rowid)")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS _findings_history (
            _rowid INTEGER,
            id INTEGER,
            review_id INTEGER,
            category TEXT,
            severity TEXT,
            description TEXT,
            context TEXT,
            plan_impact TEXT,
            status TEXT,
            created_at INTEGER,
            updated_at INTEGER,
            _version INTEGER,
            _updated INTEGER,
            _mask INTEGER
        )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_findings_history_rowid ON _findings_history (_rowid)")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS _rules_history (
            _rowid INTEGER,
            id INTEGER,
            rule_id TEXT,
            title TEXT,
            description TEXT,
            category TEXT,
            trigger_conditions TEXT,
            pattern_source TEXT,
            enforcement_level TEXT,
            created_at INTEGER,
            updated_at INTEGER,
            active BOOLEAN,
            _version INTEGER,
            _updated INTEGER,
            _mask INTEGER
        )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_rules_history_rowid ON _rules_history (_rowid)")

def create_export_views(cursor):
    """Create JSON export views for git persistence."""
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS v_findings_export AS
        SELECT 
            json_object(
                'finding_id', f.id,
                'category', f.category,
                'severity', f.severity,
                'description', f.description,
                'context', f.context,
                'plan_impact', f.plan_impact,
                'status', f.status,
                'review_info', json_object(
                    'review_id', f.review_id,
                    'panelist', json_object(
                        'name', p.name,
                        'model', p.model
                    ),
                    'plan', json_object(
                        'plan_number', pl.plan_number,
                        'title', pl.title,
                        'revision_count', pl.revision_count
                    )
                ),
                'timestamps', json_object(
                    'created_at', f.created_at,
                    'updated_at', f.updated_at
                )
            ) as finding_json
        FROM findings f
        JOIN panelist_reviews pr ON f.review_id = pr.id
        JOIN panelists p ON pr.panelist_id = p.id
        JOIN plans pl ON pr.plan_id = pl.id
    """)
    
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS v_rules_export AS
        SELECT 
            json_object(
                'rule_id', r.rule_id,
                'title', r.title,
                'description', r.description,
                'category', r.category,
                'trigger_conditions', r.trigger_conditions,
                'pattern_source', r.pattern_source,
                'enforcement_level', r.enforcement_level,
                'evidence', json_object(
                    'finding_count', COUNT(ra.id),
                    'affected_plans', json_group_array(pl.plan_number)
                ),
                'timestamps', json_object(
                    'created_at', r.created_at,
                    'updated_at', r.updated_at
                )
            ) as rule_json
        FROM rules r
        LEFT JOIN rule_applications ra ON r.id = ra.rule_id
        LEFT JOIN findings f ON ra.finding_id = f.id
        LEFT JOIN panelist_reviews pr ON f.review_id = pr.id
        LEFT JOIN plans pl ON pr.plan_id = pl.id
        GROUP BY r.id
    """)

def create_audit_triggers(cursor):
    """Create audit triggers for automatic audit logging."""
    # Panelist audit trigger
    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS trg_panelists_audit
        AFTER INSERT ON panelists
        BEGIN
            INSERT INTO audit_log (event_id, source, subject, event_type, event_time, data)
            VALUES (
                lower(hex(randomblob(16))),
                'panelists',
                NEW.id,
                'panelists.created',
                strftime('%s', 'now'),
                json_object('new', json_object('id', NEW.id, 'name', NEW.name, 'model', NEW.model))
            );
        END
    """)
    
    # Findings audit trigger
    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS trg_findings_audit
        AFTER INSERT ON findings
        BEGIN
            INSERT INTO audit_log (event_id, source, subject, event_type, event_time, data)
            VALUES (
                lower(hex(randomblob(16))),
                'findings',
                NEW.id,
                'findings.created',
                strftime('%s', 'now'),
                json_object('new', json_object('id', NEW.id, 'category', NEW.category, 'severity', NEW.severity))
            );
        END
    """)
    
    # Rules audit trigger
    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS trg_rules_audit
        AFTER INSERT ON rules
        BEGIN
            INSERT INTO audit_log (event_id, source, subject, event_type, event_time, data)
            VALUES (
                lower(hex(randomblob(16))),
                'rules',
                NEW.id,
                'rules.created',
                strftime('%s', 'now'),
                json_object('new', json_object('id', NEW.id, 'rule_id', NEW.rule_id, 'title', NEW.title))
            );
        END
    """)

def main():
    """Main database initialization function."""
    # Set up database directory - resolve from script location for cross-platform compatibility
    script_dir = Path(__file__).parent
    db_dir = script_dir  # Use the script's directory as the database directory
    db_dir.mkdir(parents=True, exist_ok=True)
    
    db_path = db_dir / "roundtable.db"
    
    safe_print(f"Initializing Round Table database at {db_path}")
    
    # Check if database already exists
    if db_path.exists():
        safe_print("Database already exists. Backup existing database...")
        backup_path = db_dir / f"roundtable_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        import shutil
        shutil.copy2(db_path, backup_path)
        safe_print(f"Backup created at {backup_path}")
    
    # Create database schema
    create_database_schema(db_path)
    
    safe_print("Round Table database initialization complete")

if __name__ == "__main__":
    main()