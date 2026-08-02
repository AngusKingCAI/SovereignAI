# External AI Comprehensive Harness Document Scan Prompt

## Prompt Version: 1.1
## Last Updated: 2026-07-28
## Purpose: Comprehensive line-by-line scan of all SovereignAI harness documents with best practice validation

---

## REPOSITORY SETUP (MANDATORY FIRST STEP)

**Repository URL**: `https://github.com/AngusKingCAI/SovereignAI.git`

### BEFORE BEGINNING THE SCAN:

1. **Clone or pull the latest version of the repository**:
   ```bash
   # If cloning for the first time:
   git clone https://github.com/AngusKingCAI/SovereignAI.git
   cd SovereignAI
   
   # If you already have a local copy:
   cd SovereignAI
   git pull origin main
   ```

2. **Verify you have the latest version**:
   ```bash
   git log --oneline -1
   ```
   The commit hash should match the latest commit on the main branch.

3. **Ensure you are on the main branch**:
   ```bash
   git branch
   ```
   You should see `* main` indicating you are on the main branch.

4. **Verify the repository structure**:
   ```bash
   ls -la
   ```
   You should see the expected directories: `Workflow/`, `Rules/`, `.devin/`, `AGENTS.md`, etc.

**CRITICAL**: Do not begin the scan until you have successfully pulled the latest version of the repository. Scanning an outdated version will produce inaccurate results and waste computational resources.

---

## INSTRUCTIONS FOR EXTERNAL AI MODELS

You are tasked with performing a **comprehensive, exhaustive, line-by-line scan** of all SovereignAI harness documentation, workflows, rules, and governance files. This scan must be extremely detailed and thorough, leaving no file unexamined and no line unanalyzed.

### CRITICAL REQUIREMENTS

1. **LINE-BY-LINE SCANNING**: You must read every single line of every file without skipping anything
2. **COMPREHENSIVE COVERAGE**: Every governance file must be examined - no exceptions, no omissions
3. **BEST PRACTICE RESEARCH**: For EACH file, you MUST perform web searches for current best practices relevant to that file type
4. **EXTREME DETAIL**: Findings must be extremely detailed with specific line references, citations, and actionable recommendations
5. **STRUCTURED OUTPUT**: All findings must be documented in the exact schema specified below
6. **HANDLING ABSENCE**: If information is missing, explicitly state "NOT FOUND" - do not hallucinate or infer
7. **CITATION ANCHORING**: Every finding must include specific file paths, line numbers, and source references

---

## SCAN SCOPE

### Governance Files to Scan (COMPREHENSIVE)

**Workflow Files:**
- All files in `Workflow/Architect/`
- All files in `Workflow/Planner/`
- All files in `Workflow/Executor/`
- All files in `Workflow/Reviewer/`
- All files in `Workflow/Researcher/`
- All files in `Workflow/Workflow_Reference/`
- All files in `Workflow/Planner/Templates/`

**Rules Files:**
- All files in `Rules/Architect/`
- All files in `Rules/Planner/`
- All files in `Rules/Executor/`
- All files in `Rules/Reviewer/`
- All files in `Rules/Researcher/`

**Configuration Files:**
- All files in `.devin/`
- All files in `.devin/skills/`
- `AGENTS.md` (project root)
- `STRUCTURE.md` (project root)

**Governance Reference Files:**
- `PRINCIPLES.md` (if exists)
- Any other governance or policy documents in project root

**EXCLUSION SCOPE:**
- `Docs/` folder (excluded)
- `Logs/` folder (excluded)
- `Plans/` folder (excluded)
- `App/` folder (excluded)
- Any application code or implementation files

---

## SCAN PROCESS (MANDATORY SEQUENCE)

### Phase 1: File Discovery and Categorization
1. Discover every single governance file using systematic file search
2. Sort files alphabetically by full path for consistent scanning order
3. Categorize each file by type:
   - Workflow files (.md)
   - Rules files (.md)
   - Configuration files (.json, .yaml, .toml)
   - Script files (.py, .sh, .bash)
   - Documentation files (.md, .txt, .rst)
   - Data files (JSON, YAML, TOML, etc.)

