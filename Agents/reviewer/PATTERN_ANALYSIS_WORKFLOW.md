# Pattern Analysis Workflow

**Version**: 1.0  
**Last Updated**: 2026-07-22  
**Status**: Active  
**Agent**: Reviewer

## Purpose
Analyze findings patterns from Round Table reviews to identify recurring issues and suggest new rules for the Planner workflow. This workflow converts raw findings into actionable governance rules.

## Workflow Rule Index

| Rule ID | Trigger | Section |
|---------|---------|---------|
| PA1 | Pattern clustering and threshold analysis | §1 |
| PA2 | Rule suggestion formatting and categorization | §2 |
| PA3 | Evidence quality and validation | §3 |

## Workflow Design Rules

### §1 - Pattern Clustering and Threshold Analysis (PA1)

**Trigger**: Processing Round Table findings for pattern analysis  
**Situation**: Analyzing findings to identify recurring patterns that should become rules  
**Judgment**: Implement threshold-based pattern clustering with minimum occurrence requirements before rule suggestion

**Detailed Rule**:
- **Minimum Threshold**: Require at least 3 occurrences of similar findings before suggesting a rule
- **Semantic Clustering**: Group findings by semantic similarity (category, severity, description patterns)
- **Time Window**: Analyze findings within last 30 days to ensure relevance
- **Severity Weighting**: Prioritize CRITICAL and HIGH severity findings for rule suggestion
- **False Positive Filtering**: Exclude findings that were later marked as false positives
- **Compliance**: Post `✅ Gate PA1 PASS: Pattern clustering meets threshold requirements`

**Evidence**: BP findings support minimum thresholds to avoid rule suggestion noise and ensure only recurring patterns become rules

### §2 - Rule Suggestion Formatting and Categorization (PA2)

**Trigger**: Converting pattern analysis results into rule suggestions  
**Situation**: Formatting new rule suggestions for integration into PLANNER_RULES.md  
**Judgment**: Use consistent rule formatting with clear trigger conditions and enforcement levels

**Detailed Rule**:
- **Rule ID Format**: Use PR## format for Planner rules (e.g., PR17 for next new rule)
- **Rule Categories**: Use standard categories (governance, structure, content, quality, security)
- **Trigger Conditions**: Specify clear trigger conditions (when the rule applies)
- **Enforcement Levels**: Specify enforcement level (hard gate, soft gate, guideline)
- **Evidence Linking**: Link rule suggestion to source findings with IDs
- **Compliance**: Post `✅ Gate PA2 PASS: Rule suggestion follows formatting standards`

**Evidence**: Consistent rule formatting enables automated rule integration and clear governance

### §3 - Evidence Quality and Validation (PA3)

**Trigger**: Validating findings used for pattern analysis  
**Situation**: Ensuring findings quality before using them for rule suggestion  
**Judgment**: Validate findings quality before including in pattern analysis

**Detailed Rule**:
- **Panelist Agreement**: Require at least 2 panelists to agree on finding validity
- **Confidence Threshold**: Require minimum confidence score of 70% from panelists
- **Context Completeness**: Findings must have sufficient context for rule formulation
- **Actionability**: Findings must be actionable (clear remediation path)
- **Compliance**: Post `✅ Gate PA3 PASS: Findings meet quality validation criteria`

**Evidence**: High-quality findings lead to more accurate and actionable rule suggestions

## Pattern Analysis Pipeline

### Step 1: Findings Collection
1. **Query Database**: Query Round Table database for findings from last 30 days
2. **Filter Status**: Only include findings with status 'open' or 'addressed'
3. **Filter Quality**: Exclude findings marked as false positives or low confidence
4. **Export Temp**: Export findings to temporary JSON for analysis

### Step 2: Pattern Clustering
1. **Category Grouping**: Group findings by category (governance, structure, content, quality, security)
2. **Severity Grouping**: Within categories, group by severity (CRITICAL, HIGH, MEDIUM, LOW)
3. **Semantic Analysis**: Analyze description patterns for semantic similarity
4. **Threshold Check**: Only keep patterns with ≥3 occurrences

