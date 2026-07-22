# JSON Export Format for Git Persistence

**Version**: 1.0  
**Last Updated**: 2026-07-22  
**Status**: Design Phase

## Export Structure

```
.Planner/roundtable/export/
├── findings/
│   ├── batch_31_34/
│   │   ├── findings_batch_31_34_20260722T120000Z.json
│   │   └── summary_batch_31_34_20260722T120000Z.json
│   └── batch_35_39/
│       └── findings_batch_35_39_20260723T150000Z.json
├── rules/
│   ├── roundtable_rules_20260722T120000Z.json
│   └── roundtable_rules_20260723T150000Z.json
└── audit/
    ├── audit_log_20260722T120000Z.json
    └── audit_log_20260723T150000Z.json
```

## Finding Export Format

### Individual Finding JSON
```json
{
  "finding_id": 42,
  "category": "architecture",
  "severity": "HIGH",
  "description": "Circular dependency between ModelRegistry and Orchestrator startup sequence",
  "context": "Plan 33 S1.3 startup sequence",
  "plan_impact": "May cause startup deadlock if ModelRegistry needs Orchestrator for sync triggers",
  "status": "open",
  "review_info": {
    "review_id": 15,
    "panelist": {
      "name": "Architecture Reviewer",
      "model": "claude-3.5-sonnet"
    },
    "plan": {
      "plan_number": "33",
      "title": "Agent Lifecycle",
      "revision_count": 17
    }
  },
  "timestamps": {
    "created_at": 1721653200,
    "updated_at": 1721653200
  }
}
```

### Batch Findings JSON
```json
{
  "export_metadata": {
    "batch_id": "31-34",
    "export_timestamp": "2026-07-22T12:00:00Z",
    "export_version": "1.0",
    "total_findings": 23,
    "plan_count": 4
  },
  "findings": [
    {
      "finding_id": 42,
      "category": "architecture",
      "severity": "HIGH",
      "description": "Circular dependency between ModelRegistry and Orchestrator startup sequence",
      "context": "Plan 33 S1.3 startup sequence",
      "plan_impact": "May cause startup deadlock if ModelRegistry needs Orchestrator for sync triggers",
      "status": "open",
      "review_info": {
        "review_id": 15,
        "panelist": {
          "name": "Architecture Reviewer",
          "model": "claude-3.5-sonnet"
        },
        "plan": {
          "plan_number": "33",
          "title": "Agent Lifecycle",
          "revision_count": 17
        }
      },
      "timestamps": {
        "created_at": 1721653200,
        "updated_at": 1721653200
      }
    }
  ],
  "summary": {
    "by_severity": {
      "CRITICAL": 2,
      "HIGH": 8,
      "MEDIUM": 10,
      "LOW": 3
    },
    "by_category": {
      "architecture": 5,
      "database": 4,
      "api-contract": 6,
      "security": 3,
      "implementation": 5
    },
    "by_status": {
      "open": 15,
      "addressed": 5,
      "deferred": 2,
      "rejected": 1
    }
  }
}
```

## Rules Export Format

### Individual Rule JSON
```json
{
  "rule_id": "RTR-1",
  "title": "Startup Sequence Dependency Check",
  "description": "Verify no circular dependencies exist in agent startup sequences. If ModelRegistry needs Orchestrator for sync triggers, this creates a circular dependency that must be resolved.",
  "category": "architecture",
  "trigger_conditions": "Plan includes agent startup sequence or initialization ordering",
  "pattern_source": "Repeated HIGH severity findings across Plans 31-34 regarding startup dependencies",
  "enforcement_level": "hard_gate",
  "evidence": {
    "finding_count": 3,
    "affected_plans": ["31", "32", "33"],
    "revision_reduction_potential": "high"
  },
  "timestamps": {
    "created_at": 1721653200,
    "updated_at": 1721653200
  }
}
```

