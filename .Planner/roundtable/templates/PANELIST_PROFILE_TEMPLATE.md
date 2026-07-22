# Panelist Profile Template

**Version**: 1.0  
**Last Updated**: 2026-07-22  
**Status**: Active

## Purpose
Define panelist profiles with competency assignments following BP-based best practices for Round Table evaluation.

## BP-Based Design Principles

- **One-Competency Assignment**: Each panelist owns one specific competency for depth evaluation
- **Topic-Based Format**: Panelists evaluate their assigned competency throughout the session
- **Credibility Matching**: Assign competencies based on panelist expertise and experience
- **Competency Isolation**: Prevent redundant questioning across panelists
- **3-5 Core Competencies**: Define 3-5 key evaluation dimensions per role

## Panelist Profile Template

```yaml
panelist_id: PANELIST-{ID}
name: "{Panelist Name}"
model: "{AI Model Used}"
specialty: "{Primary Domain Expertise}"

# Competency Assignment (BP: One competency per panelist)
assigned_competencies:
  - competency_id: COMP-{ID}
    name: "{Competency Name}"
    description: "{What this competency evaluates}"
    evaluation_criteria:
      - "{Specific criterion 1}"
      - "{Specific criterion 2}"
      - "{Specific criterion 3}"
    expertise_match: "{Why this panelist is credible for this competency}"

# Panelist Metadata
panelist_type: "{technical|domain|communication|impact|governance}"
session_role: "{evaluator|moderator|subject_matter_expert}"
experience_level: "{junior|intermediate|senior|expert}"

# Web Search Preferences (per Rule W3)
web_search_enabled: true
search_topics:
  - "{Topic 1 relevant to competency}"
  - "{Topic 2 relevant to competency}"
  - "{Topic 3 relevant to competency}"

# Scoring Authority
rubric_ownership:
  - competency_id: COMP-{ID}
    rubric_version: "{version}"
    calibration_status: "{calibrated|uncalibrated}"
```

## Competency Assignment Framework

### Core Competencies (3-5 Required)

**Technical Competency**:
- **Panelist**: Senior technical evaluator
- **Expertise**: System design, architecture, implementation patterns
- **Evaluation Criteria**: Technical feasibility, implementation quality, security considerations
- **Web Search Topics**: Best practices, technical standards, security frameworks

**Domain Competency**:
- **Panelist**: Domain expert
- **Expertise**: Industry knowledge, business context, user needs
- **Evaluation Criteria**: Domain relevance, user impact, business alignment
- **Web Search Topics**: Industry trends, user research, competitive analysis

**Communication Competency**:
- **Panelist**: Communication specialist
- **Expertise**: Clarity, documentation, stakeholder communication
- **Evaluation Criteria**: Plan clarity, documentation quality, stakeholder communication
- **Web Search Topics**: Communication best practices, documentation standards

**Cross-Team Impact Competency**:
- **Panelist**: Cross-functional specialist
- **Expertise**: Integration, dependencies, team coordination
- **Evaluation Criteria**: Integration feasibility, dependency management, team impact
- **Web Search Topics**: Integration patterns, dependency management, team coordination

**Governance Compliance Competency**:
- **Panelist**: Governance specialist
- **Expertise**: Rules, compliance, governance frameworks
- **Evaluation Criteria**: Rule compliance, governance alignment, process adherence
- **Web Search Topics**: Governance frameworks, compliance standards, rule patterns

## Example Panelist Profiles

### Example 1: Technical Evaluator
```yaml
panelist_id: PANELIST-001
name: "Architecture Reviewer"
model: "claude-3.5-sonnet"
specialty: "System Architecture and Design"

assigned_competencies:
  - competency_id: COMP-001
    name: "Technical Architecture"
    description: "Evaluates technical feasibility, implementation quality, and security considerations"
    evaluation_criteria:
      - "Architecture soundness and scalability"
      - "Implementation feasibility and complexity"
      - "Security and performance considerations"
    expertise_match: "Extensive experience in system design and architecture evaluation"

panelist_type: "technical"
session_role: "evaluator"
experience_level: "expert"

web_search_enabled: true
search_topics:
  - "System architecture best practices"
  - "Security implementation patterns"
  - "Performance optimization techniques"

rubric_ownership:
  - competency_id: COMP-001
    rubric_version: "1.0"
    calibration_status: "calibrated"
```

### Example 2: Domain Expert
```yaml
panelist_id: PANELIST-002
name: "Domain Specialist"
model: "gpt-4"
specialty: "AI/ML Domain Knowledge"

assigned_competencies:
  - competency_id: COMP-002
    name: "Domain Relevance"
    description: "Evaluates domain relevance, user impact, and business alignment"
    evaluation_criteria:
      - "Domain knowledge accuracy"
      - "User impact assessment"
      - "Business value alignment"
    expertise_match: "Deep expertise in AI/ML domain and industry trends"

panelist_type: "domain"
session_role: "evaluator"
experience_level: "expert"

web_search_enabled: true
search_topics:
  - "AI/ML industry trends"
  - "User research methodologies"
  - "Business value frameworks"

rubric_ownership:
  - competency_id: COMP-002
    rubric_version: "1.0"
    calibration_status: "calibrated"
```

## Compliance

Post compliance line after panelist profile creation:
`✅ Gate PANELIST-PROFILE PASS: Panelist profile created with competency assignment following BP principles`

## Evolution Condition

Panel profile structure changes when new competencies are defined or BP research updates competency assignment patterns.
