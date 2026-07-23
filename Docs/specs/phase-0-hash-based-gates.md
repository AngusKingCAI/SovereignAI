# Phase 0: Hash-Based State Gates Specification

**Status**: Accepted  
**Phase**: 0 - Repository Foundation  
**Created**: 2026-07-24  
**Constitutional Compliance**: Verified

## 1. Overview

This specification defines a hash-based state verification system for enforcing Architect workflow gates without relying on Devin CLI hooks. The system uses cryptographic hashes to verify phase completion states and prevents progression to subsequent phases without proper verification.

## 2. Requirements

### 2.1 Functional Requirements
- **Hash-Based State Verification**: Each phase completion generates a SHA-256 hash of the phase state
- **State Tracking**: Hash values stored in tracking files with metadata (timestamp, phase, completion signature)
- **Pre-Phase Verification**: Scripts must verify previous phase hash before allowing work to begin
- **Tamper Evidence**: Hash chain structure detects state tampering
- **Explicit Enforcement**: Agent must explicitly call verification scripts before proceeding

### 2.2 Non-Functional Requirements
- **Deterministic**: Hash generation must be reproducible and deterministic
- **Minimal Coupling**: Gate system independent of phase implementation details
- **Observable**: All gate operations logged with audit trail
- **Replaceable**: Gate implementation can be upgraded without affecting phases
- **Fail-Closed**: Any verification failure prevents phase progression

## 3. Architecture

### 3.1 State File Structure

```json
{
  "phase": "0",
  "phase_name": "Repository Foundation",
  "completion_hash": "sha256:abc123...",
  "state_hash": "sha256:def456...",
  "timestamp": "2026-07-24T10:30:00Z",
  "completion_signature": "architect-approved",
  "previous_phase_hash": null,
  "state_files": [
    "docs/specs/phase-0-logging-foundation.md",
    "Scripts/Architect/Gates/verify-phase-complete.sh",
    "Scripts/Architect/Gates/record-phase-complete.sh"
  ],
  "metadata": {
    "specification_status": "accepted",
    "implementation_status": "complete",
    "test_status": "passing"
  }
}
```

### 3.2 Hash Chain Structure

Each phase state includes:
- **completion_hash**: Hash of phase deliverables and state
- **state_hash**: Hash of the entire state file
- **previous_phase_hash**: Reference to previous phase's state_hash
- **next_phase_hash**: Filled when next phase completes

This creates a tamper-evident chain: Phase 1 → Phase 2 → Phase 3

### 3.3 Verification Process

1. **Pre-Work Verification**: Before starting work on Phase N, verify Phase N-1 completion
2. **Hash Validation**: Compute current hash of Phase N-1 state files
3. **Chain Verification**: Verify hash chain integrity back to Phase 0
4. **Signature Verification**: Verify completion signature is valid
5. **Tamper Detection**: Check for any state file modifications

## 4. Interface

### 4.1 Verification Script Interface

```bash
#!/bin/bash
# verify-phase-complete.sh <phase_number>

# Exit codes:
# 0 - Verification passed, phase is complete
# 1 - Verification failed, phase not complete
# 2 - Hash mismatch, state tampered
# 3 - Chain broken, previous phase invalid
# 4 - Signature invalid, completion not authorized
```

### 4.2 Recording Script Interface

```bash
#!/bin/bash
# record-phase-complete.sh <phase_number> <completion_signature>

# Exit codes:
# 0 - Recording successful
# 1 - Invalid phase number
# 2 - State files missing
# 3 - Hash generation failed
# 4 - State file write failed
```

### 4.3 State Query Interface

```bash
#!/bin/bash
# query-phase-state.sh <phase_number>

# Output: JSON state information
# Exit codes:
# 0 - State found and valid
# 1 - State not found
# 2 - State invalid/tampered
```

## 5. Implementation Plan

### 5.1 Phase 0 Implementation
1. Create state file structure and schema
2. Implement hash generation functions (SHA-256)
3. Implement verification scripts for Phase 0 (null previous phase)
4. Implement recording scripts for Phase 0 completion
5. Implement query scripts for state inspection
6. Add hash chain verification logic
7. Create audit logging for all gate operations

### 5.2 Script Structure

