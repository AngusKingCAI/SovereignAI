# Directory Structure and Log Naming Conventions

## Constitutional Document Hierarchy

**Root Level (Constitutional Authority)**:
- `PRINCIPLES.md` - Supreme project constitution (P1-P14 + workflow principles)
- `FOUNDING_ARCHITECTURE.md` - Architect infrastructure constitution
- `AGENTS.md` - Universal invariants for all agents
- `README.md` - Project overview

**Docs/ (Reference & Documentation)**:
- `DECISIONS.md` - Historical decision log (119 decisions from 40,323 lines)
- `DIRECTORY_STRUCTURE.md` - Architecture documentation
- `specs/` - Technical specifications
- `logging/` - System documentation

**Rules/ (Active Governance)**:
- `Architect/` - Architect-specific rules
- [Future] `Global/` - Universal rules
- [Future] Other agent rules

## Directory Structure

The SovereignAI Harness follows a structured directory layout that separates concerns and maintains architectural clarity:

```
SovereignAI/
├── PRINCIPLES.md                 # Supreme project constitution (P1-P14 + workflow)
├── FOUNDING_ARCHITECTURE.md     # Architect infrastructure constitution
├── AGENTS.md                     # Universal invariants for all agents
├── README.md                    # Project overview
├── App/                          # SovereignAI application layer
│   ├── sovereignai/             # Core application modules
│   │   ├── agent/               # Agent configuration and factory
│   │   ├── memory/              # Memory backends (episodic, procedural, trace, working, graph)
│   │   ├── messaging/           # Message bus and adapters
│   │   ├── managers/            # Component managers
│   │   ├── lifecycle/           # Lifecycle management
│   │   ├── conformance/         # Conformance checking
│   │   ├── indexing/            # Symbol indexing
│   │   ├── librarian/           # Librarian component
│   │   ├── model_registry/      # Model registry and adapters
│   │   ├── observability/       # Observability tools
│   │   ├── options/             # Options and settings
│   │   ├── orchestrator/        # Orchestrator component
│   │   ├── shared/              # Shared utilities
│   │   ├── skills/              # Application skills
│   │   ├── tests/               # Application tests
│   │   ├── versioning/          # Version management
│   │   └── workers/             # Worker components
│   ├── adapters/                # External adapters (llama_cpp, ollama)
│   ├── adapters/internal/        # Internal memory adapters
│   ├── services/                # Service providers (ollama_service)
│   ├── skills/                  # Application skills (official, user)
│   ├── databases/               # Database providers (hf_database)
│   ├── cli/                     # Command-line interface
│   ├── tui/                     # Terminal user interface
│   ├── web/                     # Web interface
│   ├── phone/                   # Phone interface
│   └── txt/                     # Text interface
├── Agents/                       # Agent-specific governance
│   └── Architect/
│       └── AGENTS.md            # Architect agent documentation
├── Rules/                        # Role-specific rules
│   └── Architect/
│       ├── Architect Rules.md   # Architect operational rules
│       └── IDE_Architecture_Rules.md  # IDE structure rules
├── Workflow/                     # Agent workflows
│   ├── Architect/
│   │   └── Architect Workflow.md
│   ├── Planner/
│   │   └── Plan.md
│   ├── Executor/
│   │   └── Execute.md
│   ├── Researcher/
│   │   └── Research.md
│   └── Reviewer/
│       └── Review.md
├── Scripts/                      # All executable scripts and source code
│   ├── Architect/                # Architect-specific scripts
│   │   ├── Gates/               # Gate enforcement system
│   │   │   ├── verify-phase-complete.sh
│   │   │   ├── record-phase-complete.sh
│   │   │   ├── verify-conversation-logging.sh
│   │   │   └── gate-core/       # Core gate functions
│   │   └── [Other architect scripts]
│   ├── src/                     # Source code
│   │   ├── logging/            # Logging system implementation
│   │   │   ├── log_level.py
│   │   │   ├── log_entry.py
│   │   │   ├── log_context.py
│   │   │   ├── correlation.py
│   │   │   ├── formatter.py
│   │   │   ├── conversation_logger.py
│   │   │   ├── logger.py
│   │   │   ├── __init__.py
│   │   │   └── output/          # Output handlers
│   │   │       ├── stdout_output.py
│   │   │       ├── file_output.py
│   │   │       └── __init__.py
│   │   └── config/             # Configuration files
│   │       └── logging_config.py
│   ├── tests/                   # Test suite
│   │   ├── test_log_level.py
│   │   ├── test_correlation.py
│   │   ├── test_formatter.py
│   │   └── test_integration.py
│   └── log_conversation.py      # Conversation logging script
├── Docs/                         # Documentation directory
│   ├── DECISIONS.md            # Historical decision log
│   ├── DIRECTORY_STRUCTURE.md   # This file
│   ├── specs/                  # Specifications
│   │   ├── phase-0-logging-foundation.md
│   │   ├── phase-0-hash-based-gates.md
│   │   └── phase-0-logging-implementation.md
│   ├── logging/                # Logging documentation
│   │   ├── LOGGING_GUIDE.md
│   │   └── EXAMPLES.md
│   ├── "Devin Local IDE Documents"  # IDE-specific documentation
│   └── "Sovereign AI Design Docs"   # Application design docs
├── Logs/                         # All log files
│   ├── Architect/              # Architect-specific logs
│   │   ├── Gates/              # Gate system logs
│   │   │   └── phase-0-state.json
│   │   ├── Conversations/      # AI conversation logs
│   │   │   └── session-*.json
│   │   ├── harness_infrastructure/  # Harness infrastructure logs
│   │   │   └── harness_infrastructure-YYYY-MM-DD.jsonl
│   │   ├── phase_0_operations/       # Phase 0 operations logs
│   │   │   └── phase_0_operations-YYYY-MM-DD.jsonl
│   │   └── constitutional_audit/     # Constitutional audit logs
│   │       └── constitutional_audit-YYYY-MM-DD.jsonl
├── Plans/                        # Execution plans (currently empty)
├── completed/                    # Executed plan artifacts (30-39 range)
└── .devin/                       # Devin CLI configuration
    ├── config.json
    └── hooks.v1.json
```

