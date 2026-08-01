# CrewAI Tasks

**Source URL:** https://docs.crewai.com/en/concepts/tasks

---

## Documentation Index
Fetch the complete documentation index at: https://docs.crewai.com/llms.txt
Use this file to discover all available pages before exploring further.

# Tasks

> Detailed guide on managing and creating tasks within the CrewAI framework.

## Overview

In the CrewAI framework, a `Task` is a specific assignment completed by an `Agent`.

Tasks provide all necessary details for execution, such as a description, the agent responsible, required tools, and more, facilitating a wide range of action complexities.

Tasks within CrewAI can be collaborative, requiring multiple agents to work together. This is managed through the task properties and orchestrated by the Crew's process, enhancing teamwork and efficiency.

### Task Execution Flow

Tasks can be executed in two ways:

* **Sequential**: Tasks are executed in the order they are defined
* **Hierarchical**: Tasks are assigned to agents based on their roles and expertise

The execution flow is defined when creating the crew:

```python
crew = Crew(
    agents=[agent1, agent2],
    tasks=[task1, task2],
    process=Process.sequential  # or Process.hierarchical
)
```

## Task Attributes

| Attribute                              | Parameters              | Type                        | Description                                                                                                     |
| :------------------------------------- | :---------------------- | :-------------------------- | :-------------------------------------------------------------------------------------------------------------- |
| **Description**                        | `description`           | `str`                       | A clear, concise statement of what the task entails.                                                            |
| **Expected Output**                    | `expected_output`       | `str`                       | A detailed description of what the task's completion looks like.                                                |
| **Name** *(optional)*                  | `name`                  | `Optional[str]`             | A name identifier for the task.                                                                                 |
| **Agent** *(optional)*                 | `agent`                 | `Optional[BaseAgent]`       | The agent responsible for executing the task.                                                                   |
| **Tools** *(optional)*                 | `tools`                 | `List[BaseTool]`            | The tools/resources the agent is limited to use for this task.                                                  |
| **Context** *(optional)*               | `context`               | `Optional[List["Task"]]`    | Other tasks whose outputs will be used as context for this task.                                                |
| **Async Execution** *(optional)*       | `async_execution`       | `Optional[bool]`            | Whether the task should be executed asynchronously. Defaults to False.                                          |
| **Human Input** *(optional)*           | `human_input`           | `Optional[bool]`            | Whether the task should have a human review the final answer of the agent. Defaults to False.                   |
| **Markdown** *(optional)*              | `markdown`              | `Optional[bool]`            | Whether the task should instruct the agent to return the final answer formatted in Markdown. Defaults to False. |
| **Config** *(optional)*                | `config`                | `Optional[Dict[str, Any]]`  | Task-specific configuration parameters.                                                                         |
| **Output File** *(optional)*           | `output_file`           | `Optional[str]`             | File path for storing the task output.                                                                          |
| **Create Directory** *(optional)*      | `create_directory`      | `Optional[bool]`            | Whether to create the directory for output_file if it doesn't exist. Defaults to True.                         |
| **Output JSON** *(optional)*           | `output_json`           | `Optional[Type[BaseModel]]` | A Pydantic model to structure the JSON output.                                                                  |
| **Output Pydantic** *(optional)*       | `output_pydantic`       | `Optional[Type[BaseModel]]` | A Pydantic model for task output.                                                                               |
| **Callback** *(optional)*              | `callback`              | `Optional[Any]`             | Function/object to be executed after task completion.                                                           |
| **Guardrail** *(optional)*             | `guardrail`             | `Optional[Callable]`        | Function to validate task output before proceeding to next task.                                                |
| **Guardrails** *(optional)*            | `guardrails`            | `Optional[List[Callable]]`  | List of guardrails to validate task output before proceeding to next task.                                      |
| **Guardrail Max Retries** *(optional)* | `guardrail_max_retries` | `Optional[int]`             | Maximum number of retries when guardrail validation fails. Defaults to 3.                                       |

**Deprecated: max_retries**
The task attribute `max_retries` is deprecated and will be removed in v1.0.0.
Use `guardrail_max_retries` instead to control retry attempts when a guardrail fails.

## Creating Tasks

There are two common ways to create tasks in CrewAI: using **JSONC project configuration (recommended for new crews)** or defining them **directly in code**.

### JSONC Configuration (Recommended)

New projects created with `crewai create crew <name>` define tasks in `crew.jsonc`. The `agents` array points to files in `agents/`, and the `tasks` array defines the ordered work the crew should run.

After creating your CrewAI project as outlined in the [Installation](/en/installation) section, edit the generated `crew.jsonc`.

Use `{placeholder}` values in task `description`, `expected_output`, and `output_file`. Put defaults in the top-level `inputs` object; `crewai run` prompts for any missing values.

Here's an example `crew.jsonc` with two ordered tasks:

```jsonc
{
  "name": "Research Crew",
  "agents": ["researcher", "reporting_analyst"],
  "tasks": [
    {
      "name": "research_task",
      "description": "Conduct thorough research about {topic}. Include current and relevant information.",
      "expected_output": "A list of the most relevant information about {topic}.",
      "agent": "researcher"
    },
    {
      "name": "reporting_task",
      "description": "Review the research and expand it into a detailed report.",
      "expected_output": "A polished markdown report without fenced code blocks.",
      "agent": "reporting_analyst",
      "context": ["research_task"],
      "markdown": true,
      "output_file": "report.md"
    }
  ],
  "inputs": {
    "topic": "AI Agents"
  }
}
```

Each task must include `description` and `expected_output`. The `agent` value should match an agent name listed in `agents`. `context` is a list of prior task names; forward references are rejected so sequential context stays explicit.

Task entries support any public `Task` field. Common fields include `name`, `agent`, `context`, `output_file`, `tools`, `human_input`, `async_execution`, `guardrail`, `guardrails`, `guardrail_max_retries`, `markdown`, `input_files`, `output_json`, `output_pydantic`, `response_model`, and `converter_cls`. Use `"type": "ConditionalTask"` with a `condition` field for conditional tasks.

### Classic YAML Configuration

Classic projects created with `crewai create crew <name> --classic` use `config/tasks.yaml` and a `@CrewBase` class in `crew.py`. This remains supported for existing YAML projects or teams that prefer decorator-based Python wiring.

### Direct Code Definition (Alternative)

Alternatively, you can define tasks directly in your code without using YAML configuration:

```python
from crewai import Task

research_task = Task(
    description="""
        Conduct a thorough research about AI Agents.
        Make sure you find any interesting and relevant information given
        the current year is 2025.
    """,
    expected_output="""
        A list with 10 bullet points of the most relevant information about AI Agents
    """,
    agent=researcher
)

reporting_task = Task(
    description="""
        Review the context you got and expand each topic into a full section for a report.
        Make sure the report is detailed and contains any and all relevant information.
    """,
    expected_output="""
        A fully fledge reports with the mains topics, each with a full section of information.
    """,
    agent=reporting_analyst,
    markdown=True,  # Enable markdown formatting for the final output
    output_file="report.md"
)
```

[Content truncated due to length - full documentation available at source URL]
