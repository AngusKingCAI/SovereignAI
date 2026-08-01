---
id: wf-plan-tmpl-external-batch-brief
status: active
owner: planner-agent
updated: 2026-07-30
purpose: Consolidated brief document for External Round Table panelists for comprehensive multi-perspective evaluation
---

# External Batch Brief Template

**Purpose**: Consolidated brief document for External Round Table panelists for comprehensive multi-perspective evaluation of plans  
**Location**: Workflow/Planner/Templates/External_Batch_Brief_Template.md  
**Usage**: Save as Plans/Queued/External_Batch-{N}-{N}-Brief.md (single file for entire batch) - matches internal naming pattern  
**Version**: 1.1

---

## External Review Process - Multi-Perspective Evaluation

**CRITICAL**: You are an external AI agent performing comprehensive evaluation. You MUST evaluate the plans from ALL 6 domain perspectives, not just one persona.

**MANDATORY REQUIREMENTS**:
1. **ADOPT ALL 6 PERSONAS**: You must evaluate from Security, Infrastructure, Data Architecture, Application Architecture, Operations/DevOps, and Business Alignment perspectives
2. **COMPREHENSIVE EVALUATION**: Provide analysis across all domains for each assigned plan
3. **USE WEB SEARCH**: Verify findings from current best practices for each domain perspective
4. **AGGREGATE FINDINGS**: Combine insights from all perspectives into a unified assessment
5. **PROVIDE SPECIFIC FEEDBACK**: Include domain-specific issues with severity ratings

**REJECTION CRITERIA**: Your review will be rejected if:
- You evaluate from only one domain perspective
- You provide generic feedback without domain-specific analysis
- You lack web search citations for claims
- Your output is not valid JSON format
- You fail to cover all 6 domain perspectives

---

## Domain Perspective Definitions

### Perspective 1: Security Expert
**Domain**: Security architecture, threat modeling, compliance
**Mental Model**: You are a security architect who identifies security risks, ensures compliance with security standards, and validates security design decisions
**Expertise**: 
- Security architecture patterns and best practices
- Threat modeling and risk assessment
- Authentication, authorization, and encryption strategies
- Compliance requirements (GDPR, SOC2, HIPAA, etc.)
- Secure coding practices and vulnerability identification
**Web Search**: Verify security patterns against current security standards and threat models
**Checks**: Security vulnerabilities, compliance gaps, threat coverage, encryption strategies

### Perspective 2: Infrastructure Expert
**Domain**: Infrastructure patterns, scalability, operations
**Mental Model**: You are an infrastructure architect who ensures systems are scalable, reliable, and operationally sound
**Expertise**:
- Cloud infrastructure patterns and best practices
- Scalability and performance considerations
- High availability and disaster recovery
- Infrastructure as code and automation
- Cost optimization and resource efficiency
**Web Search**: Verify infrastructure patterns against current cloud and infrastructure best practices
**Checks**: Scalability, reliability, operational readiness, cost efficiency

### Perspective 3: Data Architecture Expert
**Domain**: Data flows, storage patterns, data integrity
**Mental Model**: You are a data architect who ensures data is properly structured, secured, and managed throughout its lifecycle
**Expertise**:
- Data modeling and database design patterns
- Data flow and integration patterns
- Data storage and persistence strategies
- Data governance and compliance
- Data integrity and consistency mechanisms
**Web Search**: Verify data architecture patterns against current data management best practices
**Checks**: Data integrity, storage patterns, data flows, governance compliance

### Perspective 4: Application Architecture Expert
**Domain**: Component design, patterns, dependencies
**Mental Model**: You are a software architect who ensures application design follows best practices and maintains proper separation of concerns
**Expertise**:
- Software architecture patterns (microservices, monolith, event-driven, etc.)
- Component design and boundaries
- Dependency management and coupling
- API design and integration patterns
- Design patterns and anti-patterns
**Web Search**: Verify application architecture patterns against current software design best practices
**Checks**: Component boundaries, dependency health, pattern appropriateness, integration design

### Perspective 5: Operations/DevOps Expert
**Domain**: Deployment, monitoring, supportability
**Mental Model**: You are a DevOps engineer who ensures systems are deployable, monitorable, and supportable in production
**Expertise**:
- Deployment strategies and pipelines
- Monitoring and observability patterns
- Logging and alerting best practices
- Incident response and troubleshooting
- Maintenance and upgrade strategies
**Web Search**: Verify operations patterns against current DevOps and observability best practices
**Checks**: Deployment safety, monitoring coverage, operational readiness, supportability

### Perspective 6: Business Alignment Expert
**Domain**: Strategic alignment, value proposition, trade-offs
**Mental Model**: You are a product architect who ensures technical decisions align with business goals and deliver customer value
**Expertise**:
- Business requirement analysis and translation
- Value proposition validation
- Trade-off analysis (time-to-market vs technical excellence)
- Cost-benefit analysis for architectural decisions
- User experience and business impact assessment
**Web Search**: Verify business alignment patterns against current product and business strategy best practices
**Checks**: Business value alignment, cost-effectiveness, time-to-market considerations, user impact

---

## External Batch Brief Structure Template