### Phase 2: Comprehensive File-by-File Scanning
For EACH file in alphabetical order:

1. **READ the entire file line by line** - do not skip any lines
2. **PERFORM web search** for current best practices relevant to that specific file type
3. **ANALYZE** the file against the following compliance criteria based on file type:

**Workflow Files (.md) Analysis Criteria:**
- Header structure completeness (ID, Owner, Frequency, Duration, Priority, Execution Modes, Purpose, Scope, Roles, Trigger and End State)
- Phase organization and logical flow
- Step numbering consistency and sequential logic
- Universal Framework References presence and completeness
- Execution Modes definition and alignment
- Cross-reference accuracy to other governance files
- Markdown quality and formatting standards
- Template compliance where applicable
- Terminology consistency with Terminology_Glossary.md
- Planning language compliance (for planning workflows)
- Infrastructure best practices adherence

**Rules Files (.md) Analysis Criteria:**
- YAML frontmatter structure and completeness
- Rule categorization and naming conventions
- Rule enforcement patterns and dependencies
- Dependency documentation accuracy
- Cross-reference validity to workflows and other rules
- Behavioral rule consistency with AGENTS.md
- Markdown quality and formatting standards
- Authority/intelligence separation compliance
- Constitutional framework alignment (if applicable)

**Configuration Files (.json, .yaml, .toml) Analysis Criteria:**
- JSON/YAML syntax validity
- Schema compliance and structure
- Hook configuration patterns
- Skill definition completeness
- Cross-reference accuracy to workflows and rules
- Configuration security best practices
- Version compatibility

**Script Files (.py, .sh, .bash) Analysis Criteria:**
- Code quality standards
- Modularity and separation of concerns
- Error handling completeness
- Security practices
- Documentation completeness
- Performance considerations
- Dependency management

**Documentation Files (.md, .txt, .rst) Analysis Criteria:**
- Heading hierarchy structure (H1-H6 consistency)
- List formatting (bullet/numbered)
- Link validity and accuracy
- Code block syntax correctness
- Table structure validity
- Terminology consistency
- Clarity and completeness

**Cross-Reference Integrity Analysis (ALL FILES):**
- File reference accuracy
- Workflow reference consistency
- Rule reference validity
- Universal framework reference relevance
- Agent-specific reference alignment
- Broken or missing references
- Circular dependency detection

**Infrastructure Best Practices Analysis (ALL FILES):**
- Separation of universal vs agent-specific content
- Relevance requirement compliance
- Architectural consistency
- DRY principles in governance
- Single source of truth adherence
- Maintainability and scalability

### Phase 3: Findings Documentation
For EACH file, document findings in the exact schema specified below:

---

## OUTPUT SCHEMA (MANDATORY FORMAT)

Your output MUST be structured as follows. Do not deviate from this format.

### File-Level Finding Schema

