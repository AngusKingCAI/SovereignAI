# Competency Assignment Framework

**Version**: 1.0  
**Last Updated**: 2026-07-22  
**Status**: Active

## Purpose
Provide systematic framework for assigning competencies to panelists following BP-based best practices for Round Table evaluation.

## BP-Based Assignment Principles

### Core Principles (Per Research)

1. **One-Competency Assignment**: Each panelist owns one specific competency for depth evaluation
2. **Topic-Based Format**: Panelists evaluate their assigned competency throughout the session (not time-based)
3. **Credibility Matching**: Assign competencies based on panelist expertise and experience
4. **Competency Isolation**: Prevent redundant questioning across panelists
5. **3-5 Core Competencies**: Define 3-5 key evaluation dimensions per role

### Assignment Strategy

**Panelist Count vs Competency Count**:
- **6 Panelists**: 3-5 competencies (some panelists may share competencies for cross-validation)
- **Optimal**: 5 panelists for 5 competencies (1:1 assignment)
- **Minimal**: 3 panelists for 3 competencies (1:1 assignment)

**Competency Selection Priority**:
1. **Technical Skill**: Implementation feasibility, architecture quality
2. **Domain Knowledge**: Industry relevance, user impact, business alignment
3. **Communication**: Clarity, documentation quality, stakeholder communication
4. **Cross-Team Impact**: Integration feasibility, dependency management
5. **Governance Compliance**: Rule adherence, process compliance, governance alignment

## Competency Definition Framework

### Competency Structure

```yaml
competency_id: COMP-{ID}
name: "{Competency Name}"
description: "{What this competency evaluates and why it matters}"
importance_level: "{critical|high|medium|low}"
weight: {1-10}  # Relative importance for overall scoring

# Evaluation Criteria (3-5 specific criteria)
evaluation_criteria:
  - criterion_id: CRIT-{ID}
    name: "{Criterion Name}"
    description: "{What this criterion evaluates}"
    weight: {1-5}  # Relative weight within competency
    behavioral_indicators:
      - "{Observable behavior for excellent performance}"
      - "{Observable behavior for poor performance}"

# Panelist Requirements
panelist_requirements:
  expertise_level: "{junior|intermediate|senior|expert}"
  domain_experience: "{Required domain experience}"
  technical_background: "{Required technical background}"

# Web Search Topics (per Rule W3)
web_search_topics:
  - "{Topic 1 for evidence gathering}"
  - "{Topic 2 for evidence gathering}"
  - "{Topic 3 for evidence gathering}"
```

## Standard Competency Library

### COMP-001: Technical Architecture
```yaml
competency_id: COMP-001
name: "Technical Architecture"
description: "Evaluates technical feasibility, implementation quality, and system design principles"
importance_level: "critical"
weight: 10

evaluation_criteria:
  - criterion_id: CRIT-001
    name: "Architecture Soundness"
    description: "Soundness of architectural decisions and design patterns"
    weight: 5
    behavioral_indicators:
      - "Excellent: Uses proven patterns, considers scalability, addresses edge cases"
      - "Poor: Uses anti-patterns, ignores scalability, has obvious design flaws"
  
  - criterion_id: CRIT-002
    name: "Implementation Feasibility"
    description: "Practicality of implementation approach and complexity management"
    weight: 3
    behavioral_indicators:
      - "Excellent: Realistic timeline, appropriate complexity, clear dependencies"
      - "Poor: Unrealistic timeline, excessive complexity, unclear dependencies"
  
  - criterion_id: CRIT-003
    name: "Security Considerations"
    description: "Integration of security best practices and risk mitigation"
    weight: 4
    behavioral_indicators:
      - "Excellent: Proactive security measures, threat modeling, defense in depth"
      - "Poor: No security considerations, obvious vulnerabilities, reactive approach"

panelist_requirements:
  expertise_level: "expert"
  domain_experience: "System architecture, software engineering"
  technical_background: "Strong technical background in software design"

web_search_topics:
  - "System architecture best practices"
  - "Security implementation patterns"
  - "Performance optimization techniques"
```