```
Scripts/Architect/Gates/
├── gate-core/
│   ├── hash-functions.sh       # Core hash generation and verification
│   ├── state-file.sh           # State file read/write operations
│   ├── chain-verification.sh   # Hash chain integrity checks
│   └── audit-logging.sh        # Gate operation audit trail
├── verify-phase-complete.sh    # Main verification entry point
├── record-phase-complete.sh    # Main recording entry point
└── query-phase-state.sh        # State query entry point
```

### 5.3 State File Storage

```
Logs/Architect/Gates/
├── phase-0-state.json
├── phase-1-state.json
├── phase-2-state.json
└── audit-trail.log
```

### 5.4 Integration with AGENTS.md

Add to AGENTS.md:
```markdown
## Architect Workflow Gates

Before starting work on any phase, you MUST run:
\`Scripts/Architect/Gates/verify-phase-complete.sh <previous_phase_number>\`

Example: Before starting Phase 1, run:
\`Scripts/Architect/Gates/verify-phase-complete.sh 0\`

If verification fails, you MUST NOT proceed with the phase.

After completing a phase, you MUST run:
\`Scripts/Architect/Gates/record-phase-complete.sh <phase_number> architect-approved\`

This ensures proper state tracking and chain integrity.
```

## 6. Testing Strategy

### 6.1 Unit Tests
- Hash generation determinism
- State file serialization/deserialization
- Hash chain verification
- Signature validation
- Audit logging completeness

### 6.2 Integration Tests
- End-to-end phase completion recording
- Phase progression verification
- Tamper detection (modify state files, verify detection)
- Chain integrity (break chain, verify detection)
- Multi-phase progression (Phase 0 → 1 → 2)

### 6.3 Security Tests
- Hash collision resistance
- Signature spoofing attempts
- State file tampering scenarios
- Unauthorized completion attempts
- Rollback attack scenarios

## 7. Documentation Requirements

- Gate system architecture overview
- Script interface documentation
- State file format specification
- Hash algorithm documentation
- Integration guide for AGENTS.md
- Troubleshooting guide for gate failures
- Security considerations and threat model

## 8. Completion Criteria

- [x] Hash generation functions implemented and tested (SHA-256)
- [x] State file read/write operations implemented (without jq dependency)
- [x] Verification scripts working for Phase 0 (Scripts/Architect/Gates/)
- [x] Recording scripts working for Phase 0 (Scripts/Architect/Gates/)
- [x] Simple state query functionality (Scripts/Architect/Gates/)
- [x] Basic hash verification implemented
- [x] Audit logging for all gate operations (Logs/Architect/Gates/)
- [x] AGENTS.md integration completed
- [x] Phase progression blocking tested (blocks when previous phase incomplete)
- [x] Phase progression allowing tested (allows when previous phase complete)
- [x] Documentation complete
- [x] Constitutional compliance verified

**Implementation Notes**:
- jq dependency removed, using Python + grep/sed for JSON operations
- Full chain verification and query scripts implemented as simplified versions for Phase 0 scope
- Gate system successfully tested with Phase 0 → Phase 1 progression
- State files stored in Logs/Architect/Gates/ with cryptographic hash verification

## 9. Dependencies

- Phase 0 repository foundation (current)
- Existing Phase 0 Logging Foundation specification
- FOUNDING_ARCHITECTURE.md compliance
- AGENTS.md integration
- Cryptographic hash functions (SHA-256)

## 10. Risks and Mitigations

### Risk 1: Agent Bypassing Verification Scripts
**Mitigation**: AGENTS.md rules explicitly require verification, human review of compliance

### Risk 2: Hash Collisions
**Mitigation**: Use SHA-256 (cryptographically secure), implement salted hashing if needed

### Risk 3: State File Corruption
**Mitigation**: Redundant storage, backup mechanisms, recovery procedures

### Risk 4: Chain Breakage
**Mitigation**: Chain repair procedures, state recovery from audit logs

### Risk 5: Clock Skew Affecting Timestamps
**Mitigation**: Use UTC timestamps, implement time window tolerance

## 11. References

- Hashgate project (hash-bound approval concepts)
- gate-python (cryptographic primitives)
- SHA-256 specification
- FOUNDING_ARCHITECTURE.md constitutional requirements
- Phase 0 Logging Foundation specification
- Architect workflow documentation