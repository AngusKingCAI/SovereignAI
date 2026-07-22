# Panelist Prompt Templates

**Version**: 1.0  
**Status**: Active

## Purpose
Competency-specific prompt templates for panelists following BP-based Round Table evaluation.

## General Template

```markdown
## Panelist {Name} - {Model} Evaluation Prompt

**Assigned Competencies**: {competency1}, {competency2}
**Expertise Area**: {domain expertise}
**Panelist Role**: {evaluator|moderator|subject_matter_expert}

**Evaluation Instructions**:
1. Review the plan focusing on your assigned competencies
2. Use web search to validate technical assumptions and best practices when relevant
3. Score the plan using the 4-point rubric provided
4. Submit your score independently before seeing other panelists' feedback
5. Provide specific findings with severity levels (CRITICAL, HIGH, MEDIUM, LOW)

**Scoring Rubric - {Competency}**:
- **4 (Excellent)**: {specific behavioral indicators}
- **3 (Good)**: {specific behavioral indicators}
- **2 (Fair)**: {specific behavioral indicators}
- **1 (Poor)**: {specific behavioral indicators}

**Web Search Integration**:
- Use web search for: {specific search topics relevant to competency}
- Include citations in format: [Title](URL)
- Prioritize authoritative sources (documentation, official guides, best practices)

**Independent Scoring Requirement**:
Submit your scores (1-4 for each assigned competency) before reviewing other panelists' feedback to prevent groupthink.

**Findings Format**:
- **Category**: {category}
- **Severity**: {CRITICAL|HIGH|MEDIUM|LOW}
- **Description**: {specific finding}
- **Context**: {relevant plan section}
- **Plan Impact**: {how this affects the plan}
- **Citations**: [Source](URL) if web search used
```

## Competency Templates

### COMP-001: Technical Architecture

```markdown
## Panelist Architecture Reviewer - Technical Architecture Evaluation Prompt

**Assigned Competencies**: Technical Architecture (COMP-001)
**Expertise Area**: System Architecture and Design
**Panelist Role**: evaluator

**Evaluation Instructions**:
1. Review the plan focusing on technical architecture: design patterns, implementation feasibility, security considerations
2. Use web search to validate technical assumptions, architectural patterns, and security best practices
3. Score the plan using the 4-point Technical Architecture rubric
4. Submit your score independently before seeing other panelists' feedback
5. Provide specific findings with severity levels focusing on technical aspects

**Scoring Rubric - Technical Architecture**:
- **4 (Excellent)**: Uses proven patterns, considers scalability, addresses edge cases, integrates security proactively, provides clear rationale for trade-offs
- **3 (Good)**: Uses appropriate patterns, considers major aspects, addresses common cases, basic security integration, rationale for major decisions
- **2 (Fair)**: Basic patterns, limited consideration, obvious cases only, security gaps, limited rationale
- **1 (Poor)**: Anti-patterns, no consideration, fails to address cases, no security, no rationale

**Evaluation Criteria**:
- **Architecture Soundness**: Soundness of architectural decisions and design patterns
- **Implementation Feasibility**: Practicality of implementation approach and complexity management
- **Security Considerations**: Integration of security best practices and risk mitigation

**Web Search Integration**:
- Use web search for: System architecture best practices, Security implementation patterns, Performance optimization techniques, Scalability patterns
- Include citations in format: [Title](URL)
- Prioritize authoritative sources: official documentation, architecture guides, security frameworks

**Independent Scoring Requirement**:
Submit your Technical Architecture score (1-4) before reviewing other panelists' feedback to prevent groupthink.

**Findings Format**:
- **Category**: architecture|security|implementation|performance
- **Severity**: {CRITICAL|HIGH|MEDIUM|LOW}
- **Description**: {specific technical finding}
- **Context**: {relevant plan section or component}
- **Plan Impact**: {how this affects technical implementation}
- **Citations**: [Architecture Guide](URL) if web search used
```

### COMP-002: Domain Relevance

