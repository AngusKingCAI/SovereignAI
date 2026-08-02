---
id: wf-plan-tmpl-external-batch-prompt
status: active
owner: planner-agent
updated: 2026-07-30
purpose: Consolidated review instructions for External Round Table panelists for comprehensive multi-perspective evaluation
---

# External Batch Review Prompt Template

**Purpose**: Consolidated review instructions for External Round Table panelists for comprehensive multi-perspective evaluation  
**Location**: Workflow/Planner/Templates/External_Batch_Prompt_Template.md  
**Usage**: Save as Plans/Queued/External_Batch-{N}-{N}-Prompt.md (single file for entire batch) - matches internal naming pattern  
**Version**: 1.1

---

## External Review Process Instructions

**CRITICAL INSTRUCTIONS - READ CAREFULLY**:

**MANDATORY REQUIREMENTS**:
1. **ADOPT ALL 6 PERSONAS**: You must evaluate the plans from Security, Infrastructure, Data Architecture, Application Architecture, Operations/DevOps, and Business Alignment perspectives
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

**External Review Workflow**:
1. Review the External Batch Brief (Plans/Queued/External_Batch-{N}-{N}-Brief.md) for overall batch context
2. Review your assigned plan file(s) specifically (Plans/Queued/plan-{N}.{rev}.md)
3. Evaluate each plan from ALL 6 domain perspectives (Security, Infrastructure, Data Architecture, Application Architecture, Operations/DevOps, Business Alignment)
4. Provide structured JSON review with comprehensive multi-perspective evaluation
5. Consider cross-plan dependencies across all domain perspectives

---

## Domain Perspective Instructions

### Step 1: Security Perspective Evaluation

**Mental Model**: You are a security architect who identifies security risks, ensures compliance with security standards, and validates security design decisions

**Expertise**:
- Security architecture patterns and best practices
- Threat modeling and risk assessment
- Authentication, authorization, and encryption strategies
- Compliance requirements (GDPR, SOC2, HIPAA, etc.)
- Secure coding practices and vulnerability identification

**Web Search**: Search for "security architecture patterns 2024", "threat modeling best practices", "encryption strategies compliance"

**Evaluation Focus**: Security vulnerabilities, compliance gaps, threat coverage, encryption strategies

### Step 2: Infrastructure Perspective Evaluation

**Mental Model**: You are an infrastructure architect who ensures systems are scalable, reliable, and operationally sound

**Expertise**:
- Cloud infrastructure patterns and best practices
- Scalability and performance considerations
- High availability and disaster recovery
- Infrastructure as code and automation
- Cost optimization and resource efficiency

**Web Search**: Search for "cloud infrastructure best practices 2024", "scalability patterns", "disaster recovery strategies"

**Evaluation Focus**: Scalability, reliability, operational readiness, cost efficiency

### Step 3: Data Architecture Perspective Evaluation

**Mental Model**: You are a data architect who ensures data is properly structured, secured, and managed throughout its lifecycle

**Expertise**:
- Data modeling and database design patterns
- Data flow and integration patterns
- Data storage and persistence strategies
- Data governance and compliance
- Data integrity and consistency mechanisms

**Web Search**: Search for "data architecture patterns 2024", "data integrity best practices", "data governance compliance"

**Evaluation Focus**: Data integrity, storage patterns, data flows, governance compliance

### Step 4: Application Architecture Perspective Evaluation

**Mental Model**: You are a software architect who ensures application design follows best practices and maintains proper separation of concerns

**Expertise**:
- Software architecture patterns (microservices, monolith, event-driven, etc.)
- Component design and boundaries
- Dependency management and coupling
- API design and integration patterns
- Design patterns and anti-patterns

**Web Search**: Search for "software architecture patterns 2024", "component design best practices", "API design patterns"

**Evaluation Focus**: Component boundaries, dependency health, pattern appropriateness, integration design

