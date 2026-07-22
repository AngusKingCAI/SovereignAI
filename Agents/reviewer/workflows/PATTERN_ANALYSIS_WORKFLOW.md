# Pattern Analysis & Rule Suggestion Workflow

**Version**: 1.0  
**Last Updated**: 2026-07-22  
**Status**: Design Phase

## Purpose
Analyze Round Table findings patterns and suggest rule creation to reduce future plan revisions. Integrated into Phase 7 of PLAN_WORKFLOW.md as Reviewer responsibility (per GR3 single-responsibility).

## Workflow Overview

Hybrid approach combining frequency analysis for obvious patterns and ML clustering for subtle patterns:
```
Findings Database → Frequency Analysis → ML Clustering → Rule Generation → Rule Validation → Integration
```

## Phase 1: Data Collection

**Trigger**: Round Table review complete (Phase 6)  
**Goal**: Collect findings data for pattern analysis

**Steps**:
1. **Query Recent Findings**: Extract findings from last 3-5 batches
2. **Batch Context**: Include batch metadata (plan numbers, revision counts)
3. **Panelist Context**: Include panelist information (specialties, models)
4. **Compliance**: Post `✅ Gate PA-1 PASS: Findings data collected for analysis`

**SQL Query**:
```sql
SELECT 
    f.id,
    f.category,
    f.severity,
    f.description,
    f.context,
    f.plan_impact,
    f.status,
    pr.panelist_id,
    p.name as panelist_name,
    p.model as panelist_model,
    pl.plan_number,
    pl.revision_count,
    b.batch_number
FROM findings f
JOIN panelist_reviews pr ON f.review_id = pr.id
JOIN panelists p ON pr.panelist_id = p.id
JOIN plans pl ON pr.plan_id = pl.id
JOIN batches b ON pl.batch_id = b.id
WHERE b.created_at > datetime('now', '-30 days')
ORDER BY b.created_at DESC, f.severity DESC;
```

## Phase 2: Frequency Analysis

**Trigger**: Data collection complete  
**Goal**: Identify obvious high-frequency patterns

**Steps**:
1. **Category Frequency**: Count findings by category
2. **Severity Frequency**: Count findings by severity level
3. **Pattern Detection**: Identify repeated descriptions/themes
4. **High-Impact Patterns**: Flag patterns affecting multiple plans
5. **Compliance**: Post `✅ Gate PA-2 PASS: Frequency analysis completed, high-frequency patterns identified`

**Analysis Logic**:
```python
def analyze_frequency(findings_data):
    # Category frequency
    category_counts = Counter(f['category'] for f in findings_data)
    
    # Severity frequency
    severity_counts = Counter(f['severity'] for f in findings_data)
    
    # Pattern detection via text similarity
    descriptions = [f['description'] for f in findings_data]
    similarity_matrix = compute_similarity(descriptions)
    
    # Identify clusters of similar descriptions
    pattern_clusters = find_similar_clusters(similarity_matrix, threshold=0.8)
    
    # High-impact patterns (affecting multiple plans)
    high_impact = []
    for cluster in pattern_clusters:
        affected_plans = set(findings_data[i]['plan_number'] for i in cluster)
        if len(affected_plans) >= 2:
            high_impact.append({
                'pattern': cluster,
                'affected_plans': affected_plans,
                'occurrence_count': len(cluster)
            })
    
    return {
        'category_frequency': category_counts,
        'severity_frequency': severity_counts,
        'high_impact_patterns': high_impact
    }
```

## Phase 3: ML Clustering

**Trigger**: Frequency analysis complete  
**Goal**: Identify subtle patterns using clustering

**Steps**:
1. **Feature Extraction**: Convert findings to feature vectors
2. **Clustering**: Apply K-means or DBSCAN clustering
3. **Cluster Analysis**: Analyze cluster characteristics
4. **Representative Selection**: Select representative findings per cluster
5. **Compliance**: Post `✅ Gate PA-3 PASS: ML clustering completed, subtle patterns identified`

