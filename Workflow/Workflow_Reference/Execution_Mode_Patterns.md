# Execution Mode Patterns (General Reference)

**Purpose**: General reference for execution mode patterns across all agent workflows.

## Agent-Specific Execution Mode Patterns

Each agent defines its own execution mode patterns based on its operational needs and workflow types. Refer to agent-specific Reference folders for detailed execution mode definitions:

### Architect Execution Mode Patterns
- **Location**: Workflow/Architect/Reference/Execution_Mode_Patterns.md
- **Modes**: Full Comprehensive, Basic Essential, Targeted, Quick Check
- **Focus**: Architecture consistency validation workflows
- **Use Case**: Infrastructure and governance validation

### Reviewer Execution Mode Patterns
- **Location**: Workflow/Reviewer/Reference/Execution_Mode_Patterns.md
- **Modes**: Manual, Manual Batched, Automatic Batched
- **Focus**: File processing and compliance scanning workflows
- **Use Case**: Code review and best practice verification

### Other Agent Execution Modes
- **Executor**: Implementation and execution patterns (see Workflow/Executor/Reference/)
- **Planner**: Planning and strategy patterns (see Workflow/Planner/Reference/)
- **Researcher**: Research and analysis patterns (see Workflow/Researcher/Reference/)

## Universal Execution Mode Concepts

### Common Execution Mode Elements
All agent-specific execution modes should include:
- **Mode Definitions**: Clear behavior specifications for each mode
- **Checkpoint Handling**: How checkpoints are managed in each mode
- **Failure Handling**: How failures are handled in each mode
- **User Control**: Level of user control in each mode
- **Use Cases**: When to use each mode
- **Handling Patterns**: Step-by-step execution patterns
- **Failure Patterns**: Failure recovery patterns
- **Retry Logic**: Retry configuration and implementation

### Universal Retry Logic
All execution modes should implement consistent retry logic:
- **Max Retries**: 3 retries maximum
- **Backoff Pattern**: Exponential backoff (1s, 2s, 4s, 8s, etc.)
- **Retry Criteria**: Configurable based on error type
- **Retry Logging**: Log each retry attempt with metadata

### Universal State Management
All execution modes should implement consistent state management:
- **Mode Storage**: Store selected execution mode in workflow state
- **Progress Tracking**: Track progress according to mode requirements
- **Audit Trail**: Log mode-specific actions for audit trail

## Execution Mode Design Principles

### Agent-Specific Customization
- Each agent defines execution modes based on its operational needs
- Modes should reflect the agent's specific workflow types and use cases
- Agent-specific patterns are stored in agent Reference folders

### Universal Consistency
- All execution modes should follow universal retry logic patterns
- All execution modes should implement consistent state management
- All execution modes should provide clear checkpoint and failure handling

### Workflow Integration
- Execution modes are defined in workflow headers
- Phase 1 of each workflow presents execution mode options
- Workflows reference their agent-specific execution mode patterns

## Template Integration

Workflow templates should reference agent-specific execution mode patterns:
- **Phase 1**: Present agent-specific execution mode options
- **Header**: Include "Execution Modes" field with agent-specific options
- **References**: Link to agent-specific Execution_Mode_Patterns.md
- **Patterns**: Apply agent-specific handling and failure patterns