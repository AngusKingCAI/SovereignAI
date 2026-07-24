# Planner Quality Rubric

**Purpose**: Defines evaluation criteria and scoring dimensions for plan quality assessment  
**Authority**: Rules/Planner/Planner_Rules.md  
**Status**: Active  
**Created**: 2026-07-24  
**Location**: Workflow/Planner/Quality_Rubric.md

---

## Scoring Dimensions

This rubric defines 5 quality dimensions for plan evaluation, based on best practices for AI planning assessment.

### Dimension 1: Accuracy
**What it scores**: factual correctness and alignment with requirements

**Evaluation Criteria**:
- Plan goal accurately reflects user requirements
- Steps correctly identify needed changes
- Dependencies are technically accurate
- No false claims or incorrect assumptions
- Changes are feasible for SovereignAI implementation

**Scoring Levels**:
- **5 (Excellent)**: All information accurate, perfect alignment with requirements
- **4 (Good)**: Minor inaccuracies that don't affect implementation
- **3 (Fair)**: Some inaccuracies that may require clarification
- **2 (Poor)**: Significant inaccuracies affecting implementation
- **1 (Critical)**: Major factual errors that would cause implementation failure

**Hard Fail**: Goal misalignment with user requirements or technically impossible changes

---

### Dimension 2: Completeness
**What it scores**: inclusion of all necessary elements

**Evaluation Criteria**:
- All required sections present (Context, Steps, Dependencies)
- Metadata complete (Revision, Date, Goal)
- Steps cover all aspects of the needed changes
- Dependencies account for all relationships
- No missing critical information for implementation

**Scoring Levels**:
- **5 (Excellent)**: All elements present, fully comprehensive
- **4 (Good)**: Minor omissions that don't affect implementation
- **3 (Fair)**: Some omissions that may require clarification
- **2 (Poor)**: Significant omissions affecting implementation
- **1 (Critical)**: Critical missing elements that would cause implementation failure

**Hard Fail**: Missing required sections or metadata

---

### Dimension 3: Clarity
**What it scores**: readability and understandability

**Evaluation Criteria**:
- Goal statement is clear and user-focused
- Steps are unambiguous and actionable
- Language is precise and not vague
- Context provides necessary background
- Dependencies are clearly expressed

**Scoring Levels**:
- **5 (Excellent)**: Crystal clear, unambiguous, easy to follow
- **4 (Good)**: Minor ambiguities that can be resolved with context
- **3 (Fair)**: Some ambiguities requiring clarification
- **2 (Poor)**: Significant ambiguities affecting implementation
- **1 (Critical)**: Unclear goals or steps that would cause implementation confusion

**Hard Fail**: Ambiguous goal statement or unclear critical steps

---

### Dimension 4: Structure
**What it scores**: organization and logical flow

**Evaluation Criteria**:
- Plan follows Plan_Template.md format exactly
- Steps are logically ordered and sequential
- Dependencies are properly structured
- No circular dependencies
- Plan follows ≤120 lines guideline when possible

**Scoring Levels**:
- **5 (Excellent)**: Perfect structure, optimal organization
- **4 (Good)**: Minor structural issues that don't affect execution
- **3 (Fair)**: Some structural issues requiring clarification
- **2 (Poor)**: Significant structural issues affecting execution
- **1 (Critical)**: Structure violations that would cause execution failure

**Hard Fail**: Circular dependencies or format violations

---

### Dimension 5: Context
**What it scores**: background information and rationale

**Evaluation Criteria**:
- Context explains why work matters from user perspective
- Context describes what can be done after changes
- Context provides necessary background and dependencies
- Rationale is clear and supports the approach
- Context is sufficient for implementation decisions

**Scoring Levels**:
- **5 (Excellent)**: Rich context, perfect rationale, comprehensive background
- **4 (Good)**: Minor context gaps that don't affect implementation
- **3 (Fair)**: Some context gaps requiring clarification
- **2 (Poor)**: Significant context gaps affecting implementation
- **1 (Critical)**: Missing critical context that would cause implementation failure