**Clustering Logic**:
```python
def cluster_findings(findings_data):
    # Feature extraction
    texts = [f"{f['category']} {f['description']} {f['context'] or ''}" for f in findings_data]
    vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
    feature_vectors = vectorizer.fit_transform(texts)
    
    # Determine optimal cluster count using silhouette score
    silhouette_scores = []
    for n_clusters in range(2, min(10, len(findings_data))):
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        labels = kmeans.fit_predict(feature_vectors)
        score = silhouette_score(feature_vectors, labels)
        silhouette_scores.append((n_clusters, score))
    
    optimal_clusters = max(silhouette_scores, key=lambda x: x[1])[0]
    
    # Apply clustering with optimal cluster count
    kmeans = KMeans(n_clusters=optimal_clusters, random_state=42)
    cluster_labels = kmeans.fit_predict(feature_vectors)
    
    # Analyze clusters
    clusters = {}
    for i, label in enumerate(cluster_labels):
        if label not in clusters:
            clusters[label] = []
        clusters[label].append(findings_data[i])
    
    # Select representative findings per cluster
    representatives = {}
    for label, cluster_findings in clusters.items():
        # Find finding closest to cluster centroid
        cluster_center = kmeans.cluster_centers_[label]
        distances = pairwise_distances(feature_vectors[i].reshape(1, -1), cluster_center.reshape(1, -1))
        representative_idx = np.argmin(distances)
        representatives[label] = cluster_findings[representative_idx]
    
    return {
        'optimal_clusters': optimal_clusters,
        'clusters': clusters,
        'representatives': representatives
    }
```

## Phase 4: Rule Generation

**Trigger**: Frequency analysis and clustering complete  
**Goal**: Generate rule proposals from identified patterns

**Steps**:
1. **Frequency-Based Rules**: Generate rules from high-frequency patterns
2. **Cluster-Based Rules**: Generate rules from cluster representatives
3. **Rule Formatting**: Format rules according to PLANNER_RULES.md structure
4. **Evidence Collection**: Collect evidence for each rule (affected plans, occurrence count)
5. **Compliance**: Post `✅ Gate PA-4 PASS: Rule proposals generated from patterns`

**Rule Generation Logic**:
```python
def generate_rules(frequency_analysis, clustering_results):
    rules = []
    
    # Generate rules from high-frequency patterns
    for pattern in frequency_analysis['high_impact_patterns']:
        representative = pattern['pattern'][0]  # First finding in pattern
        rule = {
            'rule_id': f"RTR-{len(rules) + 1}",
            'title': generate_rule_title(representative),
            'description': generate_rule_description(pattern),
            'category': representative['category'],
            'trigger_conditions': generate_trigger_conditions(pattern),
            'pattern_source': f"Frequency analysis: {len(pattern['pattern'])} occurrences across {len(pattern['affected_plans'])} plans",
            'enforcement_level': determine_enforcement_level(representative['severity']),
            'evidence': {
                'finding_count': len(pattern['pattern']),
                'affected_plans': list(pattern['affected_plans']),
                'revision_reduction_potential': estimate_reduction_potential(pattern)
            }
        }
        rules.append(rule)
    
    # Generate rules from cluster representatives
    for label, representative in clustering_results['representatives'].items():
        if len(clustering_results['clusters'][label]) >= 2:  # Only clusters with multiple findings
            rule = {
                'rule_id': f"RTR-{len(rules) + 1}",
                'title': generate_rule_title(representative),
                'description': generate_rule_description_from_cluster(clustering_results['clusters'][label]),
                'category': representative['category'],
                'trigger_conditions': generate_trigger_conditions_from_cluster(clustering_results['clusters'][label]),
                'pattern_source': f"Cluster analysis: {len(clustering_results['clusters'][label])} similar findings",
                'enforcement_level': determine_enforcement_level(representative['severity']),
                'evidence': {
                    'finding_count': len(clustering_results['clusters'][label]),
                    'affected_plans': list(set(f['plan_number'] for f in clustering_results['clusters'][label])),
                    'revision_reduction_potential': estimate_reduction_potential_cluster(clustering_results['clusters'][label])
                }
            }
            rules.append(rule)
    
    return rules
```