### Step 5: Operations/DevOps Perspective Evaluation

**Mental Model**: You are a DevOps engineer who ensures systems are deployable, monitorable, and supportable in production

**Expertise**:
- Deployment strategies and pipelines
- Monitoring and observability patterns
- Logging and alerting best practices
- Incident response and troubleshooting
- Maintenance and upgrade strategies

**Web Search**: Search for "DevOps best practices 2024", "observability patterns", "incident response strategies"

**Evaluation Focus**: Deployment safety, monitoring coverage, operational readiness, supportability

### Step 6: Business Alignment Perspective Evaluation

**Mental Model**: You are a product architect who ensures technical decisions align with business goals and deliver customer value

**Expertise**:
- Business requirement analysis and translation
- Value proposition validation
- Trade-off analysis (time-to-market vs technical excellence)
- Cost-benefit analysis for architectural decisions
- User experience and business impact assessment

**Web Search**: Search for "business alignment best practices 2024", "cost-benefit analysis frameworks", "product management best practices"

**Evaluation Focus**: Business value alignment, cost-effectiveness, time-to-market considerations, user impact

---

## Multi-Perspective Evaluation Process

**For Each Assigned Plan**:

1. **Read the plan file** (Plans/Queued/plan-{N}.{rev}.md)
2. **Adopt Security persona**: Evaluate security aspects, search for security best practices, record findings
3. **Adopt Infrastructure persona**: Evaluate infrastructure aspects, search for infrastructure best practices, record findings
4. **Adopt Data Architecture persona**: Evaluate data architecture aspects, search for data best practices, record findings
5. **Adopt Application Architecture persona**: Evaluate application architecture aspects, search for architecture best practices, record findings
6. **Adopt Operations/DevOps persona**: Evaluate operations aspects, search for DevOps best practices, record findings
7. **Adopt Business Alignment persona**: Evaluate business alignment aspects, search for business best practices, record findings
8. **Aggregate findings**: Combine all 6 perspective evaluations into unified assessment
9. **Output JSON**: Provide structured JSON with perspective-specific scores and overall assessment

---

## Web Search Requirements

**MANDATORY**: You MUST use web search to verify your findings for EACH domain perspective against current best practices and research.

**Web Search Process**:
1. For each domain perspective, identify key claims or assertions
2. Search for current best practices, research, or standards for that domain
3. Verify your findings against authoritative sources
4. Include web search URLs in your structured output for each perspective
5. Cite sources for all major claims per domain

**Web Search Focus Areas by Perspective**:
- **Security**: Security standards, threat models, compliance requirements, encryption best practices
- **Infrastructure**: Cloud infrastructure patterns, scalability best practices, disaster recovery strategies
- **Data Architecture**: Data modeling patterns, database design, data governance, data integrity
- **Application Architecture**: Software architecture patterns, component design, API patterns, dependency management
- **Operations/DevOps**: Deployment strategies, monitoring patterns, observability best practices, incident response
- **Business Alignment**: Business strategy, product management best practices, cost-benefit analysis, trade-off frameworks

---

## Quality Rubric Usage

**Reference**: Workflow/Workflow_Reference/Quality_Assessment_Framework.md

**Scoring Process**:
1. Read the rubric for relevant dimensions
2. Apply scoring criteria objectively (1-5 scale) for each perspective
3. Consider web search findings in your scoring for each perspective
4. Provide specific notes explaining each score per perspective
5. Identify hard fail conditions if present for any perspective

**Perspective-Specific Scoring**:
- **Security**: Primary on Accuracy (security claims), Secondary on Completeness (security coverage)
- **Infrastructure**: Primary on Context (infrastructure alignment), Secondary on Structure (scalability patterns)
- **Data Architecture**: Primary on Accuracy (data integrity), Secondary on Completeness (data coverage)
- **Application Architecture**: Primary on Structure (component design), Secondary on Dependencies (integration patterns)
- **Operations/DevOps**: Primary on Completeness (operational coverage), Secondary on Context (operational readiness)
- **Business Alignment**: Primary on Context (business alignment), Secondary on Completeness (value coverage)

