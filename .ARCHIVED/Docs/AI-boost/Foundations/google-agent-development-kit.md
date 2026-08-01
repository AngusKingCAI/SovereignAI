# Agent Development Kit: Making it Easy to Build Multi-Agent Applications

**Source:** https://developers.googleblog.com/en/agent-development-kit-easy-to-build-multi-agent-applications/
**Authors:** Erwin Huizenga (Machine Learning Lead), Bo Yang (Software Engineer)
**Date:** April 9, 2025

---

## Overview

The world of AI is rapidly moving beyond single-purpose models towards intelligent, autonomous multi-agent systems. Building these multi-agent systems, however, presents new challenges. That is why today, we have introduced Agent Development Kit (ADK) at Google Cloud NEXT 2025, a new open-source framework from Google designed to simplify the full stack end-to-end development of agents and multi-agent systems. ADK empowers developers like you to build production-ready agentic applications with greater flexibility and precise control.

ADK is the same framework powering agents within Google products like Agentspace and the Google Customer Engagement Suite (CES). By open-sourcing ADK, we aim to provide developers with powerful, flexible tools to build in the rapidly evolving agent landscape. The ADK is designed to be flexible, use different models and build production ready agents for different deployment environments.

---

## Core Pillars of ADK: Build, Interact, Evaluate, Deploy

ADK provides capabilities across the entire agent development lifecycle:

### Multi-Agent by Design
Build modular and scalable applications by composing multiple specialized agents in a hierarchy. Enable complex coordination and delegation.

### Rich Model Ecosystem
Choose the model that works best for your needs. ADK works with your model of choice – whether it is Gemini or your any model accessible via Vertex AI Model Garden. The framework also offers LiteLLM integration letting you choose from a wide selection of models from providers like Anthropic, Meta, Mistral AI, AI21 Labs, and many more!

### Rich Tool Ecosystem
Equip agents with diverse capabilities: use pre-built tools (Search, Code Exec), Model Context Protocol (MCP) tools, integrate 3rd-party libraries (LangChain, LlamaIndex), or even use other agents as tools (LangGraph, CrewAI, etc).

### Built-in Streaming
Interact with your agents in human-like conversations with ADK's unique bidirectional audio and video streaming capabilities. With just a few lines of code, you can create natural interactions that change how you work with agents – moving beyond text into rich, multimodal dialogue.

### Flexible Orchestration
Define workflows using workflow agents (`Sequential`, `Parallel`, `Loop`) for predictable pipelines, or leverage LLM-driven dynamic routing (`LlmAgent` transfer) for adaptive behavior.

### Integrated Developer Experience
Develop, test, and debug locally with a powerful CLI and a visual Web UI. Inspect events, state, and agent execution step-by-step.

### Built-in Evaluation
Systematically assess agent performance by evaluating both the final response quality and the step-by-step execution trajectory against predefined test cases.

### Easy Deployment
Containerize and deploy your agents anywhere.

---

## Getting Started with Your First Agent

While we encourage you to explore the examples in the docs, the core idea is Pythonic simplicity. You define your agent's logic, the tools it can use, and how it should process information. ADK provides the structure to manage state, orchestrate tool calls, and interact with the underlying LLMs.

### Basic Agent Example

```python
from google.adk.agents import LlmAgent 
from google.adk.tools import google_Search

dice_agent = LlmAgent(
    model="gemini-2.0-flash-exp", # Required: Specify the LLM 
    name="question_answer_agent", # Required: Unique agent name
    description="A helpful assistant agent that can answer questions.",
    instruction="""Respond to the query using google search""",
    tools=[google_search], # Provide an instance of the tool
)

# you can run this by using adk web
```

This simple example shows the basic structure. ADK truly shines when building more complex applications involving multiple agents, sophisticated tool use, and dynamic orchestration, all while maintaining control.

ADK offers flexibility in the way you interact with your agents: CLI, Web UI, API Server and API (Python). The way you define your agent (the core logic within `agent.py`) is the same regardless of how you choose to interact with it. The difference lies in how you initiate and manage the interaction.

---

## Building Multi-Agent Applications with ADK

ADK truly shines when you move beyond single agents to build collaborative multi-agent systems that leverage tools. Imagine creating a team of specialized agents where a primary agent can delegate tasks based on the conversation. ADK makes this easy through hierarchical structures and intelligent routing.

### Example: Weather Agent with Delegation

Let's walk through an illustrative example – a `WeatherAgent` that handles weather queries but delegates greetings to a specialized GreetingAgent.

#### 1. Define a Tool

Agents use tools to perform actions. Here, our `WeatherAgent` needs a tool to fetch weather data. We define a Python function; ADK uses its `docstring` to understand when and how to use it.