## Phase 5: Rule Validation

**Trigger**: Rule proposals generated  
**Goal**: Validate proposed rules against existing rule set

**Steps**:
1. **Duplicate Check**: Check for duplicate or similar existing rules
2. **Conflict Check**: Check for conflicts with existing rules
3. **Quality Check**: Validate rule quality and completeness
4. **Priority Assessment**: Assess rule priority based on evidence
5. **Compliance**: Post `✅ Gate PA-5 PASS: Rule proposals validated against existing rules`

**Validation Logic**:
```python
def validate_rules(proposed_rules, existing_rules):
    validated_rules = []
    
    for proposed_rule in proposed_rules:
        # Duplicate check
        is_duplicate = False
        for existing_rule in existing_rules:
            similarity = compute_rule_similarity(proposed_rule, existing_rule)
            if similarity > 0.8:  # High similarity threshold
                is_duplicate = True
                break
        
        if is_duplicate:
            continue  # Skip duplicate rules
        
        # Conflict check
        has_conflict = False
        for existing_rule in existing_rules:
            if (proposed_rule['category'] == existing_rule['category'] and 
                proposed_rule['trigger_conditions'] == existing_rule['trigger_conditions']):
                has_conflict = True
                break
        
        if has_conflict:
            continue  # Skip conflicting rules
        
        # Quality check
        if not all([
            proposed_rule.get('title'),
            proposed_rule.get('description'),
            proposed_rule.get('category'),
            proposed_rule.get('trigger_conditions')
        ]):
            continue  # Skip incomplete rules
        
        # Priority assessment
        priority_score = (
            proposed_rule['evidence']['finding_count'] * 2 +
            len(proposed_rule['evidence']['affected_plans']) +
            (3 if proposed_rule['enforcement_level'] == 'hard_gate' else 
             2 if proposed_rule['enforcement_level'] == 'soft_gate' else 1)
        )
        
        proposed_rule['priority_score'] = priority_score
        validated_rules.append(proposed_rule)
    
    # Sort by priority score
    validated_rules.sort(key=lambda x: x['priority_score'], reverse=True)
    
    return validated_rules
```

## Phase 6: Rule Suggestion Report

**Trigger**: Rule validation complete  
**Goal**: Generate rule suggestion report for Planner integration

**Steps**:
1. **Rule Prioritization**: Prioritize validated rules by evidence and impact
2. **Report Generation**: Generate structured rule suggestion report
3. **Evidence Documentation**: Document evidence for each suggested rule
4. **Integration Instructions**: Provide clear integration instructions for Planner
5. **Compliance**: Post `✅ Gate PA-6 PASS: Rule suggestion report generated for Planner`

**Report Format**:
```python
def generate_rule_suggestion_report(validated_rules):
    report = {
        "report_metadata": {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "total_suggestions": len(validated_rules),
            "high_priority": len([r for r in validated_rules if r['enforcement_level'] == 'hard_gate'])
        },
        "rule_suggestions": []
    }
    
    for rule in validated_rules[:10]:  # Top 10 rules
        suggestion = {
            "rule_id": rule['rule_id'],
            "title": rule['title'],
            "description": rule['description'],
            "category": rule['category'],
            "trigger_conditions": rule['trigger_conditions'],
            "pattern_source": rule['pattern_source'],
            "enforcement_level": rule['enforcement_level'],
            "evidence": rule['evidence'],
            "integration_priority": rule['priority_score'],
            "suggested_section": f"§{calculate_next_section_number(rule['category'])}"
        }
        report["rule_suggestions"].append(suggestion)
    
    return report
```

## Phase 7: Findings Analysis Report

**Trigger**: Rule suggestion report complete  
**Goal**: Generate comprehensive findings analysis report for Planner

**Steps**:
1. **Summary Statistics**: Generate summary statistics for findings
2. **Trend Analysis**: Analyze trends across batches
3. **Category Breakdown**: Provide detailed category breakdown
4. **Severity Distribution**: Analyze severity distribution
5. **Recommendations**: Provide recommendations for rule integration
6. **Compliance**: Post `✅ Gate PA-7 PASS: Findings analysis report generated for Planner`

