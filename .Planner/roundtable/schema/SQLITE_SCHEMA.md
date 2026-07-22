# SQLite Schema for Round Table Findings Tracking

**Version**: 1.0  
**Last Updated**: 2026-07-22  
**Status**: Design Phase

## Schema Overview

Full audit schema incorporating BP findings:
- JSON audit logs with triggers (Simon Willison pattern)
- Version tracking for data forensics (_tablename_history pattern)
- CloudEvents spec for standardized event schema
- Automatic audit logging via triggers

## Core Tables

### panelists
Panelist metadata and scoring information.

```sql
CREATE TABLE panelists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    model TEXT NOT NULL,
    specialty TEXT,
    created_at INTEGER DEFAULT (strftime('%s', 'now')),
    updated_at INTEGER DEFAULT (strftime('%s', 'now')),
    active BOOLEAN DEFAULT 1
);

CREATE INDEX idx_panelists_active ON panelists (active);
```

### batches
Batch metadata for grouping related plans.

```sql
CREATE TABLE batches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_number TEXT NOT NULL UNIQUE,
    brief_file TEXT NOT NULL,
    plan_count INTEGER NOT NULL,
    created_at INTEGER DEFAULT (strftime('%s', 'now')),
    updated_at INTEGER DEFAULT (strftime('%s', 'now'))
);
```

### plans
Plan metadata and review status.

```sql
CREATE TABLE plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_id INTEGER NOT NULL,
    plan_number TEXT NOT NULL,
    title TEXT NOT NULL,
    file_path TEXT NOT NULL,
    revision_count INTEGER DEFAULT 0,
    review_status TEXT DEFAULT 'pending', -- pending, in_review, approved, blocked
    created_at INTEGER DEFAULT (strftime('%s', 'now')),
    updated_at INTEGER DEFAULT (strftime('%s', 'now')),
    FOREIGN KEY (batch_id) REFERENCES batches(id)
);

CREATE INDEX idx_plans_batch ON plans (batch_id);
CREATE INDEX idx_plans_status ON plans (review_status);
```

### panelist_reviews
Individual panelist review responses.

```sql
CREATE TABLE panelist_reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id INTEGER NOT NULL,
    panelist_id INTEGER NOT NULL,
    review_content TEXT NOT NULL, -- Full panelist reply
    summary TEXT, -- AI-generated summary
    findings_json TEXT, -- Structured findings as JSON
    verdict TEXT, -- Pass/Conditional/Block
    confidence_score INTEGER, -- 1-10
    created_at INTEGER DEFAULT (strftime('%s', 'now')),
    FOREIGN KEY (plan_id) REFERENCES plans(id),
    FOREIGN KEY (panelist_id) REFERENCES panelists(id)
);

CREATE INDEX idx_reviews_plan ON panelist_reviews (plan_id);
CREATE INDEX idx_reviews_panelist ON panelist_reviews (panelist_id);
```

### findings
Individual findings extracted from panelist reviews.

```sql
CREATE TABLE findings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    review_id INTEGER NOT NULL,
    category TEXT NOT NULL, -- architecture, database, api-contract, security, etc.
    severity TEXT NOT NULL, -- CRITICAL, HIGH, MEDIUM, LOW
    description TEXT NOT NULL,
    context TEXT, -- Relevant code/plan section
    plan_impact TEXT, -- How this affects the plan
    status TEXT DEFAULT 'open', -- open, addressed, deferred, rejected
    created_at INTEGER DEFAULT (strftime('%s', 'now')),
    updated_at INTEGER DEFAULT (strftime('%s', 'now')),
    FOREIGN KEY (review_id) REFERENCES panelist_reviews(id)
);

CREATE INDEX idx_findings_status ON findings (status);
CREATE INDEX idx_findings_severity ON findings (severity);
CREATE INDEX idx_findings_category ON findings (category);
```

### rules
Rules extracted from repeated findings patterns.

```sql
CREATE TABLE rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_id TEXT NOT NULL UNIQUE, -- e.g., RTR-1 (Round Table Rule 1)
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    category TEXT NOT NULL,
    trigger_conditions TEXT, -- When this rule applies
    pattern_source TEXT, -- What findings pattern generated this
    enforcement_level TEXT, -- soft_gate, hard_gate, guideline
    created_at INTEGER DEFAULT (strftime('%s', 'now')),
    updated_at INTEGER DEFAULT (strftime('%s', 'now')),
    active BOOLEAN DEFAULT 1
);

CREATE INDEX idx_rules_active ON rules (active);
CREATE INDEX idx_rules_category ON rules (category);
```

### rule_applications
Track which rules apply to which findings.