```json
{
  "file_path": "string (full relative path from project root)",
  "file_type": "string (workflow|rules|configuration|script|documentation|data)",
  "scan_status": "string (COMPLETE|INCOMPLETE|ERROR)",
  "best_practice_research": {
    "search_performed": "boolean",
    "search_query": "string (the web search query used)",
    "best_practices_found": "string (summary of current best practices found)",
    "sources": "array of strings (URLs of sources consulted)"
  },
  "compliance_analysis": {
    "header_structure": {
      "status": "string (PASS|FAIL|PARTIAL)",
      "issues": "array of objects with line_number, description, severity"
    },
    "content_organization": {
      "status": "string (PASS|FAIL|PARTIAL)",
      "issues": "array of objects with line_number, description, severity"
    },
    "cross_references": {
      "status": "string (PASS|FAIL|PARTIAL)",
      "issues": "array of objects with line_number, description, severity"
    },
    "terminology_consistency": {
      "status": "string (PASS|FAIL|PARTIAL)",
      "issues": "array of objects with line_number, description, severity"
    },
    "formatting_standards": {
      "status": "string (PASS|FAIL|PARTIAL)",
      "issues": "array of objects with line_number, description, severity"
    }
  },
  "findings": [
    {
      "id": "string (unique finding ID)",
      "category": "string (infrastructure|quality|consistency|security|performance|maintainability)",
      "severity": "string (CRITICAL|HIGH|MEDIUM|LOW)",
      "line_number": "number (specific line reference)",
      "issue_type": "string (missing|incorrect|inconsistent|outdated|inefficient|ambiguous|duplicate)",
      "description": "string (detailed description of the issue)",
      "evidence": "string (specific text or content that demonstrates the issue)",
      "best_practice_violation": "string (which best practice is violated, if applicable)",
      "recommendation": "string (specific actionable recommendation)",
      "recommendation_type": "string (add|remove|modify|restructure|clarify)",
      "priority": "string (immediate|high|medium|low)",
      "complexity": "string (simple|moderate|complex)"
    }
  ],
  "summary": {
    "total_findings": "number",
    "critical_count": "number",
    "high_count": "number",
    "medium_count": "number",
    "low_count": "number",
    "overall_assessment": "string (COMPLIANT|NEEDS_IMPROVEMENT|NON_COMPLIANT)"
  }
}
```

### Consolidated Report Schema

After scanning all files, provide a consolidated summary:

```json
{
  "scan_metadata": {
    "scan_date": "string (ISO 8601 format)",
    "scanner_model": "string (AI model used)",
    "total_files_scanned": "number",
    "scan_duration": "string (estimated or actual)",
    "scan_scope": "string (description of scope covered)"
  },
  "file_categorization": {
    "workflow_files": "number",
    "rules_files": "number",
    "configuration_files": "number",
    "script_files": "number",
    "documentation_files": "number",
    "data_files": "number"
  },
  "consolidated_findings": {
    "total_findings": "number",
    "by_severity": {
      "critical": "number",
      "high": "number",
      "medium": "number",
      "low": "number"
    },
    "by_category": {
      "infrastructure": "number",
      "quality": "number",
      "consistency": "number",
      "security": "number",
      "performance": "number",
      "maintainability": "number"
    },
    "by_file_type": {
      "workflow_files": "number",
      "rules_files": "number",
      "configuration_files": "number",
      "script_files": "number",
      "documentation_files": "number"
    }
  },
  "critical_issues": [
    {
      "file_path": "string",
      "finding_id": "string",
      "description": "string",
      "recommendation": "string"
    }
  ],
  "high_priority_issues": [
    {
      "file_path": "string",
      "finding_id": "string",
      "description": "string",
      "recommendation": "string"
    }
  ],
  "cross_cutting_concerns": [
    {
      "concern": "string (issue that affects multiple files)",
      "affected_files": "array of strings",
      "recommendation": "string"
    }
  ],
  "best_practices_gaps": [
    {
      "area": "string (domain where best practices are lacking)",
      "current_state": "string",
      "recommended_state": "string",
      "implementation_guidance": "string"
    }
  ],
  "overall_assessment": {
    "governance_maturity": "string (initial|developing|defined|quantitatively_managed|optimizing)",
    "compliance_score": "number (0-100)",
    "risk_level": "string (low|medium|high|critical)",
    "priority_recommendations": "array of strings"
  }
}
```

---

## SPECIFIC ANALYSIS REQUIREMENTS

### For Workflow Files
1. **Header Completeness**: Verify all required fields are present and accurate
2. **Phase Logic**: Ensure phases flow logically and steps are properly sequenced
3. **Step Actionability**: Each step must be specific and actionable
4. **Reference Validity**: All referenced files and workflows must exist
5. **Terminology**: All {CAPITALIZED} terms must be defined in Terminology_Glossary.md
6. **Execution Modes**: If defined, must match agent-specific patterns
7. **Template Compliance**: Must follow applicable template structures

