# Quality Assessment Framework

**Purpose**: Universal quality assessment framework for all agent workflows.

## Universal Quality Dimensions

### Dimension 1: Accuracy
**What it scores**: Factual correctness and alignment with requirements

**Universal Evaluation Criteria**:
- Work output accurately reflects user requirements
- Steps/codes correctly identify needed changes
- Dependencies/relationships are technically accurate
- No false claims or incorrect assumptions
- Changes/approaches are feasible for implementation

**Universal Scoring Levels**:
- **5 (Excellent)**: All information accurate, perfect alignment with requirements
- **4 (Good)**: Minor inaccuracies that don't affect implementation
- **3 (Fair)**: Some inaccuracies that may require clarification
- **2 (Poor)**: Significant inaccuracies affecting implementation
- **1 (Critical)**: Major factual errors that would cause implementation failure

**Hard Fail**: Goal/work misalignment with user requirements or technically impossible changes

---

### Dimension 2: Completeness
**What it scores**: Inclusion of all necessary elements

**Universal Evaluation Criteria**:
- All required sections/patterns present
- Metadata complete where applicable
- Steps/codes cover all aspects of needed changes
- Dependencies account for all relationships
- No missing critical information for implementation

**Universal Scoring Levels**:
- **5 (Excellent)**: All elements present, fully comprehensive
- **4 (Good)**: Minor omissions that don't affect implementation
- **3 (Fair)**: Some omissions that may require clarification
- **2 (Poor)**: Significant omissions affecting implementation
- **1 (Critical)**: Critical missing elements that would cause implementation failure

**Hard Fail**: Missing required sections or metadata

---

### Dimension 3: Clarity
**What it scores**: Readability and understandability

**Universal Evaluation Criteria**:
- Goal/statement is clear and user-focused
- Steps/codes are unambiguous and actionable
- Language is precise and not vague
- Context provides necessary background
- Dependencies/relationships are clearly expressed

**Universal Scoring Levels**:
- **5 (Excellent)**: Crystal clear, unambiguous, easy to follow
- **4 (Good)**: Minor ambiguities that can be resolved with context
- **3 (Fair)**: Some ambiguities requiring clarification
- **2 (Poor)**: Significant ambiguities affecting implementation
- **1 (Critical)**: Unclear goals or steps that would cause implementation confusion

**Hard Fail**: Ambiguous goal statement or unclear critical steps

---

### Dimension 4: Structure
**What it scores**: Organization and logical flow

**Universal Evaluation Criteria**:
- Work follows template/format requirements exactly
- Steps/codes are logically ordered and sequential
- Dependencies/relationships are properly structured
- No circular dependencies or contradictions
- Work follows length guidelines when applicable

**Universal Scoring Levels**:
- **5 (Excellent)**: Perfect structure, optimal organization
- **4 (Good)**: Minor structural issues that don't affect execution
- **3 (Fair)**: Some structural issues requiring clarification
- **2 (Poor)**: Significant structural issues affecting execution
- **1 (Critical)**: Structure violations that would cause execution failure

**Hard Fail**: Circular dependencies or format violations

---

### Dimension 5: Context
**What it scores**: Background information and rationale

**Universal Evaluation Criteria**:
- Context explains why work matters from user perspective
- Context describes what can be done after changes
- Context provides necessary background and dependencies
- Rationale is clear and supports the approach
- Context is sufficient for implementation decisions

**Universal Scoring Levels**:
- **5 (Excellent)**: Rich context, perfect rationale, comprehensive background
- **4 (Good)**: Minor context gaps that don't affect implementation
- **3 (Fair)**: Some context gaps requiring clarification
- **2 (Poor)**: Significant context gaps affecting implementation
- **1 (Critical)**: Missing critical context that would cause implementation failure

**Hard Fail**: Missing context or rationale for critical decisions

---

## Universal Quality Scoring

### Universal Weighting
- **Accuracy**: 30% (most critical)
- **Completeness**: 25% (critical)
- **Clarity**: 20% (important)
- **Structure**: 15% (important)
- **Context**: 10% (supporting)

### Quality Score Calculation
```
Overall Score = (Accuracy × 0.30) + (Completeness × 0.25) + (Clarity × 0.20) + (Structure × 0.15) + (Context × 0.10)
```

### Universal Quality Thresholds
- **5.0 - 4.5**: Excellent - Clean pass, proceed to next phase
- **4.4 - 3.5**: Good - Clean pass, proceed to next phase
- **3.4 - 2.5**: Fair - Proceed with documented rationale
- **2.4 - 1.5**: Poor - Requires revisions before proceeding
- **1.4 - 0.0**: Critical - Block proceeding, mandatory revisions

### Hard Fail Conditions
If any dimension has a hard fail, the overall quality score is automatically **0.0** regardless of other dimensions.

---

## Agent-Specific Customization

### Planner Agent
- **Focus**: Plan quality assessment with planning-specific criteria
- **Customization**: Planning language validation, dependency graph analysis
- **Reference**: Universal framework with planner-specific quality criteria integration

### Architect Agent
- **Focus**: Infrastructure design quality assessment
- **Customization**: Architectural pattern validation, security boundary compliance
- **Reference**: Universal framework with architect-specific criteria integration

### Executor Agent
- **Focus**: Implementation quality assessment
- **Customization**: Code quality metrics, test coverage validation
- **Reference**: Universal framework with executor-specific criteria integration

### Reviewer Agent
- **Focus**: Quality analysis and pattern recognition
- **Customization**: Recurring issue identification, governance gap analysis
- **Reference**: Universal framework with reviewer-specific criteria integration

---

## Usage Guidelines

### Universal Framework Application
1. **Apply Universal Dimensions**: Use the 5 universal dimensions as baseline
2. **Customize for Agent Type**: Add agent-specific criteria within universal framework
3. **Weight Adjustments**: Adjust weighting based on agent-specific priorities
4. **Threshold Customization**: Modify thresholds based on agent requirements
5. **Reference Pattern**: Reference universal framework for consistency

### Quality Assessment Process
1. **Load Universal Framework**: Start with universal quality dimensions
2. **Apply Agent Criteria**: Add agent-specific evaluation criteria
3. **Score Each Dimension**: Use 1-5 scale with reasoning
4. **Calculate Overall Score**: Apply weighted formula
5. **Check Hard Fails**: Validate no hard fail conditions present
6. **Determine Quality Level**: Apply thresholds to determine quality level

### Continuous Improvement
- Monitor dimension scoring patterns across agents
- Identify dimensions that consistently score low
- Update universal criteria based on patterns
- Adjust weighting based on agent feedback
- Document framework changes with rationale