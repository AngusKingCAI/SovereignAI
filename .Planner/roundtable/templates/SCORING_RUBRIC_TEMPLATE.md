# 4-Point Scoring Rubric Template

**Version**: 1.0  
**Last Updated**: 2026-07-22  
**Status**: Active

## Purpose
Provide 4-point scoring rubrics with concrete behavioral indicators for panelist evaluation following BP-based best practices.

## BP-Based Rubric Design Principles

### Core Principles (Per Research)

1. **4-Point Scale**: Use 4-point scale (1-4) to avoid neutral middle-ground bias
2. **Concrete Behavioral Indicators**: Define specific observable behaviors for each score level
3. **Competency-Specific**: Each competency has its own rubric with relevant criteria
4. **Eliminate Subjectivity**: Rubrics eliminate "gut-feel" scoring with clear behavioral anchors
5. **Calibration-Ready**: Rubrics designed for panelist calibration sessions

### Scoring Scale Definition

- **4 (Excellent)**: Exceeds expectations, demonstrates mastery, no improvements needed
- **3 (Good)**: Meets expectations, solid performance, minor improvements possible
- **2 (Fair)**: Below expectations, significant issues, major improvements needed
- **1 (Poor)**: Fails expectations, critical issues, fundamental rework needed

## Rubric Template Structure

```yaml
rubric_id: RUBRIC-{COMPETENCY_ID}
competency_id: COMP-{ID}
competency_name: "{Competency Name}"
rubric_version: "1.0"
calibration_status: "{calibrated|uncalibrated}"

# Scoring Scale with Behavioral Indicators
scoring_scale:
  - score: 4
    label: "Excellent"
    description: "{Overall description of excellent performance}"
    behavioral_indicators:
      - "{Specific observable behavior 1}"
      - "{Specific observable behavior 2}"
      - "{Specific observable behavior 3}"
    anti_patterns:
      - "{What to avoid for this score level}"
  
  - score: 3
    label: "Good"
    description: "{Overall description of good performance}"
    behavioral_indicators:
      - "{Specific observable behavior 1}"
      - "{Specific observable behavior 2}"
      - "{Specific observable behavior 3}"
    anti_patterns:
      - "{What to avoid for this score level}"
  
  - score: 2
    label: "Fair"
    description: "{Overall description of fair performance}"
    behavioral_indicators:
      - "{Specific observable behavior 1}"
      - "{Specific observable behavior 2}"
      - "{Specific observable behavior 3}"
    anti_patterns:
      - "{What to avoid for this score level}"
  
  - score: 1
    label: "Poor"
    description: "{Overall description of poor performance}"
    behavioral_indicators:
      - "{Specific observable behavior 1}"
      - "{Specific observable behavior 2}"
      - "{Specific observable behavior 3}"
    anti_patterns:
      - "{What to avoid for this score level}"

# Criterion-Specific Scoring
criteria_scoring:
  - criterion_id: CRIT-{ID}
    criterion_name: "{Criterion Name}"
    weight: {1-5}
    scoring_guidance:
      - "What to look for when scoring this criterion"
      - "Common pitfalls to avoid"
      - "Evidence requirements"
```

## Competency-Specific Rubrics

### RUBRIC-001: Technical Architecture Rubric

