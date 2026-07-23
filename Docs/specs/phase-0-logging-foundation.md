# Phase 0: Logging Foundation Specification

**Status**: Accepted  
**Phase**: 0 - Repository Foundation  
**Created**: 2026-07-23  
**Constitutional Compliance**: Verified

## 1. Overview

This specification defines a comprehensive logging foundation for the SovereignAI infrastructure harness. The logging system provides observability across three areas: harness infrastructure logging, Phase 0 operational logging, and constitutional audit logging.

## 2. Requirements

### 2.1 Functional Requirements
- **Structured JSON Logging**: All logs must be structured JSON with consistent field names
- **Standard Log Levels**: DEBUG, INFO, WARN, ERROR, FATAL following industry conventions
- **Correlation IDs**: Every log entry must include a correlation/trace ID for request tracking
- **Three Logging Areas**: Harness infrastructure, Phase 0 operations, constitutional audit
- **Consistent Schema**: Standardized field names across all logging areas

### 2.2 Non-Functional Requirements
- **Deterministic**: Logging must not introduce non-deterministic behavior
- **Minimal Coupling**: Logging system must not create tight coupling with components
- **Observable**: All system state changes must be logged
- **Replaceable**: Logging implementation must be replaceable without component changes

## 3. Architecture

### 3.1 Log Schema

Standardized field names following OpenTelemetry conventions:

```json
{
  "timestamp": "ISO 8601 UTC",
  "level": "DEBUG|INFO|WARN|ERROR|FATAL",
  "service": "service-name",
  "event": "event_name",
  "trace_id": "correlation-id",
  "component": "logging-area",
  "message": "human-readable message",
  "context": {
    "key": "value"
  }
}
```

### 3.2 Logging Areas

#### Harness Infrastructure Logging
- Component lifecycle events
- Workflow step transitions
- Gate enforcement results
- Configuration changes

#### Phase 0 Operational Logging
- Repository operations
- File access patterns
- Hook execution results
- Workflow step tracking

#### Constitutional Audit Logging
- First Rule compliance checks
- Phase progression validation
- Specification reviews
- Architectural decision records

### 3.3 Log Levels

| Level | Usage | Example |
|-------|-------|---------|
| DEBUG | Fine-grained diagnostic information | Variable values, step-by-step execution |
| INFO | Wide events (request lifecycle, state changes) | Workflow step completed, phase transition |
| WARN | Potentially harmful situations | Deprecated configuration, near-violation |
| ERROR | Error events that don't stop execution | Hook validation failed, specification not found |
| FATAL | Critical errors that require immediate attention | Constitutional violation, system failure |

## 4. Interface

### 4.1 Logging Interface

```typescript
interface Logger {
  debug(message: string, context?: object): void;
  info(message: string, context?: object): void;
  warn(message: string, context?: object): void;
  error(message: string, context?: object): void;
  fatal(message: string, context?: object): void;
  
  withContext(context: object): Logger;
  withComponent(component: string): Logger;
}
```

### 4.2 Configuration Interface

```typescript
interface LoggingConfig {
  level: LogLevel;
  format: "json";
  outputs: LogOutput[];
  schema: LogSchema;
}

interface LogOutput {
  type: "file" | "stdout" | "audit";
  path?: string;
  level?: LogLevel;
}
```

## 5. Implementation Plan

### 5.1 Phase 0 Implementation
1. Create logger interface and schema definitions
2. Implement JSON structured logging formatter
3. Create logging hooks for workflow step tracking
4. Implement constitutional audit logging
5. Add correlation ID generation and propagation

### 5.2 Future Phase Integration
- Phase 1+: Integrate logger into kernel and subsequent components
- Extensibility: Allow custom log outputs and formatters
- Integration: Connect to external observability platforms

## 6. Testing Strategy

### 6.1 Unit Tests
- Logger interface compliance
- JSON schema validation
- Log level filtering
- Correlation ID generation

### 6.2 Integration Tests
- Hook logging integration
- Workflow step tracking
- Constitutional audit trail
- Cross-component logging consistency

### 6.3 E2E Tests
- Complete logging lifecycle
- Audit trail completeness
- Log output formatting

## 7. Documentation Requirements

- Logger interface documentation
- Schema field reference
- Configuration guide
- Hook integration guide
- Audit log format specification

## 8. Completion Criteria

- [ ] Logger interface defined and stable
- [ ] JSON structured logging implemented
- [ ] Standard log levels working correctly
- [ ] Correlation ID system functional
- [ ] Three logging areas operational
- [ ] All tests passing
- [ ] Documentation complete
- [ ] Constitutional compliance verified

## 9. Dependencies

- Phase 0 repository foundation (current)
- Hook system (already implemented)
- FOUNDING_ARCHITECTURE.md compliance

## 10. Risks and Mitigations

### Risk 1: Performance Impact
**Mitigation**: Asynchronous logging, configurable sampling

### Risk 2: Schema Drift
**Mitigation**: Strict schema validation, automated testing

### Risk 3: PII in Logs
**Mitigation**: PII detection and scrubbing, field-level encryption

## 11. References

- OpenTelemetry logging specification
- Structured logging best practices research
- Devin Local hook documentation
- FOUNDING_ARCHITECTURE.md constitutional requirements