### Step 3: Rule Suggestion Generation
1. **Pattern Analysis**: For each cluster, analyze common characteristics
2. **Rule Drafting**: Draft rule suggestion following PA2 formatting
3. **Trigger Specification**: Define trigger conditions based on pattern context
4. **Enforcement Level**: Suggest enforcement level based on severity distribution
5. **Evidence Linking**: Link to source finding IDs

### Step 4: Quality Validation
1. **Panelist Agreement**: Verify PA3 criteria (≥2 panelists, ≥70% confidence)
2. **Context Validation**: Ensure sufficient context for rule formulation
3. **Actionability Check**: Verify clear remediation path exists
4. **Rule Review**: Manual review of rule suggestions by Reviewer

### Step 5: Rule Integration
1. **Rule ID Assignment**: Assign next available PR## ID
2. **PLANNER_RULES.md Update**: Add rule suggestion to PLANNER_RULES.md
3. **Database Update**: Add rule to rules table with pattern_source
4. **Rule Application**: Link rule to source findings in rule_applications table
5. **Compliance**: Post `✅ Gate PA-COMPLETE: Pattern analysis complete, {N} rules suggested`

## Output Format

### Pattern Analysis Results JSON
```json
{
  "analysis_timestamp": "2026-07-22T16:00:00Z",
  "time_window": "30 days",
  "total_findings_analyzed": 45,
  "patterns_detected": 5,
  "rules_suggested": 3,
  "patterns": [
    {
      "pattern_id": "P001",
      "category": "governance",
      "severity": "CRITICAL",
      "occurrence_count": 7,
      "finding_ids": [1, 3, 5, 8, 12, 15, 18],
      "panelist_agreement": 1.0,
      "confidence_score": 85,
      "rule_suggestion": {
        "rule_id": "PR17",
        "title": "Governance Landmine Screening",
        "description": "Plans must be screened for governance landmines before Round Table review",
        "trigger_conditions": "Plan submitted for Round Table review",
        "enforcement_level": "hard_gate",
        "category": "governance"
      }
    }
  ]
}
```

## Implementation Scripts

### Pattern Analysis Pipeline Script
- **Location**: `Agents/reviewer/scripts/pattern_analysis/pattern_analysis_pipeline.py`
- **Purpose**: Execute complete pattern analysis pipeline
- **Usage**: `python pattern_analysis_pipeline.py --days 30 --threshold 3`

### Rule Integration Script
- **Location**: `Agents/reviewer/scripts/pattern_analysis/rule_integration.py`
- **Purpose**: Integrate suggested rules into PLANNER_RULES.md
- **Usage**: `python rule_integration.py --pattern-analysis-results results.json`

### Brief Validation Script
- **Location**: `Agents/reviewer/scripts/pattern_analysis/brief_validation.py`
- **Purpose**: Validate brief quality before Round Table review
- **Usage**: `python brief_validation.py --brief-file brief.md`

## Quality Gates

### Soft Gates (Non-Blocking)
- **SG-Pattern-Count**: Warn if pattern count is below expected threshold
- **SG-Cluster-Quality**: Warn if cluster quality score is below 70%
- **SG-Evidence-Quality**: Warn if evidence quality is below threshold

### Hard Gates (Blocking)
- **HG-Pattern-Threshold**: Block if pattern count below minimum threshold (3)
- **HG-Rule-Format**: Block if rule suggestion format is invalid
- **HG-Evidence-Validation**: Block if evidence quality is insufficient

## Integration with Reviewer Workflow

1. **Post-Round Table Trigger**: Pattern analysis runs after each Round Table review
2. **Batch Processing**: Process findings in batches (e.g., weekly)
3. **Rule Suggestion Queue**: Queue rule suggestions for manual review
4. **Rule Integration**: Integrate approved rules into PLANNER_RULES.md
5. **Feedback Loop**: Monitor rule effectiveness and adjust thresholds

## Notes

- **Manual Review**: Rule suggestions require manual review before integration
- **Threshold Adjustment**: Thresholds may be adjusted based on findings volume
- **False Positive Handling**: False positive findings are excluded from pattern analysis
- **Performance Tracking**: Track rule effectiveness over time for optimization