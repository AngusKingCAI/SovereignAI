# SovereignAI Repository Categorization System

**Purpose**: Defines detailed categorization rules for all directories to ensure maximum discipline and consistency  
**Status**: Active  
**Version**: 1.0  
**Created**: 2026-07-28  
**Authority**: Architect Agent

---

## Core Categorization Principles

1. **No Flat Organization**: Every directory must have subdirectories for categorization
2. **Single Responsibility**: Each subdirectory has a single, clear purpose
3. **Naming Convention**: Subdirectory names must be descriptive and follow established patterns
4. **Categorization Completeness**: Every file must belong to a specific category
5. **No Mixed Categories**: Files cannot be placed across multiple categories
6. **Category Evolution**: New categories require Architect approval and documentation update

---

## Scripts/ Directory Categorization

### Structure
```
Scripts/
├── SchemaValidation/          # Schema validation scripts and schemas
├── Infrastructure/             # Infrastructure automation scripts
├── Testing/                    # Testing and validation scripts
├── Build/                      # Build and compilation scripts
├── Deployment/                 # Deployment automation scripts
├── Maintenance/                # Maintenance and cleanup scripts
└── Utilities/                  # General utility scripts
```

### Category Rules

#### SchemaValidation/
**Purpose**: Schema validation scripts and JSON schemas  
**File Types**:
- Schema validation scripts (Python, Bash)
- JSON schema files (*.json)
- Schema configuration files

**Naming Conventions**:
- Validation scripts: `validate_{purpose}.py`
- Schema files: `{purpose}-schema.json`
- Config files: `{purpose}_config.json`

**Examples**:
- `validate_schemas.py`
- `workflow-schema.json`
- `rules-schema.json`

#### Infrastructure/
**Purpose**: Infrastructure automation and setup scripts  
**File Types**:
- Directory creation scripts
- Environment setup scripts
- Configuration management scripts
- Hook installation scripts

**Naming Conventions**:
- Setup scripts: `setup_{purpose}.py`
- Infrastructure scripts: `{infrastructure_type}_{action}.py`

**Examples**:
- `setup_directories.py`
- `install_hooks.py`

#### Testing/
**Purpose**: Testing and validation scripts  
**File Types**:
- Test runners
- Validation scripts
- Quality check scripts
- Coverage analysis scripts

**Naming Conventions**:
- Test scripts: `test_{purpose}.py`
- Validation scripts: `validate_{purpose}.py`

**Examples**:
- `test_consistency.py`
- `validate_structure.py`

#### Build/
**Purpose**: Build and compilation scripts  
**File Types**:
- Build scripts
- Compilation scripts
- Dependency management scripts

**Naming Conventions**:
- Build scripts: `build_{purpose}.py`
- Compile scripts: `compile_{purpose}.py`

**Examples**:
- `build_docs.py`
- `compile_schemas.py`

#### Deployment/
**Purpose**: Deployment automation scripts  
**File Types**:
- Deployment scripts
- Release scripts
- Version management scripts

**Naming Conventions**:
- Deploy scripts: `deploy_{purpose}.py`
- Release scripts: `release_{purpose}.py`

**Examples**:
- `deploy_production.py`
- `release_version.py`

#### Maintenance/
**Purpose**: Maintenance and cleanup scripts  
**File Types**:
- Cleanup scripts
- Maintenance scripts
- Log rotation scripts

**Naming Conventions**:
- Cleanup scripts: `cleanup_{purpose}.py`
- Maintenance scripts: `maintain_{purpose}.py`

**Examples**:
- `cleanup_logs.py`
- `maintain_cache.py`

#### Utilities/
**Purpose**: General utility scripts  
**File Types**:
- Helper functions
- Utility scripts
- Common tools

**Naming Conventions**:
- Utility scripts: `util_{purpose}.py`
- Helper scripts: `helper_{purpose}.py`

**Examples**:
- `util_format.py`
- `helper_paths.py`

---

## Workflow/ Directory Categorization

