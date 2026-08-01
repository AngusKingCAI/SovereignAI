# LangChain Custom Middleware

**Source URL:** https://docs.langchain.com/oss/python/langchain/middleware/custom

---

## Documentation Index
Fetch the complete documentation index at: https://docs.langchain.com/llms.txt
Use this file to discover all available pages before exploring further.

# Custom middleware

Build custom middleware by implementing hooks that run at specific points in the agent execution flow.

## Hooks

Middleware provides two styles of hooks to intercept agent execution:

- **Node-style hooks**: Run sequentially at specific execution points.
- **Wrap-style hooks**: Run around each model or tool call.

### Node-style hooks

Run sequentially at specific execution points. Use for logging, validation, and state updates.

Choose the hooks your middleware needs. You can choose between node-style hooks and wrap-style hooks.

**Node-style hooks** run at specific execution points:

| Hook           | When it runs                                |
| -------------- | ------------------------------------------- |
| `before_agent` | Before agent starts (once per invocation)   |
| `before_model` | Before each model call                      |
| `after_model`  | After each model response                   |
| `after_agent`  | After agent completes (once per invocation) |

**Wrap-style hooks** run around each call, giving you control over execution:

| Hook              | When it runs           |
| ----------------- | ---------------------- |
| `wrap_model_call` | Around each model call |
| `wrap_tool_call`  | Around each tool call  |

**Example - Decorator:**

```python
from langchain.agents.middleware import before_model, after_model, AgentState
from langchain.messages import AIMessage
from langgraph.runtime import Runtime
from typing import Any


@before_model(can_jump_to=["end"])
def check_message_limit(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    if len(state["messages"]) >= 50:
        return {
            "messages": [AIMessage("Conversation limit reached.")],
            "jump_to": "end"
        }
    return None

@after_model
def log_response(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    print(f"Model returned: {state['messages'][-1].content}")
    return None
```

**Example - Class:**

```python
from langchain.agents.middleware import AgentMiddleware, AgentState, hook_config
from langchain.messages import AIMessage
from langgraph.runtime import Runtime
from typing import Any

class MessageLimitMiddleware(AgentMiddleware):
    def __init__(self, max_messages: int = 50):
        super().__init__()
        self.max_messages = max_messages

    @hook_config(can_jump_to=["end"])
    def before_model(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        if len(state["messages"]) >= self.max_messages:
            return {
                "messages": [AIMessage("Conversation limit reached.")],
                "jump_to": "end"
            }
        return None

    def after_model(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        print(f"Model returned: {state['messages'][-1].content}")
        return None
```

### Wrap-style hooks

Intercept execution and control when the handler is called. Use for retries, caching, and transformation.

You decide if the handler is called zero times (short-circuit), once (normal flow), or multiple times (retry logic).

**Available hooks:**

* `wrap_model_call` - Around each model call
* `wrap_tool_call` - Around each tool call

**Example - Decorator:**

```python
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse
from typing import Callable


@wrap_model_call
def retry_model(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse],
) -> ModelResponse:
    for attempt in range(3):
        try:
            return handler(request)
        except Exception as e:
            if attempt == 2:
                raise
            print(f"Retry {attempt + 1}/3 after error: {e}")
```

**Example - Class:**

```python
from langchain.agents.middleware import AgentMiddleware, ModelRequest, ModelResponse
from typing import Callable

class RetryMiddleware(AgentMiddleware):
    def __init__(self, max_retries: int = 3):
        super().__init__()
        self.max_retries = max_retries

    def wrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        for attempt in range(self.max_retries):
            try:
                return handler(request)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise
                print(f"Retry {attempt + 1}/{self.max_retries} after error: {e}")
```

## State updates

Both node-style and wrap-style hooks can update agent state. The mechanism differs:

* **Node-style hooks** (`before_agent`, `before_model`, `after_model`, `after_agent`): Return a dict directly. The dict is applied to the agent state using the graph's reducers.
* **Wrap-style hooks** (`wrap_model_call`, `wrap_tool_call`): For model calls, return [`ExtendedModelResponse`](https://reference.langchain.com/python/langchain/agents/middleware/types/ExtendedModelResponse) with a [`Command`](https://reference.langchain.com/python/langgraph/types/Command) to inject state updates alongside the model response. For tool calls, return a [`Command`](https://reference.langchain.com/python/langgraph/types/Command) directly. Use these when you need to track or update state based on logic that runs during the model or tool call, such as summarization trigger points, usage metadata, or custom fields calculated from the request or response.

### Node-style hooks

Return a dict from a node-style hook to merge updates into agent state. The dict keys map to state fields.

```python
from langchain.agents.middleware import after_model, AgentState
from langgraph.runtime import Runtime
from typing import Any
from typing_extensions import NotRequired


class TrackingState(AgentState):
    model_call_count: NotRequired[int]


@after_model(state_schema=TrackingState)
def increment_after_model(state: TrackingState, runtime: Runtime) -> dict[str, Any] | None:
    return {"model_call_count": state.get("model_call_count", 0) + 1}
```

### Wrap-style hooks

Return a [`ExtendedModelResponse`](https://reference.langchain.com/python/langchain/agents/middleware/types/ExtendedModelResponse) with a [`Command`](https://reference.langchain.com/python/langgraph/types/Command) from `wrap_model_call` to inject state updates from the model call layer:

```python
from typing import Callable
from langchain.agents.middleware import (
    wrap_model_call,
    ModelRequest,
    ModelResponse,
    AgentState,
    ExtendedModelResponse
)
from langgraph.types import Command
from typing_extensions import NotRequired

class UsageTrackingState(AgentState):
    """Agent state with token usage tracking."""

    last_model_call_tokens: NotRequired[int]


@wrap_model_call(state_schema=UsageTrackingState)
def track_usage(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse],
) -> ExtendedModelResponse:
    response = handler(request)
    return ExtendedModelResponse(
        model_response=response,
        command=Command(update={"last_model_call_tokens": 150}),
    )
```

The [`Command`](https://reference.langchain.com/python/langgraph/types/Command) flows through the graph's reducers, so updates are applied correctly and messages are additive rather than replacing existing state.

#### Composition with multiple middleware

When multiple middleware layers return `ExtendedModelResponse`, their commands compose:

* **Commands are applied through reducers:** Each `Command` becomes a separate state update. For messages, this means they are additive.
* **Outer wins on conflicts:** For non-reducer state fields, commands are applied inner-first, then outer. The outermost middleware's value takes precedence on conflicting keys.
* **Retry-safe:** If the outer middleware implements logic that can result in multiple calls to `handler()` again (for example, retry logic), commands from earlier calls are discarded.

[Content truncated due to length - full documentation available at source URL]