### COMP-002: Domain Relevance
```yaml
competency_id: COMP-002
name: "Domain Relevance"
description: "Evaluates domain knowledge accuracy, user impact, and business alignment"
importance_level: "high"
weight: 8

evaluation_criteria:
  - criterion_id: CRIT-004
    name: "Domain Knowledge Accuracy"
    description: "Accuracy of domain-specific knowledge and terminology"
    weight: 4
    behavioral_indicators:
      - "Excellent: Precise domain terminology, accurate concepts, industry alignment"
      - "Poor: Incorrect terminology, misconceptions, industry misalignment"
  
  - criterion_id: CRIT-005
    name: "User Impact Assessment"
    description: "Understanding of user needs and impact on user experience"
    weight: 3
    behavioral_indicators:
      - "Excellent: User-centered thinking, impact consideration, accessibility awareness"
      - "Poor: User-agnostic thinking, ignores user impact, accessibility blind spots"
  
  - criterion_id: CRIT-006
    name: "Business Value Alignment"
    description: "Alignment with business objectives and value proposition"
    weight: 3
    behavioral_indicators:
      - "Excellent: Clear business value, strategic alignment, ROI consideration"
      - "Poor: Unclear business value, misaligned priorities, no ROI consideration"

panelist_requirements:
  expertise_level: "expert"
  domain_experience: "Industry domain, business analysis"
  technical_background: "Domain-specific knowledge"

web_search_topics:
  - "Industry trends and standards"
  - "User research methodologies"
  - "Business value frameworks"
```

### COMP-003: Communication Quality
```yaml
competency_id: COMP-003
name: "Communication Quality"
description: "Evaluates plan clarity, documentation quality, and stakeholder communication"
importance_level: "high"
weight: 7

evaluation_criteria:
  - criterion_id: CRIT-007
    name: "Plan Clarity"
    description: "Clarity of plan language and structure"
    weight: 4
    behavioral_indicators:
      - "Excellent: Clear language, logical structure, unambiguous instructions"
      - "Poor: Ambiguous language, confusing structure, unclear instructions"
  
  - criterion_id: CRIT-008
    name: "Documentation Quality"
    description: "Quality and completeness of documentation"
    weight: 3
    behavioral_indicators:
      - "Excellent: Comprehensive documentation, clear examples, maintainable format"
      - "Poor: Incomplete documentation, no examples, unmaintainable format"

panelist_requirements:
  expertise_level: "intermediate"
  domain_experience: "Technical writing, documentation"
  technical_background: "Communication and documentation best practices"

web_search_topics:
  - "Technical writing best practices"
  - "Documentation standards"
  - "Communication frameworks"
```

### COMP-004: Cross-Team Impact
```yaml
competency_id: COMP-004
name: "Cross-Team Impact"
description: "Evaluates integration feasibility, dependency management, and team coordination"
importance_level: "medium"
weight: 6

evaluation_criteria:
  - criterion_id: CRIT-009
    name: "Integration Feasibility"
    description: "Feasibility of integration with existing systems and teams"
    weight: 3
    behavioral_indicators:
      - "Excellent: Clear integration path, minimal disruption, well-defined interfaces"
      - "Poor: Unclear integration, high disruption, undefined interfaces"
  
  - criterion_id: CRIT-010
    name: "Dependency Management"
    description: "Management of dependencies and external requirements"
    weight: 3
    behavioral_indicators:
      - "Excellent: Clear dependencies, realistic external requirements, risk mitigation"
      - "Poor: Unclear dependencies, unrealistic requirements, no risk mitigation"

panelist_requirements:
  expertise_level: "senior"
  domain_experience: "Systems integration, project management"
  technical_background: "Integration patterns and dependency management"

web_search_topics:
  - "Integration patterns and best practices"
  - "Dependency management strategies"
  - "Team coordination frameworks"
```