**Report Format**:
```python
def generate_findings_analysis_report(findings_data):
    report = {
        "report_metadata": {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "analysis_period": "last_30_days",
            "total_findings": len(findings_data)
        },
        "summary_statistics": {
            "by_category": dict(Counter(f['category'] for f in findings_data)),
            "by_severity": dict(Counter(f['severity'] for f in findings_data)),
            "by_status": dict(Counter(f['status'] for f in findings_data))
        },
        "trend_analysis": analyze_trends(findings_data),
        "recommendations": generate_recommendations(findings_data)
    }
    
    return report
```

## Quality Gates

- **Gate PA-1**: Findings data must include last 3-5 batches with complete metadata
- **Gate PA-2**: Must identify at least 3 high-frequency patterns with occurrence count ≥ 2
- **Gate PA-3**: Clustering must achieve silhouette score ≥ 0.5
- **Gate PA-4**: Generated rule suggestions must include evidence (affected plans, occurrence count)
- **Gate PA-5**: No duplicate or conflicting rule suggestions with existing rule set
- **Gate PA-6**: Rule suggestion report must include clear integration instructions for Planner
- **Gate PA-7**: Findings analysis report must include actionable recommendations

## Gate Enforcement (Per G6)

**Hard Gates** (Blocking):
- **PA-1**: Findings data collection required with complete metadata
- **PA-2**: High-frequency pattern identification required (≥3 patterns, occurrence ≥2)
- **PA-3**: ML clustering quality threshold required (silhouette score ≥0.5)
- **PA-4**: Rule evidence inclusion required (affected plans, occurrence count)
- **PA-5**: Rule uniqueness required (no duplicates or conflicts)
- **PA-6**: Integration instructions required in rule suggestion report
- **PA-7**: Actionable recommendations required in findings analysis report

**Soft Gates** (Non-Blocking):
- **Pattern Count**: Fewer than 3 high-frequency patterns may proceed with documented rationale
- **Cluster Quality**: Silhouette score <0.5 may proceed with documented justification
- **Evidence Strength**: Weak evidence (single occurrence) may proceed with documented rationale
- **Rule Priority**: Low-priority rules may be suggested with documented justification

**Soft Gate Enforcement Mechanism**:
- **Non-Blocking**: Soft gate violations allow proceeding with documented rationale
- **Rationale Documentation**: Document justification for proceeding despite soft gate violation
- **Monitoring**: Track soft gate violations for pattern analysis and potential hard gate conversion
- **Per AGENTS.md G6**: Soft gate enforcement defined in AGENTS.md with script-based implementation
- **Validation Scripts**: Soft gates enforced by Python scripts in `Agents/reviewer/scripts/soft_gates/`
  - `sg_pattern_count.py`: Warns if <3 high-frequency patterns identified
  - `sg_cluster_quality.py`: Warns if silhouette score <0.5
  - `sg_evidence_quality.py`: Warns if rule evidence is weak (<2 affected plans)

## Handoff to Planner

**Trigger**: Pattern analysis reports complete  
**Goal**: Handoff rule suggestions and findings analysis to Planner for integration

**Handoff Process**:
1. **Report Delivery**: Deliver rule suggestion report and findings analysis report to Planner
2. **Integration Instructions**: Provide clear instructions for rule integration
3. **Follow-up Support**: Available for clarification on rule suggestions
4. **Compliance**: Post `✅ Gate PA-8 PASS: Reports delivered to Planner for integration`

**Handoff Artifacts**:
- Rule suggestion report (with prioritized rule proposals)
- Findings analysis report (with statistics and recommendations)
- Integration instructions for PLANNER_RULES.md
- Evidence documentation for each suggested rule

## Integration with Rule Integration Workflow

This workflow is followed by RULE_INTEGRATION_WORKFLOW.md, both executed by Reviewer. This follows GR3 single-responsibility principle:
- **Reviewer**: Analyzes findings patterns, suggests rules, and integrates approved rules
- **Planner**: Uses updated PLANNER_RULES.md for future plan creation