## Log Naming Conventions

### Architect Operation Logs

**Location**: `Logs/Architect/`

**Gate System Logs**:
- `phase-{N}-state.json` - State files for each phase
- Example: `phase-0-state.json`

**Conversation Logs**:
- `{session-id}.json` - AI conversation session logs
- Example: `phase-0-logging-implementation.json`

### Application Logs

**Location**: `Logs/Architect/{component}/`

**File Naming Pattern**: `{component}-{YYYY-MM-DD}.jsonl`

**Components**:
1. **harness_infrastructure** - Harness infrastructure events
   - Example: `harness_infrastructure-2024-01-01.jsonl`
2. **phase_0_operations** - Phase 0 operations
   - Example: `phase_0_operations-2024-01-01.jsonl`
3. **constitutional_audit** - Constitutional compliance
   - Example: `constitutional_audit-2024-01-01.jsonl`

### Log File Format

**JSONL Format**: Each line is a separate JSON object

**Standard Log Entry**:
```json
{
  "timestamp": "2024-01-01T00:00:00Z",
  "level": "INFO",
  "service": "SovereignAI_Harness",
  "event": "harness_infrastructure",
  "trace_id": "trace-123",
  "component": "harness_infrastructure",
  "message": "Message content",
  "context": {
    "key": "value"
  }
}
```

**OpenTelemetry Format**:
```json
{
  "timestamp": "2024-01-01T00:00:00Z",
  "severityNumber": 9,
  "severityText": "INFO",
  "body": "Message content",
  "resource": {
    "service.name": "SovereignAI_Harness",
    "service.version": "1.0.0"
  },
  "attributes": {
    "trace_id": "trace-123",
    "component": "harness_infrastructure",
    "event": "harness_infrastructure"
  }
}
```

## Log Rotation

**Current Implementation**: Date-based rotation
- New log file created each day (UTC)
- Automatic timestamp-based naming
- Manual rotation support via `rotate_log()` method

**Future Enhancements**:
- Size-based rotation
- Compressed archival
- Automatic cleanup policies

## Access Patterns

### Reading Current Logs
```bash
# Today's harness infrastructure logs
cat Logs/Architect/harness_infrastructure/harness_infrastructure-$(date +%Y-%m-%d).jsonl

# Recent conversation logs
ls -lt Logs/Architect/Conversations/
```

### Log Querying
```bash
# Filter by log level
grep '"level": "ERROR"' Logs/Architect/harness_infrastructure/*.jsonl

# Filter by trace ID
grep '"trace_id": "trace-123"' Logs/Architect/phase_0_operations/*.jsonl

# Filter by component
grep '"component": "constitutional_audit"' Logs/Architect/constitutional_audit/*.jsonl
```

### Log Aggregation
```bash
# Combine all logs for a day
cat Logs/Architect/*/*.jsonl > daily-logs-$(date +%Y-%m-%d).jsonl

# Extract specific fields
jq '{timestamp, level, message}' Logs/Architect/harness_infrastructure/*.jsonl
```

## Storage Considerations

**Estimated Growth**:
- Conservative: 10KB per log entry
- Typical: 50 log entries per hour
- Daily: ~12MB per component
- Monthly: ~360MB per component

**Cleanup Strategy**:
- Retain logs for 30 days by default
- Archive critical logs (constitutional_audit) for 90 days
- Manual export for long-term storage

## Integration Points

**Gate System Integration**:
- Gate operations logged to `constitutional_audit` component
- State changes logged with correlation IDs
- Phase verification results recorded

**Conversation Logging**:
- All AI conversations automatically captured
- Session-based organization
- JSON format for easy processing

**Development Workflow**:
- Development logs: DEBUG level to stdout
- Production logs: INFO level to file
- Audit logs: Always enabled, stored separately

## Security Considerations

**Log Access**:
- Architect logs: Read access for developers
- Constitutional audit: Restricted access
- Conversation logs: Sensitive data handling

**Data Protection**:
- No sensitive data in log messages
- PII redaction in conversation logs
- Encrypted storage for sensitive components

This structure provides clear separation of concerns, standardized naming conventions, and predictable log organization for the SovereignAI Harness infrastructure.