### COMP-005: Governance Compliance
```yaml
competency_id: COMP-005
name: "Governance Compliance"
description: "Evaluates rule adherence, process compliance, and governance alignment"
importance_level: "medium"
weight: 5

evaluation_criteria:
  - criterion_id: CRIT-011
    name: "Rule Adherence"
    description: "Compliance with established rules and governance frameworks"
    weight: 3
    behavioral_indicators:
      - "Excellent: Follows all rules, respects governance, proactive compliance"
      - "Poor: Violates rules, ignores governance, reactive compliance"
  
  - criterion_id: CRIT-012
    name: "Process Alignment"
    description: "Alignment with established processes and workflows"
    weight: 2
    behavioral_indicators:
      - "Excellent: Follows established processes, respects workflows, consistent approach"
      - "Poor: Bypasses processes, ignores workflows, inconsistent approach"

panelist_requirements:
  expertise_level: "intermediate"
  domain_experience: "Governance frameworks, process management"
  technical_background: "Governance and compliance knowledge"

web_search_topics:
  - "Governance frameworks and standards"
  - "Compliance best practices"
  - "Process management methodologies"
```

## Panelist Assignment Algorithm

### Step 1: Competency Selection
```python
def select_competencies(plan_context):
    """
    Select 3-5 competencies based on plan type and complexity.
    Technical plans always include COMP-001 (Technical Architecture).
    Domain-specific plans include COMP-002 (Domain Relevance).
    """
    base_competencies = [COMP-001]  # Always include technical
    
    if plan_context.domain_specific:
        base_competencies.append(COMP-002)
    
    if plan_context.communication_critical:
        base_competencies.append(COMP-003)
    
    if plan_context.cross_team_impact:
        base_competencies.append(COMP-004)
    
    if plan_context.governance_critical:
        base_competencies.append(COMP-005)
    
    # Limit to 5 competencies maximum
    return base_competencies[:5]
```

### Step 2: Panelist Assignment
```python
def assign_panelists_to_competencies(competencies, available_panelists):
    """
    Assign panelists to competencies based on expertise matching.
    Each panelist gets one primary competency (BP principle).
    """
    assignments = []
    
    for competency in competencies:
        # Find panelist with matching expertise
        best_panelist = find_best_panelist(competency, available_panelists)
        
        if best_panelist:
            assignments.append({
                'panelist': best_panelist,
                'competency': competency,
                'assignment_type': 'primary'
            })
            available_panelists.remove(best_panelist)
    
    return assignments
```

### Step 3: Credibility Verification
```python
def verify_credibility(panelist, competency):
    """
    Verify that panelist has sufficient credibility for assigned competency.
    """
    panelist_expertise = panelist.expertise_level
    required_expertise = competency.panelist_requirements.expertise_level
    
    expertise_levels = ['junior', 'intermediate', 'senior', 'expert']
    
    if expertise_levels.index(panelist_expertise) >= expertise_levels.index(required_expertise):
        return True
    else:
        return False
```

## Assignment Templates

### Template 1: Technical-Heavy Plan (5 Competencies)
```yaml
competencies: [COMP-001, COMP-002, COMP-003, COMP-004, COMP-005]
panelist_assignments:
  - panelist: "Architecture Reviewer"
    competency: COMP-001
    assignment_type: "primary"
  - panelist: "Domain Specialist"
    competency: COMP-002
    assignment_type: "primary"
  - panelist: "Communication Specialist"
    competency: COMP-003
    assignment_type: "primary"
  - panelist: "Integration Expert"
    competency: COMP-004
    assignment_type: "primary"
  - panelist: "Governance Specialist"
    competency: COMP-005
    assignment_type: "primary"
```

### Template 2: Domain-Focused Plan (3 Competencies)
```yaml
competencies: [COMP-001, COMP-002, COMP-003]
panelist_assignments:
  - panelist: "Architecture Reviewer"
    competency: COMP-001
    assignment_type: "primary"
  - panelist: "Domain Specialist"
    competency: COMP-002
    assignment_type: "primary"
  - panelist: "Communication Specialist"
    competency: COMP-003
    assignment_type: "primary"
```

## Compliance

Post compliance line after competency assignment:
`✅ Gate COMPETENCY-ASSIGNMENT PASS: Competencies assigned following BP principles (one-competency-per-panelist, credibility matching)`

## Evolution Condition

Competency assignment framework evolves when new competencies are defined or BP research updates assignment patterns.
