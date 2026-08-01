# AutoGen to Microsoft Agent Framework Migration Guide

**Source URL:** https://learn.microsoft.com/en-us/agent-framework/migration-guide/from-autogen/

---

A comprehensive guide for migrating from AutoGen to the Microsoft Agent Framework Python SDK.

## Background

[AutoGen](https://github.com/microsoft/autogen) is a framework for building AI agents and multi-agent systems using large language models (LLMs). It started as a research project at Microsoft Research and pioneered several concepts in multi-agent orchestration, such as GroupChat and event-driven agent runtime. The project has been a fruitful collaboration of the open-source community and many important features came from external contributors.

[Microsoft Agent Framework](https://github.com/microsoft/agent-framework) is a new multi-language SDK for building AI agents and workflows using LLMs. It represents a significant evolution of the ideas pioneered in AutoGen and incorporates lessons learned from real-world usage. It's developed by the core AutoGen and Semantic Kernel teams at Microsoft, and is designed to be a new foundation for building AI applications going forward.

## Key Similarities and Differences

### What Stays the Same

The foundations are familiar. You still create agents around a model client, provide instructions, and attach tools. Both libraries support function-style tools, token streaming, multimodal content, and async I/O.

```python
# Both frameworks follow similar patterns
# AutoGen
agent = AssistantAgent(name="assistant", model_client=client, tools=[my_tool])
result = await agent.run(task="Help me with this task")

# Agent Framework
agent = Agent(name="assistant", client=client, tools=[my_tool])
result = await agent.run("Help me with this task")
```

### Key Differences

1. **Orchestration style**: AutoGen pairs an event-driven core with a high‑level `Team`. Agent Framework centers on a typed, graph‑based `Workflow` that routes data along edges and activates executors when inputs are ready.
2. **Tools**: AutoGen wraps functions with `FunctionTool`. Agent Framework uses `@tool`, infers schemas automatically, and adds hosted tools such as a code interpreter and web search.
3. **Agent behavior**: `AssistantAgent` is single‑turn unless you increase `max_tool_iterations`. `Agent` is multi‑turn by default and keeps invoking tools until it can return a final answer.
4. **Runtime**: AutoGen offers embedded and experimental distributed runtimes. Agent Framework focuses on single‑process composition today; distributed execution is planned.

## Model Client Creation and Configuration

Both frameworks provide model clients for major AI providers, with similar but not identical APIs.

| Feature | AutoGen | Agent Framework |
| --- | --- | --- |
| OpenAI Client | `OpenAIChatCompletionClient` | `OpenAIChatCompletionClient` |
| OpenAI Responses Client | ❌ Not available | `OpenAIChatClient` |
| Azure OpenAI | `AzureOpenAIChatCompletionClient` | `OpenAIChatCompletionClient` |
| Azure OpenAI Responses | ❌ Not available | `OpenAIChatClient` |
| Azure AI | `AzureAIChatCompletionClient` | `FoundryChatClient` / `FoundryAgent` |
| Anthropic | `AnthropicChatCompletionClient` | 🚧 Planned |
| Ollama | `OllamaChatCompletionClient` | 🚧 Planned |
| Caching | `ChatCompletionCache` wrapper | 🚧 Planned |

### AutoGen Model Clients

```python
from autogen_ext.models.openai import OpenAIChatCompletionClient, AzureOpenAIChatCompletionClient

# OpenAI
client = OpenAIChatCompletionClient(
    model="gpt-5",
    api_key="your-key"
)

# Azure OpenAI
client = AzureOpenAIChatCompletionClient(
    azure_endpoint="https://your-endpoint.openai.azure.com/",
    azure_deployment="gpt-5",
    api_version="2024-12-01",
    api_key="your-key"
)
```

### Agent Framework ChatClients

```python
from agent_framework.openai import OpenAIChatCompletionClient
from azure.identity import AzureCliCredential

# OpenAI (reads API key from environment)
client = OpenAIChatCompletionClient(model="gpt-5")

# Azure OpenAI (pass explicit Azure routing inputs)
client = OpenAIChatCompletionClient(
    model="gpt-5",
    azure_endpoint="https://your-endpoint.openai.azure.com/",
    api_version="2024-12-01",
    credential=AzureCliCredential(),
)
```

### Responses API Support (Agent Framework Exclusive)

Agent Framework's `OpenAIChatClient` provides Responses API support for both direct OpenAI and Azure OpenAI routing, including reasoning models and structured responses not available in AutoGen:

```python
from agent_framework.openai import OpenAIChatClient
from azure.identity import AzureCliCredential

# Azure OpenAI with Responses API
azure_responses_client = OpenAIChatClient(
    model="gpt-5",
    azure_endpoint="https://your-endpoint.openai.azure.com/",
    api_version="2024-12-01",
    credential=AzureCliCredential(),
)

# OpenAI with Responses API
openai_responses_client = OpenAIChatClient(model="gpt-5")
```

## Single-Agent Feature Mapping

### Basic Agent Creation and Execution

Both frameworks support similar patterns for basic agent creation and execution, with minor API differences.

### Managing Conversation State with AgentSession

Agent Framework provides `AgentSession` for managing conversation state, similar to AutoGen's state management approaches.

### OpenAI Assistant Agent Equivalence

Agent Framework provides equivalent functionality to AutoGen's OpenAI Assistant Agent through its agent model.

### Streaming Support

Both frameworks support token streaming for real-time response generation.

### Message Types and Creation

Both frameworks support similar message types and creation patterns.

### Tool Creation and Integration

- **AutoGen**: Uses `FunctionTool` wrapper
- **Agent Framework**: Uses `@tool` decorator with automatic schema inference

### Hosted Tools (Agent Framework Exclusive)

Agent Framework includes hosted tools like code interpreter and web search that are not available in AutoGen.

### MCP Server Support

Both frameworks support Model Context Protocol (MCP) servers for tool integration.

### Agent-as-a-Tool Pattern

Both frameworks support the agent-as-a-tool pattern for multi-agent systems.

### Middleware (Agent Framework Feature)

Agent Framework includes middleware capabilities for request/response interception and modification.

### Custom Agents

Both frameworks support custom agent creation with specialized behaviors.

## Multi-Agent Feature Mapping

### Programming Model Overview

- **AutoGen**: Event-driven core with high-level `Team`
- **Agent Framework**: Typed, graph-based `Workflow` with data routing along edges

### Workflow vs GraphFlow

Agent Framework introduces graph-based workflows with typed data flow, different from AutoGen's event-driven approach.

### Nesting Patterns

Both frameworks support nesting patterns for complex multi-agent systems.

### Group Chat Patterns

Agent Framework provides equivalent patterns to AutoGen's GroupChat:

- **RoundRobinGroupChat Pattern**: Sequential agent execution
- **MagenticOneGroupChat Pattern**: Coordinated multi-agent collaboration
- **Future Patterns**: Additional patterns planned

### Human-in-the-Loop with Request Response

Both frameworks support human-in-the-loop workflows with different API approaches.

### Checkpointing and Resuming Workflows

Agent Framework provides checkpointing capabilities for workflow persistence and resumption.

## Observability

Both frameworks provide observability features for monitoring and debugging agent systems.

## Conclusion

The migration from AutoGen to Microsoft Agent Framework represents an evolution of multi-agent system development, with improved tool support, better orchestration patterns, and enhanced observability. The migration path is designed to be gradual, with familiar concepts preserved and new capabilities added.

[Content truncated due to length - full documentation available at source URL]
