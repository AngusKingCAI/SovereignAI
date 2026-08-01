# ReAct Agent

**Source:** https://outcomeschool.com/blog/react-agent

**Description:** This comprehensive blog post explains the ReAct Agent pattern in detail, covering what it is, how it differs from general AI agents, its anatomy, prompt templates, implementation, and common failure modes with solutions.

---

# ReAct Agent

**Authors**: Amit Shekhar
**Published on**: April 30, 2026

In this blog, we will learn about the ReAct Agent - what it is, how it is built, its anatomy, how it
thinks and acts, and how to handle its common failure modes.

When we hear **ReAct Agent**, it sounds complex. But do not worry. If we break it down into its
individual parts, every single piece is simple.

We will cover the following:
* What is a ReAct Agent
* ReAct Agent vs AI Agent
* Anatomy of a ReAct Agent
* The ReAct Prompt Template
* How a ReAct Agent Thinks and Acts
* A Full Trace Example
* Implementing a ReAct Agent
* Common Failure Modes and How to Fix Them
* Quick Summary

## What is a ReAct Agent

A **ReAct Agent** is an **AI Agent** built using the **ReAct (Reasoning + Acting)** pattern -
the most common pattern for building AI Agents. It is not a single LLM call. It is a loop around an
LLM, where the LLM is given a list of tools it can recommend. At each step, the LLM reasons
about what to do and recommends a tool. The loop runs the tool, appends the result back to the
memory, and the LLM reasons over it on the next turn.

Let's decompose the term:

**ReAct Agent = Reasoning + Acting + Agent**

**Reasoning** is the thinking part - the LLM figures out what to do next. **Acting** is the doing
part - the LLM picks a tool, and the loop calls it. **Agent** is the wrapper around the LLM that
runs this loop, executes the tools, and feeds the results back.

In simple words:

**ReAct Agent = LLM + Tools + A loop that lets the LLM think, act, and observe until the task is
done.**

Think of a ReAct Agent like a new intern on their first day. They do not solve every problem in
their head. They think about what they need, open a tool, read the result, think again, and repeat.
A ReAct Agent works the exact same way - but at the speed of a machine.

A plain LLM call gives us one response and stops. A ReAct Agent gives us a response, runs tools,
reads results, and keeps going - until it has a final answer. So, here comes the ReAct Agent to the
rescue whenever a task is too big to solve in a single LLM call.

## ReAct Agent vs AI Agent

Now, a natural question arises - if a ReAct Agent is an LLM in a loop with tools, isn't that just an
AI Agent? Let's clear this up.

**ReAct is a pattern to build AI Agents. It is not a different category.**

**AI Agent** is the category - any system where an LLM is wrapped in a loop with tools and
memory. It does not say *how* the loop is structured, *how* the LLM picks the next action, or
*whether* the reasoning is visible.

**ReAct** is a pattern for building that loop, where the LLM follows a **Thought - Action -
Observation** cycle. At every step, the LLM first writes its reasoning (the Thought), then picks a
tool (the Action), then reads the result (the Observation), then thinks again. The reasoning is
explicit, step by step, and visible at every turn. That explicit step-by-step reasoning is
Chain-of-Thought (CoT) Prompting surfaced inside the agent loop.

So when we say "ReAct Agent," we mean an AI Agent built with the ReAct pattern. Other patterns like
Plan-and-Execute, Reflection, and Agentic RAG also build AI Agents - they just
shape the loop differently.

In simple words:

**ReAct is a way to build an AI Agent. Not all AI Agents are built this way, but most are.**

Let me tabulate the differences between an AI Agent and a ReAct Agent for your better understanding.

| Property      | AI Agent (the category)            | ReAct Agent (built with the ReAct pattern)       |
|---------------|-----------------------------------|---------------------------------------------------|
| Definition    | Any LLM in a loop with tools       | LLM that loops through Thought, Action, Observation |
| Reasoning     | May or may not be visible          | Surfaced as an explicit Thought step (in the classic form) |
| Loop pattern  | Not specified                      | Thought -> Action -> Observation -> repeat        |
| Examples      | ReAct, Plan-and-Execute, Reflection, Agentic RAG | Just the ReAct pattern |
| When to use the term | When speaking generally about agents | When you mean the Thought - Action - Observation loop specifically |

## Anatomy of a ReAct Agent

A ReAct Agent has five parts. Let's decode each one.