### Structure
```
Workflow/
├── Workflow_Reference/        # Universal framework references
│   ├── Execution_Mode_Patterns.md
│   ├── Implementation_Mode_Patterns.md
│   ├── Quality_Assessment_Framework.md
│   ├── Role_Responsibilities_Framework.md
│   ├── Performance_Metrics_Framework.md
│   ├── State_Management_Guidelines.md
│   ├── Execution_Strategy_Guidelines.md
│   ├── Runtime_Prerequisites.md
│   ├── Validation_Enforcement_Patterns.md
│   ├── Convergence_Loop_Patterns.md
│   ├── Quota_Handling_Patterns.md
│   └── Template_Usage_Guidelines.md
├── Architect/                 # Architect-specific workflows
│   ├── Reference/            # Architect reference documents
│   │   ├── Execution_Mode_Patterns.md
│   │   ├── Implementation_Mode_Patterns.md
│   │   └── Option_Evaluation_Framework.md
│   ├── Templates/            # Architect templates
│   └── Architect_General_Workflow.md
│   └── Architect_Consistency_Check_Workflow.md
├── Planner/                   # Planner-specific workflows
│   ├── Reference/            # Planner reference documents
│   │   ├── Execution_Mode_Patterns.md
│   │   ├── Implementation_Mode_Patterns.md
│   │   ├── Convergence_Loop_Specifications.md
│   │   ├── Delivery_Authorization_Specifications.md
│   │   ├── Plan_Batch_Specifications.md
│   │   ├── Role_Responsibilities.md
│   │   ├── Validation_System_Specifications.md
│   │   └── Workflow_Overview.md
│   ├── Templates/            # Planner templates
│   │   ├── Plan_Template.md
│   │   ├── Plan_Brief_Template.md
│   │   └── Plan_Prompt_Template.md
│   └── Planner_Plan_Workflow.md
├── Executor/                  # Executor-specific workflows
│   ├── Reference/            # Executor reference documents
│   │   ├── Execution_Mode_Patterns.md
│   │   ├── Implementation_Mode_Patterns.md
│   │   └── Review_Mode_Patterns.md
│   ├── Templates/            # Executor templates
│   │   └── Handoff_Template.md
│   └── Executor_Implementation_Workflow.md
└── [Other Agents]/            # Following same pattern
```

### Category Rules

#### Workflow_Reference/
**Purpose**: Universal framework references applicable to all agents  
**File Types**:
- Universal framework definitions
- Universal pattern specifications
- Universal guidelines

**Naming Conventions**:
- Framework files: `{Concept}_Patterns.md` or `{Concept}_Framework.md`
- Guidelines: `{Concept}_Guidelines.md`

**Inclusion Criteria**:
- Must be applicable to all agents
- Must represent universal patterns
- No agent-specific content

#### Agent Directories (Architect/, Planner/, Executor/)
**Purpose**: Agent-specific workflows and references  
**Structure Rules**:
- Each agent has its own directory
- Each agent directory has Reference/ and Templates/ subdirectories
- Workflow files placed directly in agent directory

**Reference/ Subdirectory**:
- Agent-specific execution mode patterns
- Agent-specific implementation patterns
- Agent-specific reference documents

**Templates/ Subdirectory**:
- Agent-specific templates
- Agent-specific prompt templates
- Agent-specific handoff templates

---

## Rules/ Directory Categorization

### Structure
```
Rules/
├── Architect/                 # Architect-specific rules
│   └── Architect_Rules.md
├── Planner/                   # Planner-specific rules
│   └── Planner_Rules.md
├── Executor/                  # Executor-specific rules
│   └── Executor_Rules.md
└── [Other Agents]/            # Following same pattern
```

### Category Rules

#### Agent Directories
**Purpose**: Agent-specific rule definitions  
**File Types**:
- Agent rule definitions
- Agent constraint specifications
- Agent governance rules

**Naming Conventions**:
- Rule files: `{Agent}_Rules.md`

**Placement Rules**:
- One rules file per agent
- No subdirectories within agent directories
- Only rule definition files

---

## Docs/ Directory Categorization