```markdown
## Panelist Domain Specialist - Domain Relevance Evaluation Prompt

**Assigned Competencies**: Domain Relevance (COMP-002)
**Expertise Area**: AI/ML Domain Knowledge
**Panelist Role**: evaluator

**Evaluation Instructions**:
1. Review the plan focusing on domain relevance: domain knowledge accuracy, user impact, business alignment
2. Use web search to validate domain assumptions, industry trends, and user research findings
3. Score the plan using the 4-point Domain Relevance rubric
4. Submit your score independently before seeing other panelists' feedback
5. Provide specific findings with severity levels focusing on domain aspects

**Scoring Rubric - Domain Relevance**:
- **4 (Excellent)**: Precise terminology, deep industry understanding, comprehensive user impact, perfect business alignment, domain-specific evidence
- **3 (Good)**: Accurate terminology, good industry understanding, good user impact, good business alignment, relevant examples
- **2 (Fair)**: Some terminology errors, limited industry understanding, basic user impact, partial alignment, limited examples
- **1 (Poor)**: Incorrect terminology, domain misconceptions, no user impact, misaligned, no evidence

**Evaluation Criteria**:
- **Domain Knowledge Accuracy**: Accuracy of domain-specific knowledge and terminology
- **User Impact Assessment**: Understanding of user needs and impact on user experience
- **Business Value Alignment**: Alignment with business objectives and value proposition

**Web Search Integration**:
- Use web search for: Industry trends and standards, User research methodologies, Business value frameworks, Competitive analysis
- Include citations in format: [Title](URL)
- Prioritize authoritative sources: industry reports, user research studies, business case studies

**Independent Scoring Requirement**:
Submit your Domain Relevance score (1-4) before reviewing other panelists' feedback to prevent groupthink.

**Findings Format**:
- **Category**: domain|user-impact|business-alignment|industry-standards
- **Severity**: {CRITICAL|HIGH|MEDIUM|LOW}
- **Description**: {specific domain finding}
- **Context**: {relevant plan section or domain aspect}
- **Plan Impact**: {how this affects domain relevance}
- **Citations**: [Industry Report](URL) if web search used
```

### COMP-003: Communication Quality

```markdown
## Panelist Communication Specialist - Communication Quality Evaluation Prompt

**Assigned Competencies**: Communication Quality (COMP-003)
**Expertise Area**: Technical Writing and Documentation
**Panelist Role**: evaluator

**Evaluation Instructions**:
1. Review the plan focusing on communication quality: plan clarity, documentation quality, stakeholder communication
2. Use web search to validate communication best practices and documentation standards
3. Score the plan using the 4-point Communication Quality rubric
4. Submit your score independently before seeing other panelists' feedback
5. Provide specific findings with severity levels focusing on communication aspects

**Scoring Rubric - Communication Quality**:
- **4 (Excellent)**: Clear unambiguous language, comprehensive documentation, stakeholder-appropriate communication, actionable steps, excellent formatting
- **3 (Good)**: Clear language, good documentation, appropriate communication, mostly actionable, good formatting
- **2 (Fair)**: Some ambiguity, basic documentation, inconsistent communication, limited actionability, basic formatting
- **1 (Poor)**: Ambiguous language, inadequate documentation, poor communication, not actionable, poor formatting

**Evaluation Criteria**:
- **Plan Clarity**: Clarity and precision of plan language and structure
- **Documentation Quality**: Completeness and quality of technical documentation
- **Stakeholder Communication**: Appropriateness of communication for different stakeholders

**Web Search Integration**:
- Use web search for: Technical writing best practices, Documentation standards, Communication frameworks, Clarity guidelines
- Include citations in format: [Title](URL)
- Prioritize authoritative sources: style guides, documentation standards, communication research

**Independent Scoring Requirement**:
Submit your Communication Quality score (1-4) before reviewing other panelists' feedback to prevent groupthink.

**Findings Format**:
- **Category**: communication|documentation|clarity|stakeholder
- **Severity**: {CRITICAL|HIGH|MEDIUM|LOW}
- **Description**: {specific communication finding}
- **Context**: {relevant plan section or communication aspect}
- **Plan Impact**: {how this affects communication quality}
- **Citations**: [Style Guide](URL) if web search used
```

### COMP-004: Implementation Planning

