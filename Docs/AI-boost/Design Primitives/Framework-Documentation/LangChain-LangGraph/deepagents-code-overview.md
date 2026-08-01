# Deep Agents Code Overview

**Source URL:** https://langchain-5e9cc07a.mintlify.app/oss/python/deepagents/code/overview

---

## Documentation Index
Fetch the complete documentation index at: https://docs.langchain.com/llms.txt
Use this file to discover all available pages before exploring further.

# Deep Agents Code

> Terminal coding agent built on the Deep Agents SDK

Deep Agents Code (`dcode`) is an open source coding agent built on the [Deep Agents SDK](/oss/python/deepagents/quickstart).
It works with any large language model and supports switching providers or models.
Persistent memory carries context across conversations, customizable skills shape behavior, and approval controls gate code execution.

## Get started

Run the following command to install Deep Agents Code and launch an interactive session:

```bash
curl -LsSf https://langch.in/dcode | bash
dcode
```

See the [Quickstart](/oss/deepagents/code/quickstart) to add provider credentials, run your first task, and learn interactive mode.

## Capabilities

- **Remote sandboxes**: Run agent tools remotely instead of on your local machine.
- **Goals and rubrics**: Define measurable objectives or grading criteria so the agent can check whether work is done.
- **Subagents**: Delegate work to task-specific subagents for parallel execution.
- **Memory**: Store and retrieve information across sessions, including project conventions and learned patterns.
- **Context compaction**: Summarize older messages and offload originals to storage.
- **Human-in-the-loop**: Require human approval for sensitive tool operations.
- **Skills**: Extend agent capabilities with custom expertise and instructions.
- **MCP tools**: Load external tools from Model Context Protocol servers.
- **Tracing**: Trace agent operations in LangSmith for observability and debugging.

## Next steps

- **Quickstart**: Install Deep Agents Code, run your first task, and use interactive or non-interactive modes.
- **Configuration**: Set up credentials, `config.toml`, environment variables, hooks, and CLI flags.
