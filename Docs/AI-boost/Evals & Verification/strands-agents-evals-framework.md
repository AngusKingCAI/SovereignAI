# Strands Agents Evals SDK

**Source URL:** https://github.com/strands-agents/evals

## Description

Strands Evals SDK is a comprehensive evaluation framework for AI agents and LLM applications. It provides tools ranging from simple output validation to complex multi-agent interaction analysis, trajectory evaluation, and automated experiment generation. It's designed to measure and improve AI systems with sophisticated assessment capabilities.

## Key Features

- **Multiple Evaluation Types**: Output evaluation, trajectory analysis, tool usage assessment, and interaction evaluation
- **Multimodal Evaluation**: MLLM-as-a-Judge evaluators for image-to-text tasks with built-in rubrics
- **Dynamic Simulators**: Multi-turn conversation simulation with realistic user behavior and goal-oriented interactions
- **LLM-as-a-Judge**: Built-in evaluators using language models for sophisticated assessment with structured scoring
- **Trace-based Evaluation**: Analyze agent behavior through OpenTelemetry execution traces
- **Automated Experiment Generation**: Generate comprehensive test suites from context descriptions
- **Custom Evaluators**: Extensible framework for domain-specific evaluation logic
- **Experiment Management**: Save, load, and version evaluation experiments with JSON serialization
- **Failure Detection & Root Cause Analysis**: Automatically detect failures and diagnose root causes with actionable fix recommendations
- **Chaos Testing**: Deterministic fault injection via Strands plugin hooks — simulate tool timeouts, network errors, and response corruption
- **Red Team Evaluation**: Adversarial safety testing with built-in attack strategies (Crescendo, GOAT, PAIR, BadLikertJudge, SequentialBreak)

## Installation

```bash
pip install strands-agents-evals
```

## Quick Start Example

```python
from strands import Agent
from strands_evals import Case, Experiment
from strands_evals.evaluators import OutputEvaluator

# Create test cases
test_cases = [
    Case[str, str](
        name="knowledge-1",
        input="What is the capital of France?",
        expected_output="The capital of France is Paris.",
        metadata={"category": "knowledge"}
    )
]
```

## Evaluation Capabilities

1. **Output Evaluation**: Validate agent outputs against expected results
2. **Trajectory Analysis**: Analyze the sequence of actions an agent takes
3. **Tool Usage Assessment**: Evaluate how agents use available tools
4. **Interaction Evaluation**: Assess multi-agent interactions and conversations
5. **Safety Testing**: Red team evaluation for adversarial attacks
6. **Resilience Testing**: Chaos testing for fault tolerance

## Advanced Features

- **Multi-language Support**: Python SDK and TypeScript SDK available
- **Integration Tools**: Comprehensive tooling for different evaluation needs
- **Documentation & Samples**: Extensive documentation and sample code
- **Community Support**: Active Discord community for support

## Repository Stats

- 167 stars, 49 forks
- 193 commits
- Apache-2.0 license
- Active development with comprehensive documentation
- Both Python and TypeScript support

## Best For

Organizations that need:
- Comprehensive evaluation framework for production agents
- Advanced safety and security testing
- Multi-agent system evaluation
- Custom evaluation logic for specific domains
- Integration with OpenTelemetry for tracing
- Chaos testing for resilience evaluation