```
+------------------------------------------------+
|                Loop Controller                 |
|                                                |
|   System Prompt --->  +-------+                |
|                       |       |                |
|   Memory        --->  |  LLM  | <-----+        |
|                       +-------+       |        |
|                           |           |        |
|                           | pick      | obs    |
|                           v           |        |
|                       +-------+       |        |
|                       | Tools | ------+        |
|                       +-------+                |
+------------------------------------------------+
```

**1. The LLM.** This is the brain. It does the reasoning. It reads the conversation history and
decides the next step - either pick a tool for the loop to call, or produce the final answer.

**2. The System Prompt.** This tells the LLM how to behave. It explains the ReAct pattern, lists the
available tools, and sets the rules. Without a good system prompt, the LLM may not think, act, or
stop reliably.

**3. The Tools.** These are the actions the agent can take - search the web, query a database, run a
calculator, send an email, read a file, and etc. Each tool has a name, a description, and an input
schema.

**4. The Memory.** This is the running history of the conversation - the user's question,
every thought, every action, every observation. The LLM reads this memory at every step to decide
what to do next.

**5. The Loop Controller.** This is the code that runs the loop. It sends the memory to the LLM,
executes any tool calls, appends the results back to the memory, and checks if the agent is
done. It also handles the stop conditions - like a maximum number of steps.

All five parts work together. Remove any one of them, and it is no longer a ReAct Agent.

## The ReAct Prompt Template

A good system prompt is what makes a plain LLM behave reliably as a ReAct Agent. Without one, the
LLM may answer too early, skip the reasoning, or use the tools poorly. With one, the LLM knows to
think, act, observe, and loop.

Here is a simple ReAct prompt template:

```
You are a helpful assistant that solves problems by thinking step by step and recommending tools when needed.

You have access to the following tools:
- search(query): Search the web for information.
- calculator(expression): Evaluate a math expression.

At each step, respond in one of these two formats:

Format 1 - When you need to recommend a tool:
Thought: <your reasoning about what to do next>
Action: <tool_name>(<tool_input>)

Format 2 - When you have the final answer:
Thought: <your final reasoning>
Final Answer: <the answer to the user's question>

Rules:
- Always start with a Thought.
- Recommend one tool per turn, unless multiple independent tools would clearly help in parallel.
- Wait for the Observation before continuing.
- Stop as soon as you have the final answer.
```

Here, we can see that the prompt does three things:
* Explains the ReAct pattern (Thought, Action, Observation, Final Answer).
* Lists the available tools with their inputs.
* Sets rules to keep the agent from going off the rails.

## How a ReAct Agent Thinks and Acts

Now, let's put all the parts together to see how a ReAct Agent runs end to end.

Here is the shape of the loop:

```
        +-----------------+
        |  User Question  |
        +-----------------+
                 |
                 v
        +-----------------+
        |    Thought      |  <-- LLM reasons about the next step
        +-----------------+
                 |
        +--------+--------+
        |                 |
        v                 v
  +-----------+    +---------------+
  |  Action   |    | Final Answer  | ---> back to user
  +-----------+    +---------------+
        |
        v
  +-----------+
  |   Tool    |
  +-----------+
        |
        v
  +-------------+
  | Observation | --+
  +-------------+   |
                    |
                    +---> back to Thought (loop continues)
```

The user's question goes in at the top. The LLM produces a Thought, and from that Thought it picks
one of two paths - either an Action that the loop turns into a tool call, or a Final Answer that
ends the loop. When the LLM picks an Action, the loop runs the tool, the result comes back as an
Observation, and the Observation feeds into the next Thought. This Thought - Action - Observation
cycle keeps going until the LLM produces the Final Answer.

Here are the steps the agent follows:

**Step 1:** The user sends a question. The Loop Controller adds it to the Memory.

**Step 2:** The Loop Controller sends the Memory (system prompt + user question + history) to the
LLM.

**Step 3:** The LLM responds with either a Thought + Action, or a Final Answer.

**Step 4:** If the response is a Final Answer, the Loop Controller returns it to the user. The agent
is done.

**Step 5:** If the response is a Thought + Action, the Loop Controller executes the tool and gets
the result. This result is the Observation.

**Step 6:** The Loop Controller appends the Thought, Action, and Observation to the Memory.

**Step 7:** Go back to Step 2.

This loop continues until the LLM produces a Final Answer or the maximum step limit is reached.

## A Full Trace Example

Let's trace through a real example to see every part in action.

**User:** "What is 15% of the population of Tokyo?"

```
Thought 1: I need to find the population of Tokyo first. I do not know the exact current number, so I will search for it.
Action 1: search("current population of Tokyo")
Observation 1: The population of Tokyo is approximately 14 million.

Thought 2: Now I need to calculate 15% of 14 million. Let me use the calculator to be accurate.
Action 2: calculator("14000000 * 0.15")
Observation 2: 2100000

Thought 3: I now have the answer. 15% of the population of Tokyo (14 million) is 2.1 million.
Final Answer: 15% of the population of Tokyo is approximately 2.1 million people.
```

