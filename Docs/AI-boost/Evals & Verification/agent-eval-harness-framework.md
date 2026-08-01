# Agent Eval Harness Framework

**Source URL:** https://github.com/Siddharth-1001/agent-eval-harness

## Description

Agent Eval Harness is a lightweight, open-source evaluation harness for agentic AI systems that enables tracing, measuring, and comparing AI agents in minutes. It focuses on observability and provides structured traces, automated metrics, and side-by-side comparisons without sending data to any hosted platform, ensuring no vendor lock-in and complete data privacy.

## Why Agent Eval Harness?

Production AI agents fail in subtle ways that are invisible without structured observability:

- **Hallucinated tool arguments** — LLMs fabricate function parameters that look plausible but are wrong
- **Silent latency regressions** — a model update doubles response time and nobody notices
- **Cost creep** — token usage grows 3x after a prompt change
- **Tool failures** — success rates drop from 95% to 60% across deployments

Agent Eval Harness provides the infrastructure to detect and measure these issues systematically.

## Key Features

- **Structured Tracing**: Complete execution traces for agent behavior analysis
- **Automated Metrics**: Built-in metrics for latency, cost, success rates, and more
- **Side-by-Side Comparisons**: Compare different agent versions or configurations
- **No Vendor Lock-in**: All data stays on your machine
- **Local Dashboard**: Built-in web interface for visualizing results
- **Framework Agnostic**: Works with multiple agent frameworks
- **Lightweight**: Minimal dependencies and easy setup

## Supported Frameworks

| Framework | Install Extra | Adapter | Integration Style |
|-----------|---------------|---------|-------------------|
| **LangGraph / LangChain** | `langchain` | `LangGraphTracer` | Context manager with callback handler |
| **OpenAI Agents SDK** | `openai` | `trace_openai_agent` | Decorator with auto-injected hooks |
| **Anthropic** | `anthropic` | Various adapters | Framework-specific integration |
| **CrewAI** | `crewai` | Various adapters | Framework-specific integration |
| **Pydantic AI** | `pydantic-ai` | Various adapters | Framework-specific integration |

## Installation

```bash
# Core (no framework dependencies)
pip install agent-eval-harness

# With a specific framework
pip install 'agent-eval-harness[langchain]'
pip install 'agent-eval-harness[openai]'
pip install 'agent-eval-harness[anthropic]'
pip install 'agent-eval-harness[crewai]'
pip install 'agent-eval-harness[pydantic-ai]'

# All frameworks
pip install 'agent-eval-harness[all]'

# Development
pip install 'agent-eval-harness[dev]'
```

**Requirements:** Python 3.12+

## Quick Start

```bash
# Install
pip install agent-eval-harness

# Run an example (no API key needed — uses mock LLM)
python -m examples.langchain_example

# View results
agent-eval list
agent-eval show <run_id>

# Start the local dashboard
agent-eval dashboard
```

Open http://127.0.0.1:7000 to see the dashboard.

## Key Capabilities

1. **Execution Tracing**: Capture complete agent execution flows
2. **Performance Metrics**: Measure latency, token usage, costs
3. **Error Analysis**: Track and analyze tool failures and errors
4. **Version Comparison**: Compare different agent versions side-by-side
5. **Local Storage**: All evaluation data stored locally
6. **Web Dashboard**: Interactive dashboard for result visualization
7. **Framework Integration**: Easy integration with popular agent frameworks

## Repository Stats

- 20 stars, 0 forks
- 22 commits
- MIT license
- Python 3.12+ support
- Active development with comprehensive examples
- CI/CD pipeline configured

## Best For

Teams that need:
- Local evaluation without external dependencies
- Framework-agnostic evaluation infrastructure
- Real-time observability for agent behavior
- Performance regression detection
- Cost and latency monitoring
- Side-by-side agent comparisons
- Complete data privacy and control
- Quick setup and minimal configuration