# LangChain AgentEvals Framework

**Source URL:** https://github.com/langchain-ai/agentevals

## Description

AgentEvals is a comprehensive evaluation package for AI agents that focuses on **agent trajectory** - the intermediate steps an agent takes as it runs. It provides evaluators and utilities for assessing agent performance, particularly important given the black box nature of LLMs and how changes in one part of an agent can affect downstream behavior.

## Key Features

- **Agent Trajectory Evaluation**: Focuses on intermediate steps an agent takes during execution
- **Multiple Evaluation Modes**: 
  - Strict match (same messages in same order)
  - Unordered match (same tool calls in any order)
  - Subset/superset match
  - Tool args match modes
- **LLM-as-Judge**: Uses language models (like OpenAI's o3-mini) to evaluate trajectory accuracy
- **Multi-language Support**: Available in both Python and TypeScript
- **Graph Trajectory**: Specialized evaluators for graph-based agent workflows
- **LangSmith Integration**: Seamless integration with LangSmith's pytest integration

## Installation

**Python:**
```bash
pip install agentevals
```

**TypeScript:**
```bash
npm install agentevals @langchain/core
```

## Quick Start Example

```python
from agentevals.trajectory.llm import create_trajectory_llm_as_judge, TRAJECTORY_ACCURACY_PROMPT

trajectory_evaluator = create_trajectory_llm_as_judge(
    prompt=TRAJECTORY_ACCURACY_PROMPT,
    model="openai:o3-mini",
)

# Evaluate agent trajectory
eval_result = trajectory_evaluator(outputs=outputs)
```

## Evaluation Types

1. **Agent Trajectory Match**: Compares agent execution against expected trajectories
2. **Trajectory LLM-as-Judge**: Uses LLMs to evaluate trajectory quality and accuracy
3. **Graph Trajectory**: Specialized evaluation for graph-based agent workflows

## Use Cases

- Validating agent behavior before deployment
- Testing agent responses to different inputs
- Ensuring tools are called in correct order
- Evaluating multi-step reasoning processes
- Quality assurance for agentic applications

## Repository Stats

- 675 stars, 54 forks
- 244 commits
- Active development with regular updates
- MIT license
- Comprehensive documentation and examples

## Best For

Teams using LangChain/LangGraph who need:
- Structured evaluation of agent trajectories
- Integration with existing LangChain workflows
- Both Python and TypeScript support
- Production-ready evaluation infrastructure