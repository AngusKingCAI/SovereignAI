# Research Workflow

**Version**: 1.0  
**Last Updated**: 2026-07-22  
**Status**: Active

## Purpose
Conduct external research and create design documents for the SovereignAI project. Provide findings and recommendations to the Planner agent for plan creation.

## Workflow Overview
```
Research Question → External Research → Findings Analysis → Design Document Creation
```

## Phase 1: Research Definition

**Trigger**: Research task initiated by user or Planner agent  
**Goal**: Define the research scope and success criteria

**Steps**:
1. **Understand Question**: Understand the research question or problem
2. **Define Scope**: Define research boundaries and scope
3. **Set Success Criteria**: Define what constitutes successful research
4. **Identify Sources**: Identify potential information sources
5. **Compliance**: Post `✅ Gate RESEARCH-1 PASS: Research scope defined, success criteria set`

**Exit Gate**: Research scope clearly defined with success criteria

---

## Phase 2: External Research

**Trigger**: Research scope defined  
**Goal**: Conduct external research using web search and other sources

**Steps**:
1. **Execute Searches**: Execute web searches for relevant information
2. **Collect Information**: Collect information from multiple sources
3. **Verify Authority**: Verify source authority and credibility
4. **Organize Findings**: Organize findings by topic and relevance
5. **Compliance**: Post `✅ Gate RESEARCH-2 PASS: External research complete, {source_count} sources consulted`

**Exit Gate**: External research complete with findings organized

---

## Phase 3: Findings Analysis

**Trigger**: External research complete  
**Goal**: Analyze findings and draw conclusions

**Steps**:
1. **Analyze Findings**: Analyze collected information
2. **Identify Patterns**: Identify patterns and trends in findings
3. **Draw Conclusions**: Draw conclusions based on evidence
4. **Assess Relevance**: Assess relevance to original research question
5. **Compliance**: Post `✅ Gate RESEARCH-3 PASS: Findings analyzed, conclusions drawn`

**Exit Gate**: Findings analyzed with conclusions drawn

---

## Phase 4: Design Document Creation

**Trigger**: Findings analysis complete  
**Goal**: Create design document based on research findings

**Steps**:
1. **Structure Document**: Structure design document with appropriate sections
2. **Document Findings**: Document research findings and conclusions
3. **Add Recommendations**: Add recommendations based on findings
4. **Include References**: Include source references and citations
5. **Validate Document**: Validate document completeness and accuracy
6. **Compliance**: Post `✅ Gate RESEARCH-4 PASS: Design document created`

**Exit Gate**: Design document ready for Planner agent

---

## Universal Rules Compliance

**All phases must follow**:
- **GR1-GR5**: Universal governance rules (agent responsibilities, single-responsibility, handoff boundaries)
- **ER1-ER5**: Universal editing rules (file editing best practices, large changes, failure recovery)

---

## Stop Conditions

**Halt execution if**:
- Missing compliance line for any gate
- Research cannot be conducted
- Findings cannot be analyzed
- Design document cannot be created

---

## Evolution

**This workflow evolves when**:
- Research methods change
- Design document format changes
- Source requirements change
- Governance rules are updated