```yaml
rubric_id: RUBRIC-001
competency_id: COMP-001
competency_name: "Technical Architecture"
rubric_version: "1.0"
calibration_status: "calibrated"

scoring_scale:
  - score: 4
    label: "Excellent"
    description: "Architecture demonstrates exceptional technical soundness with comprehensive consideration of all aspects"
    behavioral_indicators:
      - "Uses proven architectural patterns appropriate for the problem domain"
      - "Considers scalability, maintainability, and extensibility in design decisions"
      - "Addresses edge cases and failure modes comprehensively"
      - "Integrates security best practices proactively"
      - "Provides clear rationale for architectural trade-offs"
    anti_patterns:
      - "Over-engineering for simple problems"
      - "Using complex patterns when simple solutions suffice"
  
  - score: 3
    label: "Good"
    description: "Architecture demonstrates solid technical soundness with consideration of major aspects"
    behavioral_indicators:
      - "Uses appropriate architectural patterns for the problem domain"
      - "Considers scalability and maintainability in major design decisions"
      - "Addresses common edge cases and failure modes"
      - "Integrates basic security practices"
      - "Provides rationale for major architectural decisions"
    anti_patterns:
      - "Missing consideration of important aspects"
      - "Insufficient rationale for key decisions"
  
  - score: 2
    label: "Fair"
    description: "Architecture demonstrates basic technical soundness but has significant gaps"
    behavioral_indicators:
      - "Uses architectural patterns but may not be optimal for the problem"
      - "Limited consideration of scalability and maintainability"
      - "Addresses only obvious edge cases"
      - "Basic security integration with notable gaps"
      - "Limited rationale for architectural decisions"
    anti_patterns:
      - "Using patterns inappropriate for the problem"
      - "Ignoring critical aspects like security or scalability"
  
  - score: 1
    label: "Poor"
    description: "Architecture demonstrates fundamental technical flaws"
    behavioral_indicators:
      - "Uses anti-patterns or inappropriate architectural choices"
      - "No consideration of scalability or maintainability"
      - "Fails to address edge cases and failure modes"
      - "No security integration or obvious security flaws"
      - "No rationale for architectural decisions"
    anti_patterns:
      - "Architecture that will clearly fail in production"
      - "Security vulnerabilities that are obvious and critical"

criteria_scoring:
  - criterion_id: CRIT-001
    criterion_name: "Architecture Soundness"
    weight: 5
    scoring_guidance:
      - "Look for appropriate use of design patterns"
      - "Check if architectural decisions align with problem requirements"
      - "Evaluate consideration of non-functional requirements"
      - "Evidence: Pattern descriptions, architectural diagrams, rationale documentation"
  
  - criterion_id: CRIT-002
    criterion_name: "Implementation Feasibility"
    weight: 3
    scoring_guidance:
      - "Assess if implementation timeline is realistic"
      - "Evaluate complexity management approach"
      - "Check if dependencies are clearly identified"
      - "Evidence: Implementation timeline, complexity analysis, dependency mapping"
  
  - criterion_id: CRIT-003
    criterion_name: "Security Considerations"
    weight: 4
    scoring_guidance:
      - "Look for proactive security measures"
      - "Check if threat modeling is considered"
      - "Evaluate defense-in-depth approach"
      - "Evidence: Security requirements, threat analysis, security testing plan"
```

### RUBRIC-002: Domain Relevance Rubric

```yaml
rubric_id: RUBRIC-002
competency_id: COMP-002
competency_name: "Domain Relevance"
rubric_version: "1.0"
calibration_status: "calibrated"

scoring_scale:
  - score: 4
    label: "Excellent"
    description: "Demonstrates exceptional domain knowledge with precise alignment to industry standards and user needs"
    behavioral_indicators:
      - "Uses precise domain terminology and concepts accurately"
      - "Demonstrates deep understanding of industry trends and standards"
      - "Shows comprehensive user impact consideration"
      - "Aligns perfectly with business objectives and value proposition"
      - "Provides domain-specific evidence and examples"
    anti_patterns:
      - "Over-complicating with unnecessary domain jargon"
      - "Making assumptions without domain validation"
  
  - score: 3
    label: "Good"
    description: "Demonstrates solid domain knowledge with good alignment to industry standards and user needs"
    behavioral_indicators:
      - "Uses domain terminology and concepts accurately"
      - "Demonstrates understanding of major industry trends"
      - "Shows good user impact consideration"
      - "Aligns well with business objectives"
      - "Provides relevant domain-specific examples"
    anti_patterns:
      - "Minor inaccuracies in domain terminology"
      - "Limited consideration of some user needs"
  
  - score: 2
    label: "Fair"
    description: "Demonstrates basic domain knowledge with some alignment issues"
    behavioral_indicators:
      - "Uses domain terminology with some inaccuracies"
      - "Demonstrates limited understanding of industry trends"
      - "Shows basic user impact consideration"
      - "Partial alignment with business objectives"
      - "Limited domain-specific examples"
    anti_patterns:
      - "Significant terminology errors"
      - "Misalignment with industry standards"
  
  - score: 1
    label: "Poor"
    description: "Demonstrates fundamental domain knowledge errors"
    behavioral_indicators:
      - "Uses domain terminology incorrectly"
      - "Demonstrates misunderstanding of basic domain concepts"
      - "Shows little or no user impact consideration"
      - "Misaligned with business objectives"
      - "No domain-specific evidence or examples"
    anti_patterns:
      - "Fundamental misconceptions about the domain"
      - "Complete misalignment with industry standards"

criteria_scoring:
  - criterion_id: CRIT-004
    criterion_name: "Domain Knowledge Accuracy"
    weight: 4
    scoring_guidance:
      - "Look for accurate use of domain terminology"
      - "Check understanding of domain concepts and principles"
      - "Evaluate alignment with industry standards"
      - "Evidence: Domain terminology usage, concept explanations, industry references"
  
  - criterion_id: CRIT-005
    criterion_name: "User Impact Assessment"
    weight: 3
    scoring_guidance:
      - "Assess consideration of user needs and experience"
      - "Evaluate impact on user workflows"
      - "Check accessibility and usability considerations"
      - "Evidence: User impact analysis, accessibility considerations, UX implications"
  
  - criterion_id: CRIT-006
    criterion_name: "Business Value Alignment"
    weight: 3
    scoring_guidance:
      - "Look for clear business value proposition"
      - "Evaluate strategic alignment with objectives"
      - "Check ROI consideration and business impact"
      - "Evidence: Business case, strategic alignment, ROI analysis"
```

