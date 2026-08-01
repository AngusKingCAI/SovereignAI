# OpenAI Agents SDK - Agents Documentation

**Source URL:** https://openai.github.io/openai-agents-python/agents/

---

# Agents

Agents are the core building block in your apps. An agent is a large language model (LLM) configured with instructions, tools, and optional runtime behavior such as handoffs, guardrails, and structured outputs.

Use this page when you want to define or customize a single plain `Agent`. If you are deciding how multiple agents should collaborate, read [Agent orchestration](https://openai.github.io/openai-agents-python/docs/agent-orchestration). If the agent should run inside an isolated workspace with manifest-defined files and sandbox-native capabilities, read [Sandbox agent concepts](https://openai.github.io/openai-agents-python/docs/sandbox-agents/concepts).

The SDK uses the Responses API by default for OpenAI models, but the distinction here is orchestration: `Agent` plus `Runner` lets the SDK manage turns, tools, guardrails, handoffs, and sessions for you. If you want to own that loop yourself, use the Responses API directly instead.

## Choose the next guide

Use this page as the hub for agent definition. Jump to the adjacent guide that matches the next decision you need to make.

| If you want to... | Read next |
|-------------------|-----------|
| Choose a model or provider setup | [Models](https://openai.github.io/openai-agents-python/docs/models) |
| Add capabilities to the agent | [Tools](https://openai.github.io/openai-agents-python/docs/tools) |
| Run an agent against a real repo, document bundle, or isolated workspace | [Sandbox agents quickstart](https://openai.github.io/openai-agents-python/docs/sandbox-agents/quickstart) |
| Decide between manager-style orchestration and handoffs | [Agent orchestration](https://openai.github.io/openai-agents-python/docs/agent-orchestration) |
| Configure handoff behavior | [Handoffs](https://openai.github.io/openai-agents-python/docs/handoffs) |
| Run turns, stream events, or manage conversation state | [Running agents](https://openai.github.io/openai-agents-python/docs/running-agents) |
| Inspect final output, run items, or resumable state | [Results](https://openai.github.io/openai-agents-python/docs/results) |
| Share local dependencies and runtime state | [Context management](https://openai.github.io/openai-agents-python/docs/context-management) |
| Add validation or safety checks | [Guardrails](https://openai.github.io/openai-agents-python/docs/guardrails) |
| Add persistent memory | [Sessions overview](https://openai.github.io/openai-agents-python/docs/sessions) |
| Add tracing and debugging | [Tracing](https://openai.github.io/openai-agents-python/docs/tracing) |
| Build voice agents | [Voice agents quickstart](https://openai.github.io/openai-agents-python/docs/voice-agents/quickstart) |
| Build realtime agents | [Realtime agents quickstart](https://openai.github.io/openai-agents-python/docs/realtime-agents/quickstart) |

## Basic configuration

The simplest agent definition includes a name and instructions:

```python
from agents import Agent

agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant",
)
```

## Prompt templates

You can use prompt templates to create dynamic instructions:

```python
from agents import Agent

agent = Agent(
    name="Assistant",
    instructions=f"You are a helpful assistant who speaks {language}",
)
```

## Context

Agents can access context through the `context` parameter:

```python
from agents import Agent

agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant",
    context={"user_id": "123"},
)
```

## Output types

You can specify structured output types:

```python
from agents import Agent
from pydantic import BaseModel

class Response(BaseModel):
    answer: str
    confidence: float

agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant",
    output_type=Response,
)
```

## Multi-agent system design patterns

### Manager (agents as tools)

Use the manager pattern when you want a central agent to coordinate others:

```python
from agents import Agent

manager = Agent(
    name="Manager",
    instructions="You coordinate the work of other agents",
    tools=[specialist1_tool, specialist2_tool],
)
```

### Handoffs

Use handoffs when agents should transfer control based on context:

```python
from agents import Agent, handoff

agent1 = Agent(
    name="Agent1",
    instructions="You are agent 1",
    handoffs=[agent2],
)

agent2 = Agent(
    name="Agent2",
    instructions="You are agent 2",
)
```

## Dynamic instructions

You can modify agent instructions dynamically:

```python
from agents import Agent

agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant",
)

# Update instructions
agent.instructions = "You are now a technical support specialist"
```

## Lifecycle events (hooks)

Agents support lifecycle hooks for custom behavior:

```python
from agents import Agent

@Agent.on_start
def on_start_hook(context):
    print("Agent starting")

@Agent.on_end
def on_end_hook(context):
    print("Agent ending")
```

## Guardrails

Add guardrails to validate inputs and outputs:

```python
from agents import Agent, Guardrail

guardrail = Guardrail(
    name="safety_check",
    instructions="Ensure the response is safe and appropriate",
)

agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant",
    guardrails=[guardrail],
)
```

## Cloning/copying agents

You can clone agents for reuse:

```python
from agents import Agent

original = Agent(name="Assistant", instructions="You are helpful")
clone = original.clone()
```

## Forcing tool use

Force the agent to use specific tools:

```python
from agents import Agent

agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant",
    tools=[tool1, tool2],
    tool_choice="required",
)
```

## Tool use behavior

Configure how tools are used:

```python
from agents import Agent

agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant",
    tools=[tool1, tool2],
    tool_choice="auto",  # or "required", "none"
)
```

[Content truncated due to length - full documentation available at source URL]