### For Rules Files
1. **YAML Validity**: Frontmatter must be valid YAML/JSON
2. **Rule Clarity**: Rules must be clear, specific, and enforceable
3. **Authority Separation**: Must maintain proper separation between authority and intelligence
4. **Dependencies**: Rule dependencies must be documented and valid
5. **Consistency**: Rules must be consistent with AGENTS.md definitions
6. **Enforcement**: Rules must be enforceable and measurable

### For Configuration Files
1. **Syntax Validity**: Must be valid JSON/YAML/TOML
2. **Schema Compliance**: Must conform to expected schema structure
3. **Security**: No sensitive data or secrets in configuration
4. **References**: All referenced paths and files must exist
5. **Version Compatibility**: Configuration must be compatible with current versions

### For Cross-Reference Integrity
1. **File Existence**: All referenced files must exist
2. **Path Accuracy**: All file paths must be accurate and relative
3. **Link Validity**: All links must resolve to valid targets
4. **Circular Dependencies**: Detect and report any circular references
5. **Orphaned References**: Identify references to non-existent content

---

## BEST PRACTICE RESEARCH REQUIREMENTS

For EACH file, you MUST perform web searches using the following patterns:

### For Workflow Files:
- "AI agent workflow documentation best practices 2026"
- "Technical workflow documentation standards and templates"
- "Governance workflow design patterns and best practices"
- "Multi-agent system workflow coordination best practices"

### For Rules Files:
- "AI agent rule documentation and governance best practices"
- "Technical rule definition and enforcement patterns"
- "Agent governance framework documentation standards"
- "Multi-agent system rule hierarchy and dependency best practices"

### For Configuration Files:
- "AI agent configuration management best practices"
- "Technical configuration schema design patterns"
- "Hook and skill configuration documentation standards"
- "Configuration security and version control best practices"

### For Documentation Files:
- "Technical documentation quality standards and best practices"
- "Markdown documentation structure and formatting guidelines"
- "API documentation and reference documentation patterns"
- "Technical writing best practices for developer documentation"

### For Cross-Reference Integrity:
- "Documentation cross-reference integrity best practices"
- "Technical documentation link validation and maintenance"
- "Governance document dependency management patterns"

---

## QUALITY ASSURANCE REQUIREMENTS

### Self-Validation Checklist
Before finalizing your report, ensure:

1. **Coverage Verification**: Every governance file has been scanned
2. **Line-by-Line Analysis**: No lines were skipped in any file
3. **Best Practice Research**: Web searches were performed for EACH file
4. **Schema Compliance**: Output follows the exact schema specified
5. **Citation Accuracy**: All line numbers and references are accurate
6. **Absence Handling**: Missing information is marked as "NOT FOUND"
7. **Specificity**: All findings are specific with actionable recommendations
8. **Consistency**: Analysis criteria are applied consistently across files

### Confidence Scoring
For each finding, include a confidence score (0-100) based on:
- **Evidence Strength**: How clear is the evidence for this finding?
- **Best Practice Alignment**: How strongly does this violate established best practices?
- **Impact Assessment**: How significant is the impact of this issue?
- **Recommendation Clarity**: How clear and actionable is the recommendation?

---

## TIME AND RESOURCE EXPECTATIONS

This scan is designed to be **extremely comprehensive and time-intensive**. 

**Expected Duration**: Several hours to several days depending on the number of files
**Expected Token Usage**: Very high (comprehensive line-by-line analysis + web searches)
**Expected Output Size**: Extensive (detailed findings for each file)

**Do NOT rush this process**. Thoroughness and accuracy are more important than speed.

---

## OUTPUT DELIVERABLES

1. **Individual File Reports**: One JSON object per file following the File-Level Finding Schema
2. **Consolidated Summary Report**: Single JSON object following the Consolidated Report Schema
3. **Executive Summary**: Human-readable summary of key findings and priorities
4. **Detailed Findings Document**: Human-readable detailed findings with specific recommendations

---

