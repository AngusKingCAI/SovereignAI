# Writing Effective Tools for Agents — With Agents

**Source:** https://www.anthropic.com/engineering/writing-tools-for-agents
**Author:** Anthropic Engineering
**Date:** September 11, 2025

---

## Overview

Agents are only as effective as the tools we give them. We share how to write high-quality tools and evaluations, and how you can boost performance by using Claude to optimize its tools for itself.

The Model Context Protocol (MCP) can empower LLM agents with potentially hundreds of tools to solve real-world tasks. But how do we make those tools maximally effective?

In this post, we describe our most effective techniques for improving performance in a variety of agentic AI systems.

We begin by covering how you can:
- Build and test prototypes of your tools
- Create and run comprehensive evaluations of your tools with agents
- Collaborate with agents like Claude Code to automatically increase the performance of your tools

We conclude with key principles for writing high-quality tools we've identified along the way:
- Choosing the right tools to implement (and not to implement)
- Namespacing tools to define clear boundaries in functionality
- Returning meaningful context from tools back to agents
- Optimizing tool responses for token efficiency
- Prompt-engineering tool descriptions and specs

---

## What is a Tool?

In computing, deterministic systems produce the same output every time given identical inputs, while non-deterministic systems—like agents—can generate varied responses even with the same starting conditions.

When we traditionally write software, we're establishing a contract between deterministic systems. For instance, a function call like `getWeather("NYC")` will always fetch the weather in New York City in the exact same manner every time it is called.

Tools are a new kind of software which reflects a contract between deterministic systems and non-deterministic agents. When a user asks "Should I bring an umbrella today?," an agent might call the weather tool, answer from general knowledge, or even ask a clarifying question about location first. Occasionally, an agent might hallucinate or even fail to grasp how to use a tool.

This means fundamentally rethinking our approach when writing software for agents: instead of writing tools and MCP servers the way we'd write functions and APIs for other developers or systems, we need to design them for agents.

Our goal is to increase the surface area over which agents can be effective in solving a wide range of tasks by using tools to pursue a variety of successful strategies. Fortunately, in our experience, the tools that are most "ergonomic" for agents also end up being surprisingly intuitive to grasp as humans.

---

## How to Write Tools

In this section, we describe how you can collaborate with agents both to write and to improve the tools you give them. Start by standing up a quick prototype of your tools and testing them locally. Next, run a comprehensive evaluation to measure subsequent changes. Working alongside agents, you can repeat the process of evaluating and improving your tools until your agents achieve strong performance on real-world tasks.

### Building a Prototype

It can be difficult to anticipate which tools agents will find ergonomic and which tools they won't without getting hands-on yourself. Start by standing up a quick prototype of your tools. If you're using Claude Code to write your tools (potentially in one-shot), it helps to give Claude documentation for any software libraries, APIs, or SDKs (including potentially the MCP SDK) your tools will rely on. LLM-friendly documentation can commonly be found in flat `llms.txt` files on official documentation sites.

Wrapping your tools in a local MCP server or Desktop extension (DXT) will allow you to connect and test your tools in Claude Code or the Claude Desktop app.

To connect your local MCP server to Claude Code, run `claude mcp add <name> <command> [args...]`.

To connect your local MCP server or DXT to the Claude Desktop app, navigate to `Settings > Developer` or `Settings > Extensions`, respectively.

Tools can also be passed directly into Anthropic API calls for programmatic testing.

Test the tools yourself to identify any rough edges. Collect feedback from your users to build an intuition around the use-cases and prompts you expect your tools to enable.

### Running an Evaluation

Next, you need to measure how well Claude uses your tools by running an evaluation. Start by generating lots of evaluation tasks, grounded in real world uses. We recommend collaborating with an agent to help analyze your results and determine how to improve your tools.

#### Generating Evaluation Tasks