### Structure
```
Docs/
├── Code/                      # Code documentation
│   ├── Python/               # Python-specific documentation
│   ├── JavaScript/           # JavaScript-specific documentation
│   ├── Markdown/             # Markdown-specific documentation
│   └── YAML/                 # YAML-specific documentation
├── Research/                  # Research documentation
│   ├── Architecture/          # Architecture research
│   ├── BestPractices/         # Best practices research
│   └── CaseStudies/           # Case study documentation
├── Architecture/              # Architecture documentation
│   ├── DesignPatterns/        # Design pattern documentation
│   ├── SystemArchitecture/    # System architecture docs
│   └── ComponentArchitecture/ # Component architecture docs
├── Governance/                # Governance documentation
│   ├── Rules/                # Rule documentation
│   ├── Workflows/            # Workflow documentation
│   └── Processes/            # Process documentation
└── Repository/                # Repository documentation
    ├── Structure/            # Repository structure docs
    ├── Categorization/       # Categorization rules
    └── Guidelines/          # Repository guidelines
```

### Category Rules

#### Code/
**Purpose**: Language-specific code documentation  
**Categorization**: By programming language  
**File Types**:
- Style guides
- Best practices
- Code patterns
- Language-specific conventions

#### Research/
**Purpose**: Research and analysis documentation  
**Categorization**: By research domain  
**File Types**:
- Architecture research
- Best practices research
- Case studies
- Analysis documents

#### Architecture/
**Purpose**: Architecture documentation  
**Categorization**: By architecture domain  
**File Types**:
- Design patterns
- System architecture
- Component architecture
- Infrastructure documentation

#### Governance/
**Purpose**: Governance documentation  
**Categorization**: By governance domain  
**File Types**:
- Rule documentation
- Workflow documentation
- Process documentation
- Compliance documentation

#### Repository/
**Purpose**: Repository-level documentation  
**Categorization**: By repository domain  
**File Types**:
- Structure documentation
- Categorization rules
- Repository guidelines
- Maintenance documentation

---

## Logs/ Directory Categorization

### Structure
```
Logs/
├── Architect/                 # Architect-specific logs
│   ├── Consistency Review/   # Consistency check results
│   ├── Session/              # Architect session logs
│   └── Validation/           # Architect validation logs
├── Planner/                   # Planner-specific logs
│   ├── Roundtable/            # Round Table review logs
│   │   ├── Internal/         # Internal review logs
│   │   └── External/         # External review logs
│   ├── Session/              # Planner session logs
│   └── Validation/           # Planner validation logs
├── Executor/                  # Executor-specific logs
│   ├── Session/              # Executor session logs
│   ├── Handoff/              # Handoff documentation
│   └── Validation/           # Executor validation logs
└── [Other Agents]/            # Following same pattern
```

### Category Rules

#### Agent Directories
**Purpose**: Agent-specific logging  
**Categorization**: By log type  
**Subdirectories**:
- `Session/` - Session-specific logs
- `Validation/` - Validation results
- Agent-specific categories (e.g., `Consistency Review/`, `Roundtable/`, `Handoff/`)

**Naming Conventions**:
- Session logs: `session-{timestamp}.md`
- Validation logs: `{validation_type}-{timestamp}.md`
- Scan reports: `Scan_{timestamp}.md`

---

## Agents/ Directory Categorization

### Structure
```
Agents/
├── Executor/                  # Executor agent governance
│   ├── AGENTS.md
│   └── [Other governance files]
├── Planner/                   # Planner agent governance
│   ├── AGENTS.md
│   └── [Other governance files]
├── Researcher/                # Researcher agent governance
│   ├── AGENTS.md
│   └── [Other governance files]
└── Reviewer/                  # Reviewer agent governance
    ├── AGENTS.md
    └── [Other governance files]
```

### Category Rules

#### Agent Directories
**Purpose**: Individual agent governance files  
**Categorization**: By agent  
**File Types**:
- Agent configuration files
- Agent-specific rules
- Agent workflow documentation

**Naming Conventions**:
- Agent config: `AGENTS.md`
- Agent rules: `{Agent}_Rules.md`

---

