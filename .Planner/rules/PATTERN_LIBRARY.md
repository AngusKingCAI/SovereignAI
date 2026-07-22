# Pattern Library

**Version**: 1.0  
**Last Updated**: 2026-07-22  
**Status**: Active

## Purpose
Repository of known anti-patterns and governance landmines identified through Round Table reviews. Used for Phase 6.0 self-check to catch common issues before expensive panelist rounds.

## Pattern Categories

### Governance Patterns

#### G1: Missing Security Compliance
**Pattern**: Plan lacks security review or compliance checks  
**Severity**: CRITICAL  
**Detection**: No security section, missing compliance with PR12 (Security)  
**Fix**: Add security review section with threat analysis and compliance checklist  
**Frequency**: High (7 occurrences in recent reviews)

#### G2: Unclear Approval Authority  
**Pattern**: Plan doesn't specify who approves what  
**Severity**: HIGH  
**Detection**: Missing approval chains, unclear decision authority  
**Fix**: Document approval matrix with clear authority levels  
**Frequency**: Medium (3 occurrences in recent reviews)

#### G3: Missing Rollback Plan  
**Pattern**: Plan includes deployment steps but no rollback strategy  
**Severity**: HIGH  
**Detection**: Deployment section present, rollback section missing  
**Fix**: Add rollback plan with specific rollback steps and triggers  
**Frequency**: Medium (4 occurrences in recent reviews)

### Structure Patterns

#### S1: Incomplete Manifest  
**Pattern**: Executor Manifest missing required components  
**Severity**: CRITICAL  
**Detection**: Missing Success Criteria, Exit Conditions, or Phase definitions  
**Fix**: Complete manifest with all required components per PR5  
**Frequency**: High (8 occurrences in recent reviews)

#### S2: Invalid Phase Dependencies  
**Pattern**: Phase dependencies are circular or impossible  
**Severity**: HIGH  
**Detection**: Phase A depends on Phase B, Phase B depends on Phase A  
**Fix**: Restructure phases to eliminate circular dependencies  
**Frequency**: Medium (2 occurrences in recent reviews)

#### S3: Missing Deliverable Definitions  
**Pattern**: Phases list steps but no deliverable definitions  
**Severity**: MEDIUM  
**Detection**: Phase steps present, deliverables section missing or incomplete  
**Fix**: Add deliverable definitions with acceptance criteria for each phase  
**Frequency**: High (6 occurrences in recent reviews)

### Content Patterns

#### C1: Vague Requirements  
**Pattern**: Requirements use vague terms (TBD, TBA, TODO, pending)  
**Severity**: MEDIUM  
**Detection**: Presence of placeholder terms in requirements section  
**Fix**: Replace vague terms with specific, actionable requirements  
**Frequency**: High (10 occurrences in recent reviews)

#### C2: Ambiguous Success Criteria  
**Pattern**: Success criteria are not measurable or testable  
**Severity**: HIGH  
**Detection**: Success criteria use subjective language (better, improved, optimized)  
**Fix**: Replace with measurable, testable criteria (response time < 200ms, error rate < 0.1%)  
**Frequency**: Medium (5 occurrences in recent reviews)

#### C3: Missing Context Section  
**Pattern**: Plan lacks context about problem, stakeholders, or constraints  
**Severity**: MEDIUM  
**Detection**: Context section missing or too brief (< 200 words)  
**Fix**: Add comprehensive context with problem statement, stakeholders, constraints  
**Frequency**: Medium (4 occurrences in recent reviews)

### Quality Patterns

#### Q1: Missing Test Plan  
**Pattern**: Plan includes implementation but no testing strategy  
**Severity**: HIGH  
**Detection**: Implementation steps present, test section missing or incomplete  
**Fix**: Add comprehensive test plan with unit, integration, and acceptance tests  
**Frequency**: High (7 occurrences in recent reviews)

#### Q2: Inconsistent Formatting  
**Pattern**: Plan uses inconsistent heading levels, formatting, or structure  
**Severity**: LOW  
**Detection**: Mixed heading levels (H1 → H3), inconsistent section ordering  
**Fix**: Standardize formatting per PR6 structure requirements  
**Frequency**: Medium (3 occurrences in recent reviews)

#### Q3: Missing Compliance Indicators  
**Pattern**: Plan lacks compliance indicators (✅/❌) for rule validation  
**Severity**: MEDIUM  
**Detection**: No compliance lines present in relevant sections  
**Fix**: Add compliance indicators after each major section  
**Frequency**: High (9 occurrences in recent reviews)

### Path Patterns

#### P1: Non-Repo-Relative Paths  
**Pattern**: Plan uses absolute paths instead of repo-relative paths  
**Severity**: HIGH  
**Detection**: Presence of Windows absolute paths (C:\), Unix absolute paths (/home/, /root/)  
**Fix**: Convert all paths to repo-relative format (./.Planner/, ./Agents/)  
**Frequency**: Medium (2 occurrences in recent reviews)

#### P2: Invalid Path References  
**Pattern**: Plan references files or directories that don't exist  
**Severity**: MEDIUM  
**Detection**: File references to non-existent paths  
**Fix**: Verify all path references exist or update to correct paths  
**Frequency**: Low (1 occurrence in recent reviews)

#### P3: Mixed Path Separators  
**Pattern**: Plan uses both forward slashes and backslashes inconsistently  
**Severity**: LOW  
**Detection**: Mixed usage of / and \ in paths  
**Fix**: Standardize to forward slashes for cross-platform compatibility  
**Frequency**: Medium (3 occurrences in recent reviews)

## Usage in Phase 6.0 Self-Check

The Pattern Library is used in Phase 6.0 self-check to:
1. **Anti-Pattern Detection**: Check plan against known anti-patterns
2. **Pattern Severity Assessment**: Prioritize fixes based on pattern severity
3. **Pattern Frequency Tracking**: Monitor which patterns occur most frequently
4. **Pattern Evolution**: Update library as new patterns emerge from Round Table reviews

## Pattern Evolution

Patterns are added to this library based on:
- **Frequency**: Patterns occurring in ≥3 Round Table reviews
- **Severity**: CRITICAL and HIGH severity patterns prioritized
- **Actionability**: Patterns with clear remediation steps
- **Governance Value**: Patterns that align with PR rules and governance principles

## Pattern Statistics

**Total Patterns**: 14  
**CRITICAL Patterns**: 3  
**HIGH Patterns**: 6  
**MEDIUM Patterns**: 4  
**LOW Patterns**: 1  

**Most Frequent Patterns**:
1. C1: Vague Requirements (10 occurrences)
2. Q3: Missing Compliance Indicators (9 occurrences)
3. S1: Incomplete Manifest (8 occurrences)
4. G1: Missing Security Compliance (7 occurrences)
5. Q1: Missing Test Plan (7 occurrences)

## Pattern Validation

Each pattern in this library includes:
- **Pattern Name**: Clear, descriptive name
- **Severity**: CRITICAL, HIGH, MEDIUM, or LOW
- **Detection**: Clear detection criteria or validation logic
- **Fix**: Specific remediation steps
- **Frequency**: Occurrence count in recent reviews

## Notes

- This library is a living document updated after each Round Table review
- Patterns are removed if they no longer occur in recent reviews
- New patterns are added based on findings from pattern analysis workflow
- Pattern severity may be adjusted based on governance impact