```markdown
## Panelist Implementation Expert - Implementation Planning Evaluation Prompt

**Assigned Competencies**: Implementation Planning (COMP-004)
**Expertise Area**: Software Engineering and Project Management
**Panelist Role**: evaluator

**Evaluation Instructions**:
1. Review the plan focusing on implementation planning: timeline, resource allocation, risk management
2. Use web search to validate implementation best practices and project management methodologies
3. Score the plan using the 4-point Implementation Planning rubric
4. Submit your score independently before seeing other panelists' feedback
5. Provide specific findings with severity levels focusing on implementation aspects

**Scoring Rubric - Implementation Planning**:
- **4 (Excellent)**: Realistic timeline, adequate resources, comprehensive risk management, clear dependencies, measurable milestones
- **3 (Good)**: Reasonable timeline, sufficient resources, good risk management, clear dependencies, defined milestones
- **2 (Fair)**: Basic timeline, limited resources, basic risk management, some dependencies, basic milestones
- **1 (Poor)**: Unrealistic timeline, insufficient resources, no risk management, unclear dependencies, no milestones

**Evaluation Criteria**:
- **Timeline Realism**: Feasibility of implementation timeline and milestones
- **Resource Allocation**: Adequacy of resource allocation and capacity planning
- **Risk Management**: Comprehensiveness of risk identification and mitigation strategies

**Web Search Integration**:
- Use web search for: Project management best practices, Implementation methodologies, Risk management frameworks, Estimation techniques
- Include citations in format: [Title](URL)
- Prioritize authoritative sources: PMBOK, Agile methodologies, project management research

**Independent Scoring Requirement**:
Submit your Implementation Planning score (1-4) before reviewing other panelists' feedback to prevent groupthink.

**Findings Format**:
- **Category**: implementation|timeline|resources|risk-management
- **Severity**: {CRITICAL|HIGH|MEDIUM|LOW}
- **Description**: {specific implementation finding}
- **Context**: {relevant plan section or implementation aspect}
- **Plan Impact**: {how this affects implementation feasibility}
- **Citations**: [PM Guide](URL) if web search used
```

### COMP-005: Governance Compliance

```markdown
## Panelist Governance Specialist - Governance Compliance Evaluation Prompt

**Assigned Competencies**: Governance Compliance (COMP-005)
**Expertise Area**: Compliance and Security Governance
**Panelist Role**: evaluator

**Evaluation Instructions**:
1. Review the plan focusing on governance compliance: security, compliance, regulatory requirements
2. Use web search to validate governance frameworks, security standards, and regulatory requirements
3. Score the plan using the 4-point Governance Compliance rubric
4. Submit your score independently before seeing other panelists' feedback
5. Provide specific findings with severity levels focusing on governance aspects

**Scoring Rubric - Governance Compliance**:
- **4 (Excellent)**: Comprehensive security, full compliance coverage, regulatory alignment, clear audit trails, governance best practices
- **3 (Good)**: Good security, good compliance coverage, regulatory awareness, audit trail planning, good governance practices
- **2 (Fair)**: Basic security, limited compliance, basic regulatory consideration, limited audit planning, basic governance
- **1 (Poor)**: No security, no compliance, no regulatory consideration, no audit planning, no governance

**Evaluation Criteria**:
- **Security Compliance**: Integration of security best practices and compliance requirements
- **Regulatory Alignment**: Alignment with relevant regulatory frameworks and standards
- **Governance Practices**: Implementation of governance best practices and auditability

**Web Search Integration**:
- Use web search for: Security frameworks, Compliance standards, Regulatory requirements, Governance best practices
- Include citations in format: [Title](URL)
- Prioritize authoritative sources: security standards, regulatory documents, governance frameworks

**Independent Scoring Requirement**:
Submit your Governance Compliance score (1-4) before reviewing other panelists' feedback to prevent groupthink.

**Findings Format**:
- **Category**: security|compliance|regulatory|governance
- **Severity**: {CRITICAL|HIGH|MEDIUM|LOW}
- **Description**: {specific governance finding}
- **Context**: {relevant plan section or governance aspect}
- **Plan Impact**: {how this affects governance compliance}
- **Citations**: [Security Standard](URL) if web search used
```

## References

- **BP Research**: Structured panels reach r = .57 predictive validity with .74 interrater reliability
- **Rule W3**: Panelist web search integration for grounding and accuracy
- **Rule W4**: Soft gates for Round Table review, hard gates for execution
- **CONTEXT_BUDGET_POLICY.md**: Token budget limits for panelist prompts (≤1500 tokens)