## .devin/ Directory Categorization

### Structure
```
.devin/
├── skills/                    # Agent skill definitions
│   ├── architect/
│   │   └── SKILL.md
│   ├── executor/
│   │   └── SKILL.md
│   ├── planner/
│   │   └── SKILL.md
│   ├── researcher/
│   │   └── SKILL.md
│   └── reviewer/
│       └── SKILL.md
├── hooks.v1.json             # Hook configuration
└── [Other Devin config]
```

### Category Rules

#### skills/
**Purpose**: Agent skill definitions  
**Categorization**: By agent  
**File Types**:
- Skill definition files
- Skill configuration files

**Naming Conventions**:
- Skill files: `SKILL.md` (exactly this name)
- Skill directories: `{agent_name}/` (lowercase)

---

## .claude/ Directory Categorization

### Structure
```
.claude/
├── rules.md                  # Claude Code rules
└── [Other Claude config]
```

### Category Rules

#### Claude Configuration
**Purpose**: Claude Code configuration and rules  
**File Types**:
- Claude Code rules
- Claude Code configuration

**Naming Conventions**:
- Rules files: `rules.md`
- Config files: `{purpose}.json`

---

## Categorization Decision Tree

When creating a file, follow this comprehensive decision tree:

### Scripts/ Directory
1. **Is it a schema validation script?** → Scripts/SchemaValidation/
2. **Is it infrastructure automation?** → Scripts/Infrastructure/
3. **Is it testing/validation?** → Scripts/Testing/
4. **Is it build/compilation?** → Scripts/Build/
5. **Is it deployment?** → Scripts/Deployment/
6. **Is it maintenance?** → Scripts/Maintenance/
7. **Is it a general utility?** → Scripts/Utilities/

### Workflow/ Directory
1. **Is it a universal framework?** → Workflow/Workflow_Reference/
2. **Is it agent-specific?** → Workflow/{Agent}/
   - **Is it a reference document?** → Workflow/{Agent}/Reference/
   - **Is it a template?** → Workflow/{Agent}/Templates/
   - **Is it a workflow file?** → Workflow/{Agent}/

### Docs/ Directory
1. **Is it code documentation?** → Docs/Code/{Language}/
2. **Is it research?** → Docs/Research/{Domain}/
3. **Is it architecture?** → Docs/Architecture/{Domain}/
4. **Is it governance?** → Docs/Governance/{Domain}/
5. **Is it repository documentation?** → Docs/Repository/{Domain}/

### Logs/ Directory
1. **Which agent generated it?** → Logs/{Agent}/
   - **Is it a session log?** → Logs/{Agent}/Session/
   - **Is it validation?** → Logs/{Agent}/Validation/
   - **Is it agent-specific type?** → Logs/{Agent}/{Type}/

---

## Categorization Compliance Checklist

Before creating any file:
- [ ] Determined appropriate top-level directory
- [ ] Determined appropriate subdirectory categorization
- [ ] Verified naming convention compliance
- [ ] Checked if category already exists
- [ ] Confirmed no mixed categorization
- [ ] Updated relevant documentation if new category created

---

## Category Addition Process

When a new category is needed:
1. **Research existing categories** to ensure no overlap
2. **Define clear purpose** for new category
3. **Present category proposal** to user with rationale
4. **Update this Repository_Categorization.md** document
5. **Update STRUCTURE.md** if directory structure changes
6. **Update INDEX.md** with new category information

---

## Categorization Enforcement

### Architect Agent Responsibilities
- Enforce categorization rules during file creation
- Validate categorization compliance before file placement
- Present user approval for new category creation
- Document categorization decisions in workflow logs
- Maintain this Repository_Categorization.md document

### Violation Handling
- Misplaced files: MOVE to correct category
- Uncategorizable files: REQUEST user approval for new category
- Mixed categorization: SEPARATE into appropriate categories
- Naming violations: RENAME to follow conventions

---

**Current Status**: Active  
**Last Updated**: 2026-07-28  
**Maintained By**: Architect Agent  
**Review Frequency**: Monthly or when categorization needs change