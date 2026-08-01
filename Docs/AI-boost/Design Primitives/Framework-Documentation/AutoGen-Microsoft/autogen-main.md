# AutoGen Main Documentation

**Source URL:** https://microsoft.github.io/autogen/stable/index.html

---

# AutoGen

### A framework for building AI agents and applications

## Studio

An web-based UI for prototyping with agents without writing code. Built on AgentChat.

```bash
pip install -U autogenstudio
autogenstudio ui --port 8080 --appdir ./myapp
```

**Start here if you are new to AutoGen and want to prototype with agents without writing code.**

## AgentChat

A programming framework for building conversational single and multi-agent applications. Built on Core. Requires Python 3.10+.

```python
# pip install -U "autogen-agentchat" "autogen-ext[openai]"
import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

async def main() -> None:
    agent = AssistantAgent("assistant", OpenAIChatCompletionClient(model="gpt-4o"))
    print(await agent.run(task="Say 'Hello World!'"))

asyncio.run(main())
```

**Start here if you are prototyping with agents using Python.**

## Core

An event-driven programming framework for building scalable multi-agent AI systems. Example scenarios:

* Deterministic and dynamic agentic workflows for business processes.
* Research on multi-agent collaboration.
* Distributed agents for multi-language applications.

**Start here if you are getting serious about building multi-agent systems.**

## Extensions

Implementations of Core and AgentChat components that interface with external services or other libraries. You can find and use community extensions or create your own. Examples of built-in extensions:

* `McpWorkbench` for using Model-Context Protocol (MCP) servers.
* `OpenAIAssistantAgent` for using Assistant API.
* `DockerCommandLineCodeExecutor` for running model-generated code in a Docker container.
* `GrpcWorkerAgentRuntime` for distributed agents.

## Available Components

- **Studio**: Web-based UI for prototyping without code
- **AgentChat**: Conversational agent framework for Python
- **Core**: Event-driven framework for scalable multi-agent systems
- **Extensions**: Community and built-in extensions for external services

## Installation

Each component can be installed separately:

- Studio: `pip install -U autogenstudio`
- AgentChat: `pip install -U "autogen-agentchat" "autogen-ext[openai]"`
- Core: `pip install -U autogen-core`
- Extensions: `pip install -U autogen-ext`

## Community

- GitHub: https://github.com/microsoft/autogen
- Discord: https://aka.ms/autogen-discord
- Twitter: https://twitter.com/pyautogen
