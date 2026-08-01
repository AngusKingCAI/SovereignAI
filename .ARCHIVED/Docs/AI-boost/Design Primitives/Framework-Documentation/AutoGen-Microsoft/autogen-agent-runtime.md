# AutoGen Agent and Agent Runtime

**Source URL:** https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/framework/agent-and-agent-runtime.html

---

# Agent and Agent Runtime

In this and the following section, we focus on the core concepts of AutoGen: agents, agent runtime, messages, and communication – the foundational building blocks for an multi-agent applications.

**Note**: The Core API is designed to be unopinionated and flexible. So at times, you may find it challenging. Continue if you are building an interactive, scalable and distributed multi-agent system and want full control of all workflows. If you just want to get something running quickly, you may take a look at the [AgentChat API](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/index.html).

## Agent Overview

An agent in AutoGen is an entity defined by the base interface [`Agent`](https://microsoft.github.io/autogen/stable/reference/python/autogen_core.base.Agent.html). It has a unique identifier of the type [`AgentId`](https://microsoft.github.io/autogen/stable/reference/python/autogen_core.base.AgentId.html), a metadata dictionary of the type [`AgentMetadata`](https://microsoft.github.io/autogen/stable/reference/python/autogen_core.base.AgentMetadata.html).

In most cases, you can subclass your agents from higher level class [`RoutedAgent`](https://microsoft.github.io/autogen/stable/reference/python/autogen_core.base.RoutedAgent.html) which enables you to route messages to corresponding message handler specified with [`message_handler()`](https://microsoft.github.io/autogen/stable/reference/python/autogen_core.base.message_handler.html) decorator and proper type hint for the `message` variable.

## Agent Runtime

An agent runtime is the execution environment for agents in AutoGen. Similar to the runtime environment of a programming language, an agent runtime provides the necessary infrastructure to facilitate communication between agents, manage agent lifecycles, enforce security boundaries, and support monitoring and debugging.

For local development, developers can use [`SingleThreadedAgentRuntime`](https://microsoft.github.io/autogen/stable/reference/python/autogen_core.runtime.SingleThreadedAgentRuntime.html), which can be embedded in a Python application.

**Note**: Agents are not directly instantiated and managed by application code. Instead, they are created by the runtime when needed and managed by the runtime.

If you are already familiar with [AgentChat](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/index.html), it is important to note that AgentChat's agents such as [`AssistantAgent`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.agents.AssistantAgent.html) are created by application and thus not directly managed by the runtime. To use an AgentChat agent in Core, you need to create a wrapper Core agent that delegates messages to the AgentChat agent and let the runtime manage the wrapper agent.

## Implementing an Agent

To implement an agent, the developer must subclass the [`RoutedAgent`](https://microsoft.github.io/autogen/stable/reference/python/autogen_core.base.RoutedAgent.html) class and implement a message handler method for each message type the agent is expected to handle using the [`message_handler()`](https://microsoft.github.io/autogen/stable/reference/python/autogen_core.base.message_handler.html) decorator.

```python
from dataclasses import dataclass

from autogen_core import AgentId, MessageContext, RoutedAgent, message_handler


@dataclass
class MyMessageType:
    content: str


class MyAgent(RoutedAgent):
    def __init__(self) -> None:
        super().__init__("MyAgent")

    @message_handler
    async def handle_my_message_type(self, message: MyMessageType, ctx: MessageContext) -> None:
        print(f"{self.id.type} received message: {message.content}")
```

This agent only handles `MyMessageType` and messages will be delivered to `handle_my_message_type` method. Developers can have multiple message handlers for different message types by using [`message_handler()`](https://microsoft.github.io/autogen/stable/reference/python/autogen_core.base.message_handler.html) decorator and setting the type hint for the `message` variable in the handler function.

## Using an AgentChat Agent

If you have an [AgentChat](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/index.html) agent and want to use it in the Core API, you can create a wrapper [`RoutedAgent`](https://microsoft.github.io/autogen/stable/reference/python/autogen_core.base.RoutedAgent.html) that delegates messages to the AgentChat agent.

```python
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient


class MyAssistant(RoutedAgent):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4o")
        self._delegate = AssistantAgent(name, model_client=model_client)

    @message_handler
    async def handle_my_message_type(self, message: MyMessageType, ctx: MessageContext) -> None:
        print(f"{self.id.type} received message: {message.content}")
        response = await self._delegate.on_messages(
            [TextMessage(content=message.content, source="user")], ctx.cancellation_token
        )
        print(f"{self.id.type} responded: {response.chat_message}")
```

## Registering Agent Type

To make agents available to the runtime, developers can use the [`register()`](https://microsoft.github.io/autogen/stable/reference/python/autogen_core.base.Agent.html) class method of the [`BaseAgent`](https://microsoft.github.io/autogen/stable/reference/python/autogen_core.base.Agent.html) class. The process of registration associates an agent type, which is uniquely identified by a string, and a factory function that creates an instance of the agent type of the given class.

```python
from autogen_core import SingleThreadedAgentRuntime

runtime = SingleThreadedAgentRuntime()
await MyAgent.register(runtime, "my_agent", lambda: MyAgent())
await MyAssistant.register(runtime, "my_assistant", lambda: MyAssistant("my_assistant"))
```

Once an agent type is registered, we can send a direct message to an agent instance using an [`AgentId`](https://microsoft.github.io/autogen/stable/reference/python/autogen_core.base.AgentId.html). The runtime will create the instance the first time it delivers a message to this instance.

```python
runtime.start()  # Start processing messages in the background.
await runtime.send_message(MyMessageType("Hello, World!"), AgentId("my_agent", "default"))
await runtime.send_message(MyMessageType("Hello, World!"), AgentId("my_assistant", "default"))
await runtime.stop()  # Stop processing messages in the background.
```

## Running the Single-Threaded Agent Runtime

The above code snippet uses [`start()`](https://microsoft.github.io/autogen/stable/reference/python/autogen_core.runtime.SingleThreadedAgentRuntime.html) to start a background task to process and deliver messages to recipients' message handlers. This is a feature of the local embedded runtime [`SingleThreadedAgentRuntime`](https://microsoft.github.io/autogen/stable/reference/python/autogen_core.runtime.SingleThreadedAgentRuntime.html).

To stop the background task immediately, use the [`stop()`](https://microsoft.github.io/autogen/stable/reference/python/autogen_core.runtime.SingleThreadedAgentRuntime.html) method:

```python
runtime.start()
# ... Send messages, publish messages, etc.
await runtime.stop()  # This will return immediately but will not cancel any in-progress message handling.
```

You can resume the background task by calling [`start()`](https://microsoft.github.io/autogen/stable/reference/python/autogen_core.runtime.SingleThreadedAgentRuntime.html) again.

For batch scenarios such as running benchmarks for evaluating agents, you may want to wait for the background task to stop automatically when there are no unprocessed messages and no agent is handling messages.

[Content truncated due to length - full documentation available at source URL]