**Hard Fail**: Missing context or rationale for critical decisions

---

## Overall Quality Scoring

### Weighting
- **Accuracy**: 30% (most critical)
- **Completeness**: 25% (critical)
- **Clarity**: 20% (important)
- **Structure**: 15% (important)
- **Context**: 10% (supporting)

### Quality Score Calculation
```
Overall Score = (Accuracy × 0.30) + (Completeness × 0.25) + (Clarity × 0.20) + (Structure × 0.15) + (Context × 0.10)
```

### Quality Thresholds
- **5.0 - 4.5**: Excellent - Clean pass, proceed to external review
- **4.4 - 3.5**: Good - Clean pass, proceed to external review
- **3.4 - 2.5**: Fair - Proceed with documented rationale
- **2.4 - 1.5**: Poor - Requires revisions before external review
- **1.4 - 0.0**: Critical - Block external review, mandatory revisions

### Hard Fail Conditions
If any dimension has a hard fail, the overall quality score is automatically **0.0** regardless of other dimensions.

---

## Panelist Usage

Panelists should use this rubric to:
1. **Receive Persona Instructions**: Review Workflow/Planner/Plan_Prompt_Template.md for persona adoption instructions
2. **Use web search to verify findings** - Check current best practices and research to ground evaluations
3. Evaluate plans across all 5 dimensions
4. Provide dimension-specific scores (1-5) grounded in current research
5. Identify hard fail conditions if present
6. Provide specific feedback for low-scoring dimensions with web search citations
7. Calculate overall quality score using the weighting formula

**Round Table Process**:
- **Plan Brief**: Planner creates brief using Workflow/Planner/Plan_Brief_Template.md
- **Persona Assignment**: Each panelist assigned specific domain-split persona
- **Review Instructions**: Panelists follow Workflow/Planner/Plan_Prompt_Template.md for persona adoption
- **Quality Evaluation**: Use this rubric (Workflow/Planner/Quality_Rubric.md) for dimension scoring
- **Web Search**: Verify findings against current best practices with source citations
- **Structured Output**: Provide JSON output per Workflow/Planner/Plan_Prompt_Template.md format

**Web Search Requirement**:
- Panelists must use web search to verify their findings against current best practices
- Include web sources in structured output format
- Avoid relying on training data which may be outdated
- Reference current research when providing improvement suggestions

**Structured Output Format**:
```json
{
  "verdict": "PASS|FAIL",
  "dimensions": {
    "accuracy": {"score": 4, "notes": "Minor inaccuracies in step 3", "web_sources": ["https://example.com/accuracy-guidelines"]},
    "completeness": {"score": 5, "notes": "All elements present", "web_sources": []},
    "clarity": {"score": 3, "notes": "Some ambiguous language in goal", "web_sources": ["https://example.com/clarity-best-practices"]},
    "structure": {"score": 4, "notes": "Minor format deviation", "web_sources": []},
    "context": {"score": 5, "notes": "Excellent background", "web_sources": []}
  },
  "overall_score": 4.2,
  "issues": [
    {"severity": "MEDIUM", "dimension": "clarity", "description": "Ambiguous goal statement", "web_sources": ["https://example.com/goal-clarity"]}
  ],
  "notes": "Overall good plan, clarify goal statement based on current best practices"
}
```

---

## Continuous Improvement

This rubric will evolve based on:
- Round Table analysis patterns (dimensions that consistently score low)
- Gate failure patterns (structural issues that need detection)
- Best practice research updates
- Implementation feedback from manual execution

**Rubric Amendments**:
1. Identify dimension that needs refinement
2. Update scoring criteria or levels
3. Adjust weighting if needed
4. Update hard fail conditions
5. Document amendment with date and rationale