With your early prototype, Claude Code can quickly explore your tools and create dozens of prompt and response pairs. Prompts should be inspired by real-world uses and be based on realistic data sources and services (for example, internal knowledge bases and microservices). We recommend you avoid overly simplistic or superficial "sandbox" environments that don't stress-test your tools with sufficient complexity. Strong evaluation tasks might require multiple tool calls—potentially dozens.

**Examples of strong tasks:**
- Schedule a meeting with Jane next week to discuss our latest Acme Corp project. Attach the notes from our last project planning meeting and reserve a conference room.
- Customer ID 9182 reported that they were charged three times for a single purchase attempt. Find all relevant log entries and determine if any other customers were affected by the same issue.
- Customer Sarah Chen just submitted a cancellation request. Prepare a retention offer. Determine: (1) why they're leaving, (2) what retention offer would be most compelling, and (3) any risk factors we should be aware of before making an offer.

**Examples of weaker tasks:**
- Schedule a meeting with jane@acme.corp next week.
- Search the payment logs for `purchase_complete` and `customer_id=9182`.
- Find the cancellation request by Customer ID 45892.

Each evaluation prompt should be paired with a verifiable response or outcome. Your verifier can be as simple as an exact string comparison between ground truth and sampled responses, or as advanced as enlisting Claude to judge the response. Avoid overly strict verifiers that reject correct responses due to spurious differences like formatting, punctuation, or valid alternative phrasings.

For each prompt-response pair, you can optionally also specify the tools you expect an agent to call in solving the task, to measure whether or not agents are successful in grasping each tool's purpose during evaluation. However, because there might be multiple valid paths to solving tasks correctly, try to avoid overspecifying or overfitting to strategies.

#### Running the Evaluation

We recommend running your evaluation programmatically with direct LLM API calls. Use simple agentic loops (`while`-loops wrapping alternating LLM API and tool calls): one loop for each evaluation task. Each evaluation agent should be given a single task prompt and your tools.

In your evaluation agents' system prompts, we recommend instructing agents to output not just structured response blocks (for verification), but also reasoning and feedback blocks. Instructing agents to output these before tool call and response blocks may increase LLMs' effective intelligence by triggering chain-of-thought (CoT) behaviors.

If you're running your evaluation with Claude, you can turn on interleaved thinking for similar functionality "off-the-shelf". This will help you probe why agents do or don't call certain tools and highlight specific areas of improvement in tool descriptions and specs.

As well as top-level accuracy, we recommend collecting other metrics like the total runtime of individual tool calls and tasks, the total number of tool calls, the total token consumption, and tool errors. Tracking tool calls can help reveal common workflows that agents pursue and offer some opportunities for tools to consolidate.

#### Analyzing Results

Agents are your helpful partners in spotting issues and providing feedback on everything from contradictory tool descriptions to inefficient tool implementations and confusing tool schemas. However, keep in mind that what agents omit in their feedback and responses can often be more important than what they include. LLMs don't always say what they mean.

Observe where your agents get stumped or confused. Read through your evaluation agents' reasoning and feedback (or CoT) to identify rough edges. Review the raw transcripts (including tool calls and tool responses) to catch any behavior not explicitly described in the agent's CoT. Read between the lines; remember that your evaluation agents don't necessarily know the correct answers and strategies.

Analyze your tool calling metrics. Lots of redundant tool calls might suggest some right-sizing or consolidation opportunities. Slow tools might need optimization. Frequent tool errors might indicate bugs or unclear tool schemas.

### Collaborating with Agents to Improve Tools

Once you've identified areas for improvement, you can collaborate with agents to iteratively improve your tools. Here's the process:

1. **Share evaluation results** with Claude Code or another agent
2. **Ask for specific improvements** based on the identified issues
3. **Iterate rapidly** - agents can suggest and implement changes quickly
4. **Re-run evaluations** to measure improvement
5. **Repeat until satisfied** with performance