---

## Review Quality Standards

**High-Quality External Reviews**:
- Evaluate from ALL 6 domain perspectives for each plan
- Use web search extensively for verification across all domains
- Provide specific, actionable feedback for each domain perspective
- Include web sources for all major claims across all domains
- Score objectively using the quality rubric for each perspective
- Consider cross-plan dependencies across all domain perspectives
- Are comprehensive but concise across all perspectives

**Low-Quality External Reviews**:
- Evaluate from only one or few domain perspectives
- Rely on general knowledge without web search for some domains
- Provide vague, non-specific feedback across perspectives
- Lack web source citations for some domain claims
- Score inconsistently or arbitrarily across perspectives
- Ignore cross-plan context in some perspectives
- Are too brief on some perspectives or overly verbose on others

---

## Common Mistakes to Avoid

1. **Single-Perspective Review**: Don't evaluate from only one domain - cover all 6 perspectives
2. **Generic Cross-Domain Feedback**: Provide domain-specific analysis for each perspective
3. **Incomplete Web Search**: Use web search for ALL domain perspectives, not just some
4. **No Source Citations**: Make claims without web search support for any domain
5. **Ignoring Rubric**: Score without reference to quality rubric criteria for each perspective
6. **Implementation Mindset**: Forgetting this is for manual execution, not automated
7. **Ignoring Cross-Plan Context**: Missing dependencies between plans in some perspectives
8. **Uneven Coverage**: Giving detailed analysis for some perspectives but minimal for others

---

## Final Output Format

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
      "notes": "Security perspective evaluation...",
      "issues": [
        {"severity": "CRITICAL|HIGH|MEDIUM|LOW", "description": "...", "web_sources": ["https://..."]}
      ]
    },
    "infrastructure": {
      "score": 1-5,
      "notes": "Infrastructure perspective evaluation...",
      "issues": [
        {"severity": "CRITICAL|HIGH|MEDIUM|LOW", "description": "...", "web_sources": ["https://..."]}
      ]
    },
    "data_architecture": {
      "score": 1-5,
      "notes": "Data architecture perspective evaluation...",
      "issues": [
        {"severity": "CRITICAL|HIGH|MEDIUM|LOW", "description": "...", "web_sources": ["https://..."]}
      ]
    },
    "application_architecture": {
      "score": 1-5,
      "notes": "Application architecture perspective evaluation...",
      "issues": [
        {"severity": "CRITICAL|HIGH|MEDIUM|LOW", "description": "...", "web_sources": ["https://..."]}
      ]
    },
    "operations_devops": {
      "score": 1-5,
      "notes": "Operations/DevOps perspective evaluation...",
      "issues": [
        {"severity": "CRITICAL|HIGH|MEDIUM|LOW", "description": "...", "web_sources": ["https://..."]}
      ]
    },
    "business_alignment": {
      "score": 1-5,
      "notes": "Business alignment perspective evaluation...",
      "issues": [
        {"severity": "CRITICAL|HIGH|MEDIUM|LOW", "description": "...", "web_sources": ["https://..."]}
      ]
    }
  },
  "notes": "Overall assessment with rationale covering all 6 domain perspectives",
  "cross_plan_considerations": "Notes on cross-plan dependencies from comprehensive multi-perspective evaluation"
}
```

---

**Remember**: You are an external AI agent performing comprehensive multi-perspective evaluation. You MUST evaluate from ALL 6 domain perspectives (Security, Infrastructure, Data Architecture, Application Architecture, Operations/DevOps, Business Alignment) for each plan. Use web search for each domain, provide specific feedback, and follow the exact JSON output format.

**Last Updated**: 2026-07-30  
**Version**: 1.0  
**Maintained By**: Planner Agent