```python
def get_weather(city: str) -> Dict:
    # Best Practice: Log tool execution for easier debugging
    print(f"--- Tool: get_weather called for city: {city} ---")
    city_normalized = city.lower().replace(" ", "") # Basic input normalization

    # Mock weather data for simplicity
    mock_weather_db = {
        "newyork": {"status": "success", "report": "The weather in New York is sunny with a temperature of 25°C."},
        "london": {"status": "success", "report": "It's cloudy in London with a temperature of 15°C."},
        "tokyo": {"status": "success", "report": "Tokyo is experiencing light rain and a temperature of 18°C."},
        "chicago": {"status": "success", "report": "The weather in Chicago is sunny with a temperature of 25°C."},
        "toronto": {"status": "success", "report": "It's partly cloudy in Toronto with a temperature of 30°C."},
        "chennai": {"status": "success", "report": "It's rainy in Chennai with a temperature of 15°C."},
    }

    # Best Practice: Handle potential errors gracefully within the tool
    if city_normalized in mock_weather_db:
        return mock_weather_db[city_normalized]
    else:
        return {"status": "error", "error_message": f"Sorry, I don't have weather information for '{city}'."}
```

#### 2. Define the Agents and Their Relationship

We use `LlmAgent` to create our agents. Pay close attention to the instruction and description fields – the LLM relies heavily on these for understanding roles and making delegation decisions using auto delegations for sub agents.

```python
greeting_agent = Agent(
    model=LiteLlm(model="anthropic/claude-3-sonnet-20240229"),
    name="greeting_agent",
    instruction="You are the Greeting Agent. Your ONLY task is to provide a friendly greeting to the user. Do not engage in any other conversation or tasks.",
    # Crucial for delegation: Clear description of capability
    description="Handles simple greetings and hellos",
)

farewell_agent = Agent(
    model=LiteLlm(model="anthropic/claude-3-sonnet-20240229"),
    name="farewell_agent",
    instruction="You are the Farewell Agent. Your ONLY task is to provide a polite goodbye message. Do not perform any other actions.",
    # Crucial for delegation: Clear description of capability
    description="Handles simple farewells and goodbyes",
)

root_agent = Agent(
    name="weather_agent_v2", 
    model="gemini-2.0-flash-exp",
    description="You are the main Weather Agent, coordinating a team. - Your main task: Provide weather using the `get_weather` tool. Handle its 'status' response ('report' or 'error_message'). - Delegation Rules: - If the user gives a simple greeting (like 'Hi', 'Hello'), delegate to `greeting_agent`. - If the user gives a simple farewell (like 'Bye', 'See you'), delegate to `farewell_agent`. - Handle weather requests yourself using `get_weather`. - For other queries, state clearly if you cannot handle them.",
    tools=[get_weather], # Root agent still needs the weather tool
    sub_agents=[greeting_agent, farewell_agent]
)
```

### How Delegation Works

- The default agent behavior is to allow delegation
- When processing a user message, the LLM considers the query, the current agent's `description`, and the `description` fields of related agents (parent / sub agents defined in the hierarchy)
- If the LLM determines another agent is a better fit based on its description (e.g., user says "Hi", matching the `GreetingAgent` description, it initiates a transfer

**Clear, distinct descriptions are vital!** The LLM uses them to route tasks effectively.

In this setup, if a user starts with "Hi", the `WeatherAgent` (if it's the root agent processing the input) can recognize it's not a weather query, see the `GreetingAgent` is suitable via its description, and automatically transfer control. If the user asks "What's the weather in Chicago?", the `WeatherAgent` handles it directly using its `get_weather` tool.

This example demonstrates how ADK's hierarchical structure and description-driven delegation allow you to build sophisticated multi-agent systems with clear separation of concerns.

---

## Key Design Principles

### 1. Clear Agent Descriptions
The `description` field is critical for automatic delegation. It should:
- Clearly state the agent's capabilities
- Be distinct from other agents' descriptions
- Help the LLM understand when to delegate

### 2. Focused Agent Instructions
The `instruction` field should:
- Define the agent's specific role
- Set clear boundaries on what the agent should do
- Include delegation rules when appropriate

### 3. Tool Design
Tools should:
- Have clear docstrings that explain their purpose
- Handle errors gracefully
- Log execution for debugging
- Normalize inputs where appropriate

### 4. Hierarchical Organization
Agent hierarchies should:
- Have a clear root agent
- Define explicit delegation rules
- Maintain separation of concerns
- Enable specialization

---

## Evaluation and Testing

ADK includes built-in evaluation capabilities that allow you to:
- Define test cases with expected outputs
- Evaluate both final response quality and execution trajectory
- Compare agent performance across different configurations
- Identify areas for improvement

This systematic evaluation approach helps ensure that agents behave correctly and reliably before deployment.

---

## Deployment

ADK makes deployment straightforward with:
- Containerization support
- Flexible deployment options (any environment)
- Consistent behavior across development and production
- Easy scaling and management

---

## Key Takeaways

1. **Multi-agent by design** - ADK is built from the ground up for multi-agent systems
2. **Flexible model support** - Works with Gemini, Vertex AI, and LiteLLM for broad model compatibility
3. **Rich tool ecosystem** - Pre-built tools, MCP tools, third-party libraries, and agent-as-tool patterns
4. **Built-in streaming** - Audio and video streaming for natural multimodal interactions
5. **Flexible orchestration** - Both workflow agents and LLM-driven dynamic routing
6. **Integrated developer experience** - CLI, Web UI, and powerful debugging tools
7. **Built-in evaluation** - Systematic assessment of agent performance
8. **Easy deployment** - Containerize and deploy anywhere

---

*Note: This content was fetched from the Google Developers Blog and saved for offline reference. For the most up-to-date version, visit the source URL.*