Here, we can see how the agent:
* Recognized that it did not have the population data and reached for a tool.
* Chained the output of the search into the input of the calculator.
* Stopped as soon as it had the final answer.

## Implementing a ReAct Agent

Now, here is the important realization:

**If we write code that takes the user's question, sends it to an LLM, runs the tools the LLM picks,
feeds the observations back, and repeats this loop until the LLM has a final answer - our piece of
code is a ReAct Agent.**

That is all a ReAct Agent is. No magic. No black box. Just a loop, an LLM, some tools, and memory -
all wired together in code.

Let's see what this looks like in real Python code:

```python
REACT_SYSTEM_PROMPT = "..."  # the ReAct prompt template from the previous section

async def run_react_agent(user_question, tools, max_steps=10):
    messages = [
        {"role": "system", "content": REACT_SYSTEM_PROMPT},
        {"role": "user", "content": user_question},
    ]
    step = 0

    while True:
        # Safety stop: bail out if we hit the step limit
        if step >= max_steps:
            return "Reached step limit without a final answer."
        step += 1

        # Ask the LLM to think, then either act or give the final answer
        response = await call_llm(messages, tools)

        # If the LLM has the final answer, stop the loop and return it
        if response.is_done:
            return response.final_answer

        # Otherwise, run each tool the LLM picked and feed the observation back
        for tool_call in response.tool_calls:
            observation = await call_tool(tool_call.name, tool_call.arguments)
            messages.append({
                "role": "tool",
                "name": tool_call.name,
                "content": str(observation),
            })
```

Here, we have the entire ReAct Agent in about 20 lines of Python.

## Common Failure Modes and How to Fix Them

ReAct Agents are powerful, but they can fail in specific ways. Let's decode each one.

**1. Infinite loops.** The agent keeps calling the same tool with the same input and never produces
a final answer.

**How to fix:** Set a hard `max_steps` limit. Also, detect repeated identical actions and either
stop or inject a message telling the agent to try a different approach.

**2. Wrong tool selection.** The agent calls the wrong tool for the job - like using search for a
math problem.

**How to fix:** Write very clear tool descriptions. The description is what the LLM uses to pick the
tool, so every word matters. Say exactly what the tool does and when to use it.

**3. Hallucinated tool calls.** The agent calls a tool that does not exist or passes invalid
arguments.

**How to fix:** Use an LLM with native tool-use support (like Claude, GPT, or Gemini) so the schema
is enforced. Always validate tool inputs before executing, and return a clear error message as the
Observation if they are invalid.

**4. Context explosion.** After many steps, the conversation history becomes too long for the LLM's
context window.

**How to fix:** Summarize older steps, drop stale observations, or use a separate memory store. For
long-running agents, we must actively manage the context - this is the discipline of Context
Engineering.

**5. Premature stopping.** The agent gives a final answer before gathering enough information.

**How to fix:** Add a critic step that reviews the final answer before it is returned, or require
the agent to check its answer against a checklist (Did I cover all the parts of the question? Did I
cite a source? Did I verify the math?) before emitting the Final Answer. The system prompt should
make this verification step explicit, not optional.

**6. Getting stuck after a tool error.** A tool fails, and the agent does not know how to recover.

**How to fix:** Catch tool errors, convert them into natural-language Observations (e.g., "Error:
the search API timed out. Try again or use a different query."), and let the LLM reason its way out.

## Quick Summary

Let's recap what we have learned:
* **A ReAct Agent** is an AI Agent that loops through Thought, Action, and Observation until the
  task is done. It is an LLM wrapped in a loop with tools and memory.
* **The anatomy** has five parts: the LLM, the System Prompt, the Tools, the Memory, and the Loop
  Controller. Remove any one, and it is no longer a ReAct Agent.
* **The system prompt** is what makes a plain LLM behave reliably as a ReAct Agent. It explains the
  pattern, lists the tools, and sets the rules.
* **The loop** is simple: send memory to LLM -> if tool call, execute and append observation -> if
  final answer, return.
* **Common failure modes** include infinite loops, wrong tool selection, hallucinated tool calls,
  context explosion, premature stopping, and errors after tool failures. Handling these is the real
  work of building a production agent.
* ReAct or a ReAct-style loop is the most common pattern under the hood of modern AI agents - from
  coding assistants to customer support bots to research assistants.