### Rules Collection JSON
```json
{
  "export_metadata": {
    "export_timestamp": "2026-07-22T12:00:00Z",
    "export_version": "1.0",
    "total_rules": 12,
    "active_rules": 10
  },
  "rules": [
    {
      "rule_id": "RTR-1",
      "title": "Startup Sequence Dependency Check",
      "description": "Verify no circular dependencies exist in agent startup sequences. If ModelRegistry needs Orchestrator for sync triggers, this creates a circular dependency that must be resolved.",
      "category": "architecture",
      "trigger_conditions": "Plan includes agent startup sequence or initialization ordering",
      "pattern_source": "Repeated HIGH severity findings across Plans 31-34 regarding startup dependencies",
      "enforcement_level": "hard_gate",
      "evidence": {
        "finding_count": 3,
        "affected_plans": ["31", "32", "33"],
        "revision_reduction_potential": "high"
      },
      "timestamps": {
        "created_at": 1721653200,
        "updated_at": 1721653200
      }
    }
  ],
  "summary": {
    "by_category": {
      "architecture": 3,
      "database": 2,
      "api-contract": 4,
      "security": 2,
      "implementation": 1
    },
    "by_enforcement": {
      "hard_gate": 5,
      "soft_gate": 4,
      "guideline": 3
    }
  }
}
```

## Audit Log Export Format

### Audit Event JSON
```json
{
  "event_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "source": "findings",
  "subject": "42",
  "event_type": "findings.created",
  "event_time": 1721653200,
  "specversion": "1.0",
  "data": {
    "new": {
      "id": 42,
      "review_id": 15,
      "category": "architecture",
      "severity": "HIGH",
      "description": "Circular dependency between ModelRegistry and Orchestrator startup sequence",
      "status": "open"
    }
  }
}
```

### Audit Log Collection JSON
```json
{
  "export_metadata": {
    "export_timestamp": "2026-07-22T12:00:00Z",
    "export_version": "1.0",
    "total_events": 156,
    "time_range": {
      "start": 1721653200,
      "end": 1721739600
    }
  },
  "events": [
    {
      "event_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "source": "findings",
      "subject": "42",
      "event_type": "findings.created",
      "event_time": 1721653200,
      "specversion": "1.0",
      "data": {
        "new": {
          "id": 42,
          "review_id": 15,
          "category": "architecture",
          "severity": "HIGH",
          "description": "Circular dependency between ModelRegistry and Orchestrator startup sequence",
          "status": "open"
        }
      }
    }
  ]
}
```

## Git Commit Message Format

### Findings Export Commit
```
RoundTable: Export findings for batch 31-34

Export timestamp: 2026-07-22T12:00:00Z
Total findings: 23
Plans: 31, 32, 33, 34

Summary:
- CRITICAL: 2
- HIGH: 8  
- MEDIUM: 10
- LOW: 3

Generated with Devin RoundTable workflow
```

### Rules Export Commit
```
RoundTable: Export rules with pattern analysis

Export timestamp: 2026-07-22T12:00:00Z
Total rules: 12
Active rules: 10

New rules from batch 31-34:
- RTR-1: Startup Sequence Dependency Check
- RTR-2: SSE Infrastructure Unification

Generated with Devin RoundTable workflow
```

## Export Workflow

1. **Generate JSON from SQLite views**:
   ```bash
   sqlite3 roundtable.db "SELECT json_group_array(finding_json) FROM v_findings_export" > findings_export.json
   ```

2. **Add export metadata**:
   ```python
   export_data = {
     "export_metadata": {
       "batch_id": batch_id,
       "export_timestamp": datetime.utcnow().isoformat() + "Z",
       "export_version": "1.0",
       "total_findings": len(findings)
     },
     "findings": findings
   }
   ```

3. **Write to timestamped file**:
   ```python
   filename = f"findings_batch_{batch_id}_{timestamp}.json"
   with open(f".Planner/roundtable/export/findings/{filename}", 'w') as f:
     json.dump(export_data, f, indent=2)
   ```

4. **Git commit with structured message**:
   ```bash
   git add .Planner/roundtable/export/
   git commit -m "$(cat <<'EOF'
   RoundTable: Export findings for batch 31-34
   
   Export timestamp: 2026-07-22T12:00:00Z
   Total findings: 23
   
   Generated with Devin RoundTable workflow
   EOF
   )"
   ```

## Diffability Benefits

Plain JSON format enables:
- **Git diff**: See exactly what changed between exports
- **PR review**: Review rule changes like code
- **Rollback**: Revert to previous rule sets
- **History**: Track rule evolution over time
- **Merge**: Resolve conflicts in rule definitions

## Incremental Exports

Only export changed data since last export:
```sql
SELECT json_group_array(finding_json) 
FROM v_findings_export 
WHERE updated_at > :last_export_timestamp
```