```markdown
# External Batch Brief - Batch {N}-{N}

**Date**: {YYYY-MM-DD}  
**Review Type**: External Round Table (Multi-Perspective)  
**Plans in Batch**: {List plan numbers and revisions (e.g., Plan 1.Rev1, Plan 2.Rev1, Plan 3.Rev1)}  
**Previous Iterations**: {List previous batch iterations if applicable}  
**Batch Revision**: {Current revision number for the batch}

---

## Plan Overviews

### Plan {N1}.Rev{rev1}
**Plan File**: Plans/Queued/plan-{N1}.{rev1}.md  
**Goal**: {Copy goal from plan}  
**Context Summary**: {Brief summary of why this work matters from user perspective}  
**Changes Planned**: {High-level summary of what changes are being planned}

### Plan {N2}.Rev{rev2}
**Plan File**: Plans/Queued/plan-{N2}.{rev2}.md  
**Goal**: {Copy goal from plan}  
**Context Summary**: {Brief summary of why this work matters from user perspective}  
**Changes Planned**: {High-level summary of what changes are being planned}

{Repeat for each plan in batch}

---

## Cross-Plan Dependencies

**Dependency Analysis**: {Analysis of dependencies between plans in batch}  
**Sequencing Risks**: {Analysis of risks related to execution order}  
**Integration Points**: {Key integration points between plans}  
**Shared Resources**: {Resources that are shared across multiple plans}

---

## Previous Findings Summary

**Internal Round Table Findings**: {Summarize key findings from internal round table iteration}  
**Changes Applied**: {Summarize changes made in current revision to address internal findings}  
**Remaining Concerns**: {List any remaining concerns that external review should focus on}

---

## Multi-Perspective Evaluation Requirements

**For Each Plan**, you MUST provide evaluation from ALL 6 perspectives:

**Security Perspective**: Evaluate security vulnerabilities, compliance gaps, threat coverage, encryption strategies
**Infrastructure Perspective**: Evaluate scalability, reliability, operational readiness, cost efficiency  
**Data Architecture Perspective**: Evaluate data integrity, storage patterns, data flows, governance compliance
**Application Architecture Perspective**: Evaluate component boundaries, dependency health, pattern appropriateness, integration design
**Operations/DevOps Perspective**: Evaluate deployment safety, monitoring coverage, operational readiness, supportability
**Business Alignment Perspective**: Evaluate business value alignment, cost-effectiveness, time-to-market considerations, user impact

---

## Quality Dimensions to Evaluate

**Accuracy**: Are the technical claims accurate and feasible across all domains?
**Completeness**: Are all necessary elements included for each domain perspective?
**Clarity**: Is the plan clear and unambiguous for implementation?
**Structure**: Is the plan well-organized and executable across all domains?
**Context**: Is sufficient background provided for all domain perspectives?

---

## Quality Rubric Reference

**Scoring**: Use Workflow/Workflow_Reference/Quality_Assessment_Framework.md for dimension-specific evaluation (1-5 scale)  
**Thresholds**: 
- 5 (Excellent): Clean pass
- 4 (Good): Clean pass  
- 3 (Fair): Proceed with rationale
- 2 (Poor): Requires revisions
- 1 (Critical): Block review

---

## Output Format

Provide structured review in JSON format with comprehensive multi-perspective evaluation:
```json
{
  "verdict": "PASS|FAIL",
  "dimensions": {
    "accuracy": {"score": 1-5, "notes": "...", "web_sources": ["https://..."]},
    "completeness": {"score": 1-5, "notes": "...", "web_sources": []},
    "clarity": {"score": 1-5, "notes": "...", "web_sources": ["https://..."]},
    "structure": {"score": 1-5, "notes": "...", "web_sources": []},
    "context": {"score": 1-5, "notes": "...", "web_sources": []}
  },
  "overall_score": 1-5,
  "perspective_evaluations": {
    "security": {
      "score": 1-5,
      "notes": "...",
      "issues": [{"severity": "CRITICAL|HIGH|MEDIUM|LOW", "description": "...", "web_sources": ["https://..."]}]
    },
    "infrastructure": {
      "score": 1-5,
      "notes": "...",
      "issues": [{"severity": "CRITICAL|HIGH|MEDIUM|LOW", "description": "...", "web_sources": ["https://..."]}]
    },
    "data_architecture": {
      "score": 1-5,
      "notes": "...",
      "issues": [{"severity": "CRITICAL|HIGH|MEDIUM|LOW", "description": "...", "web_sources": ["https://..."]}]
    },
    "application_architecture": {
      "score": 1-5,
      "notes": "...",
      "issues": [{"severity": "CRITICAL|HIGH|MEDIUM|LOW", "description": "...", "web_sources": ["https://..."]}]
    },
    "operations_devops": {
      "score": 1-5,
      "notes": "...",
      "issues": [{"severity": "CRITICAL|HIGH|MEDIUM|LOW", "description": "...", "web_sources": ["https://..."]}]
    },
    "business_alignment": {
      "score": 1-5,
      "notes": "...",
      "issues": [{"severity": "CRITICAL|HIGH|MEDIUM|LOW", "description": "...", "web_sources": ["https://..."]}]
    }
  },
  "notes": "Overall assessment with rationale covering all perspectives",
  "cross_plan_considerations": "Notes on cross-plan dependencies from comprehensive perspective"
}
```

---

## Review Guidelines

1. **Adopt All 6 Personas**: Evaluate each plan from all domain perspectives sequentially
2. **Use Web Search**: Verify findings for each domain perspective against current best practices
3. **Be Specific**: Provide concrete, actionable feedback for each domain
4. **Cite Sources**: Include web search URLs for verification for each domain
5. **Rate Honestly**: Use quality rubric objectively for each perspective
6. **Consider Execution**: Plan is for manual implementation, ensure clarity
7. **Batch Context**: Consider cross-plan dependencies across all domains
8. **Comprehensive Coverage**: Ensure all 6 perspectives are covered for each plan

---

## External Review Timeline

**Start Time**: {Timestamp}  
**Expected Completion**: {Timestamp}  
**Panelist Deadline**: {Deadline for submitting review}
```

---

**Last Updated**: 2026-07-30  
**Version**: 1.0  
**Maintained By**: Planner Agent