```sql
CREATE TABLE rule_applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_id INTEGER NOT NULL,
    finding_id INTEGER NOT NULL,
    application_confidence REAL, -- 0.0-1.0
    created_at INTEGER DEFAULT (strftime('%s', 'now')),
    FOREIGN KEY (rule_id) REFERENCES rules(id),
    FOREIGN KEY (finding_id) REFERENCES findings(id)
);
```

## Audit Tables

### audit_log
Central audit log following CloudEvents spec.

```sql
CREATE TABLE audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT NOT NULL UNIQUE, -- UUID
    source TEXT NOT NULL, -- Table name that changed
    subject TEXT, -- Primary key of affected row
    event_type TEXT NOT NULL, -- *.created, *.updated, *.deleted
    event_time INTEGER NOT NULL, -- Unix timestamp
    specversion TEXT DEFAULT '1.0',
    data TEXT NOT NULL -- JSON: {"new": {...}, "old": {...}}
);

CREATE INDEX idx_audit_time ON audit_log (event_time);
CREATE INDEX idx_audit_source ON audit_log (source);
CREATE INDEX idx_audit_type ON audit_log (event_type);
```

### _panelists_history
Version tracking for panelists table.

```sql
CREATE TABLE _panelists_history (
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
);

CREATE INDEX idx_panelists_history_rowid ON _panelists_history (_rowid);
```

### _findings_history
Version tracking for findings table.

```sql
CREATE TABLE _findings_history (
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
);

CREATE INDEX idx_findings_history_rowid ON _findings_history (_rowid);
```

### _rules_history
Version tracking for rules table.

```sql
CREATE TABLE _rules_history (
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
);

CREATE INDEX idx_rules_history_rowid ON _rules_history (_rowid);
```

## JSON Export Views

### v_findings_export
JSON export format for git persistence.

```sql
CREATE VIEW v_findings_export AS
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
WHERE f.status != 'rejected';
```

### v_rules_export
JSON export format for rules git persistence.

```sql
CREATE VIEW v_rules_export AS
SELECT 
    json_object(
        'rule_id', r.rule_id,
        'title', r.title,
        'description', r.description,
        'category', r.category,
        'trigger_conditions', r.trigger_conditions,
        'pattern_source', r.pattern_source,
        'enforcement_level', r.enforcement_level,
        'active', r.active,
        'timestamps', json_object(
            'created_at', r.created_at,
            'updated_at', r.updated_at
        )
    ) as rule_json
FROM rules r
WHERE r.active = 1;
```

## Triggers

### Audit Trigger Template
Apply to all main tables for automatic audit logging.

```sql
-- Example for findings table
CREATE TRIGGER findings_audit_insert
AFTER INSERT ON findings
BEGIN
    INSERT INTO audit_log (
        event_id, source, subject, event_type, event_time, data
    ) VALUES (
        lower(hex(randomblob(16))),
        'findings',
        NEW.id,
        'findings.created',
        strftime('%s', 'now'),
        json_object('new', json_object(
            'id', NEW.id,
            'review_id', NEW.review_id,
            'category', NEW.category,
            'severity', NEW.severity,
            'description', NEW.description,
            'status', NEW.status
        ))
    );
END;

CREATE TRIGGER findings_audit_update
AFTER UPDATE ON findings
BEGIN
    INSERT INTO audit_log (
        event_id, source, subject, event_type, event_time, data
    ) VALUES (
        lower(hex(randomblob(16))),
        'findings',
        NEW.id,
        'findings.updated',
        strftime('%s', 'now'),
        json_object('new', json_object(
            'id', NEW.id,
            'review_id', NEW.review_id,
            'category', NEW.category,
            'severity', NEW.severity,
            'description', NEW.description,
            'status', NEW.status
        ), 'old', json_object(
            'id', OLD.id,
            'review_id', OLD.review_id,
            'category', OLD.category,
            'severity', OLD.severity,
            'description', OLD.description,
            'status', OLD.status
        ))
    );
END;
```

## Migration Strategy

1. **Phase 1**: Create core tables (panelists, batches, plans, panelist_reviews)
2. **Phase 2**: Add findings and rules tables
3. **Phase 3**: Implement audit infrastructure (audit_log, triggers)
4. **Phase 4**: Add version tracking (_tablename_history tables)
5. **Phase 5**: Create JSON export views

## Usage Pattern

1. User pastes panelist reply → Insert into panelist_reviews
2. AI extracts findings → Insert into findings with JSON structure
3. Pattern detection → Generate rules from repeated findings
4. JSON export → Git commit for persistence
5. Audit trail → Automatic via triggers