This collaborative approach has shown significant improvements in our internal testing, with Claude-optimized tools often outperforming human-written versions.

---

## Key Principles for Writing High-Quality Tools

### 1. Choosing the Right Tools to Implement (and Not to Implement)

One of the most common failure modes we see is bloated tool sets that cover too much functionality or lead to ambiguous decision points about which tool to use. If a human engineer can't definitively say which tool should be used in a given situation, an AI agent can't be expected to do better.

**Guidelines:**
- Start with a minimal viable set of tools
- Add tools only when there's a clear need
- Consolidate overlapping functionality
- Remove tools that aren't being used effectively

**Example:** Instead of having separate tools for `get_user_by_id`, `get_user_by_email`, and `get_user_by_name`, consider a single `search_users` tool with optional parameters.

### 2. Namespacing Tools to Define Clear Boundaries in Functionality

Namespacing helps agents understand tool boundaries and reduces confusion about which tool to use for a given task.

**Guidelines:**
- Use consistent naming conventions
- Group related tools with prefixes (e.g., `slack_`, `asana_`, `github_`)
- Make tool names descriptive and self-explanatory
- Avoid overly generic names that could apply to multiple domains

**Example:**
- Good: `slack_send_message`, `slack_list_channels`, `slack_get_user_info`
- Less good: `send_message`, `list_channels`, `get_user_info`

### 3. Returning Meaningful Context from Tools Back to Agents

Tools should return information that helps agents understand what happened and why, not just raw data.

**Guidelines:**
- Include success/failure status in responses
- Provide human-readable error messages
- Return context that helps agents understand tool behavior
- Include metadata that might be useful for decision-making

**Example:**
```json
{
  "status": "success",
  "message": "User updated successfully",
  "user_id": "12345",
  "changes": {
    "email": "new@example.com",
    "updated_at": "2025-09-11T10:30:00Z"
  }
}
```

### 4. Optimizing Tool Responses for Token Efficiency

Token efficiency matters for both cost and performance. Tools should return information concisely without losing necessary context.

**Guidelines:**
- Return only the information that's actually needed
- Use structured formats (JSON) for conciseness
- Avoid verbose prose in tool responses
- Consider pagination for large result sets
- Use abbreviations where appropriate (while maintaining clarity)

**Example:**
Instead of returning full user objects with all fields, return only the fields the agent requested or commonly needs.

### 5. Prompt-Engineering Tool Descriptions and Specs

Tool descriptions and specifications are essentially prompts that tell agents how to use the tool. Treat them with the same care you'd give to system prompts.

**Guidelines:**
- Write clear, concise descriptions
- Include examples of when to use the tool
- Specify parameters and their purposes
- Describe edge cases and error conditions
- Use language that LLMs understand well

**Example:**
```
Description: Searches for users in the system by various criteria. Use this when you need to find a specific user or list of users based on search terms.

Parameters:
- query: Search term (name, email, or partial match)
- limit: Maximum number of results (default: 10, max: 100)
- include_deleted: Whether to include deleted users (default: false)

Returns: List of user objects with id, name, email, and status.
```

---

## Key Takeaways

1. **Tools are contracts with agents** - Design them for non-deterministic systems, not just deterministic ones
2. **Prototype and test early** - Get hands-on experience with your tools before finalizing
3. **Evaluate comprehensively** - Use realistic tasks that stress-test your tools
4. **Collaborate with agents** - Use Claude Code and other agents to iteratively improve your tools
5. **Choose tools wisely** - Minimal viable sets beat bloated tool catalogs
6. **Namespace clearly** - Help agents understand tool boundaries
7. **Return meaningful context** - Give agents the information they need to understand tool behavior
8. **Optimize for tokens** - Concise responses improve cost and performance
9. **Engineer descriptions** - Tool specs are prompts—treat them with care

---

*Note: This content was fetched from Anthropic's engineering blog and saved for offline reference. For the most up-to-date version, visit the source URL.*