### RUBRIC-003: Communication Quality Rubric

```yaml
rubric_id: RUBRIC-003
competency_id: COMP-003
competency_name: "Communication Quality"
rubric_version: "1.0"
calibration_status: "calibrated"

scoring_scale:
  - score: 4
    label: "Excellent"
    description: "Communication is exceptionally clear, comprehensive, and tailored to all stakeholders"
    behavioral_indicators:
      - "Uses clear, unambiguous language throughout"
      - "Logical structure with excellent flow and organization"
      - "Comprehensive documentation with clear examples"
      - "Tailored communication for different stakeholder audiences"
      - "Maintainable and consistent documentation format"
    anti_patterns:
      - "Over-explaining simple concepts"
      - "Excessive detail that obscures main points"
  
  - score: 3
    label: "Good"
    description: "Communication is clear and well-structured with good documentation"
    behavioral_indicators:
      - "Uses clear language with minor ambiguities"
      - "Logical structure with good flow"
      - "Good documentation with relevant examples"
      - "Appropriate communication for main stakeholders"
      - "Maintainable documentation format"
    anti_patterns:
      - "Some ambiguities in language"
      - "Minor structural issues"
  
  - score: 2
    label: "Fair"
    description: "Communication has clarity issues and structural problems"
    behavioral_indicators:
      - "Uses language with some ambiguities and confusion"
      - "Structure needs improvement for better flow"
      - "Basic documentation with limited examples"
      - "Generic communication not tailored to audiences"
      - "Documentation format needs improvement"
    anti_patterns:
      - "Significant ambiguities that impede understanding"
      - "Poor structure that confuses readers"
  
  - score: 1
    label: "Poor"
    description: "Communication is unclear, confusing, and poorly structured"
    behavioral_indicators:
      - "Uses ambiguous and confusing language"
      - "Poor structure with no logical flow"
      - "Incomplete or missing documentation"
      - "No consideration of stakeholder communication needs"
      - "Unmaintainable documentation format"
    anti_patterns:
      - "Communication that prevents understanding"
      - "Structure that makes content inaccessible"

criteria_scoring:
  - criterion_id: CRIT-007
    criterion_name: "Plan Clarity"
    weight: 4
    scoring_guidance:
      - "Look for clear, unambiguous language"
      - "Check logical structure and flow"
      - "Evaluate clarity of instructions and requirements"
      - "Evidence: Language clarity, structure analysis, instruction clarity"
  
  - criterion_id: CRIT-008
    criterion_name: "Documentation Quality"
    weight: 3
    scoring_guidance:
      - "Assess completeness of documentation"
      - "Evaluate quality and relevance of examples"
      - "Check maintainability of documentation format"
      - "Evidence: Documentation completeness, example quality, format assessment"
```

## Rubric Usage Guidelines

### Scoring Process

1. **Independent Scoring**: Each panelist scores independently before group discussion
2. **Evidence-Based**: Scores must be based on observable behaviors, not gut feel
3. **Rubric Reference**: Panelists must reference specific behavioral indicators
4. **Rationale Documentation**: Panelists must provide rationale for scores
5. **Calibration**: Panelists should calibrate scoring through group discussion

### Scoring Template

```yaml
panelist_id: PANELIST-{ID}
competency_id: COMP-{ID}
evaluation_date: "{YYYY-MM-DD}"

# Overall Competency Score
overall_score: {1-4}
overall_rationale: "{Rationale for overall score}"

# Criterion-Specific Scores
criterion_scores:
  - criterion_id: CRIT-{ID}
    score: {1-4}
    rationale: "{Rationale for criterion score}"
    evidence:
      - "{Specific evidence from plan}"
      - "{Specific behavioral indicator observed}"

# Web Search Evidence (per Rule W3)
web_search_evidence:
  - search_query: "{Search query used}"
  citation_url: "{URL of evidence}"
  relevance: "{How this evidence supports the score}"

# Calibration Notes
calibration_notes: "{Notes from group discussion and calibration}"
```

### Calibration Process

1. **Pre-Session Calibration**: Panelists review rubric and discuss scoring expectations
2. **Sample Scoring**: Panelists score sample responses to align expectations
3. **Dispute Resolution**: Establish process for resolving scoring disputes
4. **Rubric Updates**: Update rubrics based on calibration feedback

## Compliance

Post compliance line after rubric creation:
`✅ Gate RUBRIC-CREATION PASS: 4-point scoring rubric created with concrete behavioral indicators following BP principles`

## Evolution Condition

Rubrics evolve when competencies are updated, behavioral indicators are refined, or calibration feedback indicates need for improvement.
