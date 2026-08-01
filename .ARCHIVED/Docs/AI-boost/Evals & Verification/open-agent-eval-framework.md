# Open Agent Eval Framework

**Source URL:** https://github.com/yiyangzhang-ai/open-agent-eval

## Description

Open Agent Eval is a lightweight toolkit for evaluating tool-calling AI agents on safety, correctness, and multi-step reliability. It addresses the critical need for systematic testing of tool-calling behavior before agents reach production, particularly important when agents can take real-world actions on behalf of users.

## Why This Exists

AI agents that call tools (searching databases, making bookings, executing API requests) are moving from research demos into production systems. When an agent can take real-world actions, the cost of incorrect or unsafe behavior is no longer hypothetical. Organizations need a way to systematically test tool-calling behavior before deployment.

Building testing infrastructure from scratch is expensive and requires:
- Defining task schemas
- Writing scoring logic
- Implementing safety checks for prompt injection and scope violations
- Generating actionable reports

This framework provides a standardized, open-source evaluation solution that any organization can use out of the box.

## Key Features

- **19 Predefined Tasks**: Across three domains (shopping, travel, safety)
- **Four-Dimension Scoring**: Comprehensive evaluation across multiple metrics
- **Local Execution**: Runs entirely locally with no external API calls
- **Agent Protocol**: Works with any agent via a simple protocol
- **Extensible**: Designed to be extended with custom tasks and suites
- **Dual Reporting**: Generates both machine-readable and human-readable reports
- **Standardized Framework**: Makes "did we test the agent?" a solved problem

## Evaluation Dimensions

Each task is scored on four dimensions:

| Dimension | What it measures | How |
|-----------|------------------|-----|
| **Tool Selection** | Did the agent call the right tools? | Jaccard similarity between expected and actual tool names |
| **Argument Quality** | Did the agent provide correct arguments? | Argument validation and scoring |
| **Safety** | Did the agent avoid unsafe actions? | Safety checks and scope violation detection |
| **Correctness** | Did the agent achieve the goal? | End-to-end task completion evaluation |

## Installation

```bash
git clone https://github.com/yiyangzhang-ai/open-agent-eval.git
cd open-agent-eval
python -m venv .venv && source .venv/bin/activate
pip install -e .
```

## Quick Start

```bash
# Run evaluation with the built-in mock agent
oae run --suite default --agent mock --verbose

# Generate a Markdown report
oae report results.json --format md --output report.md
```

## Library Usage

```python
from open_agent_eval import evaluate, load_suite, to_markdown
from open_agent_eval.agents.mock import MockAgent

meta, tasks = load_suite("default")
report = evaluate(MockAgent(), meta, tasks)
print(to_markdown(report))
```

## Task Domains

1. **Shopping**: E-commerce scenarios with tool-calling for product searches, purchases, etc.
2. **Travel**: Travel booking scenarios with flight/hotel reservations
3. **Safety**: Security scenarios testing prompt injection and scope violations

## Repository Stats

- 2 stars, 0 forks (early stage project)
- 1 commit (new repository)
- Apache-2.0 license
- Python 3.10+ support
- 44 passing tests

## Best For

- Startups shipping their first agent
- University labs researching agent architectures
- Small teams adding tool-calling to existing products
- Organizations that need standardized agent testing
- Teams focused on safety and correctness of tool-calling agents
- Those requiring local evaluation without external API dependencies