## HANDLING INSTRUCTIONS

### If You Encounter:
- **Missing files**: Document as "NOT FOUND" with expected location
- **Unreadable files**: Document as "ERROR" with reason and attempt recovery
- **Ambiguous content**: Document as "AMBIGUOUS" with clarification questions
- **Conflicting information**: Document as "CONFLICT" with details and reconciliation suggestions
- **Best practice uncertainty**: Document as "UNCERTAIN" with reasoning and multiple options

### Quality Standards:
- **Precision**: Be precise in your language and findings
- **Evidence**: Provide specific evidence for each finding
- **Actionability**: Make recommendations specific and actionable
- **Context**: Provide context for why something is an issue
- **Prioritization**: Prioritize findings by severity and impact

---

## SCAN COMPLETION CRITERIA

The scan is considered complete when:

1. ✅ Every governance file has been examined line by line
2. ✅ Best practice research has been performed for each file
3. ✅ Findings are documented in the specified schema format
4. ✅ All critical and high-severity issues are identified
5. ✅ Cross-cutting concerns are consolidated
6. ✅ Overall assessment with maturity score is provided
7. ✅ Actionable recommendations are prioritized
8. ✅ Self-validation checklist is completed

---

## EXAMPLE FINDING FORMAT

```json
{
  "file_path": "Workflow/Planner/Planner_Scanner_Workflow.md",
  "file_type": "workflow",
  "scan_status": "COMPLETE",
  "best_practice_research": {
    "search_performed": true,
    "search_query": "AI agent workflow documentation best practices 2026",
    "best_practices_found": "Workflow documentation should include clear phase organization, step numbering, and comprehensive reference sections. Current standards emphasize modular workflow design with clear trigger/end states.",
    "sources": [
      "https://example.com/workflow-best-practices",
      "https://example.com/technical-documentation-standards"
    ]
  },
  "compliance_analysis": {
    "header_structure": {
      "status": "PARTIAL",
      "issues": [
        {
          "line_number": 8,
          "description": "Duration field uses vague terminology 'Extended' without specific timeframes",
          "severity": "MEDIUM"
        }
      ]
    },
    "content_organization": {
      "status": "PASS",
      "issues": []
    },
    "cross_references": {
      "status": "FAIL",
      "issues": [
        {
          "line_number": 45,
          "description": "Reference to Workflow/Workflow_Reference/Execution_Strategy_Guidelines.md which does not exist",
          "severity": "HIGH"
        }
      ]
    },
    "terminology_consistency": {
      "status": "PASS",
      "issues": []
    },
    "formatting_standards": {
      "status": "PASS",
      "issues": []
    }
  },
  "findings": [
    {
      "id": "WF-PLAN-001",
      "category": "infrastructure",
      "severity": "HIGH",
      "line_number": 45,
      "issue_type": "incorrect",
      "description": "Cross-reference to non-existent file Execution_Strategy_Guidelines.md",
      "evidence": "Reference Files: - Execution Strategy: Workflow/Workflow_Reference/Execution_Strategy_Guidelines.md",
      "best_practice_violation": "Documentation cross-reference integrity - all references must resolve to existing files",
      "recommendation": "Remove reference to non-existent file or create the missing reference file",
      "recommendation_type": "modify",
      "priority": "high",
      "complexity": "simple",
      "confidence_score": 95
    }
  ],
  "summary": {
    "total_findings": 1,
    "critical_count": 0,
    "high_count": 1,
    "medium_count": 0,
    "low_count": 0,
    "overall_assessment": "NEEDS_IMPROVEMENT"
  }
}
```

---

## FINAL INSTRUCTIONS

This is a **comprehensive, exhaustive scan** designed to identify every possible issue, inconsistency, inefficiency, and best practice violation in the SovereignAI harness documentation.

**Take your time. Be thorough. Be precise. Be complete.**

Your output will be used to significantly improve the quality, compliance, and effectiveness of the SovereignAI multi-agent system governance framework.

**Begin the scan now.**