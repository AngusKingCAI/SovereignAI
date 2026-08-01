# ReAct Design Pattern

**Source:** https://guidance.readthedocs.io/en/stable/example_notebooks/art_of_prompt_design/react.html

**Description:** This technical documentation shows how to implement the ReAct pattern using the Guidance library. It demonstrates two approaches: using the tools API of the gen function and using stateful control for fine-grained execution control.

---

# ReAct Design Pattern

Authors: @Sam1320, @slundberg

The ReAct prompting strategy (by Yao et al.) consists of prompting a language model to generate explicit reasoning traces that contain an "action" step. The action step selects actions to execute in order to gain more information. ReAct can be viewed as a specific form of chain of thought combined with tool use. To execute the ReAct pattern we just need to follow the standard tool use paradigm of executing the selected actions and injecting the result (aka. Observation) back into the prompt and repeating the process until a final answer is found.

This notebook shows two different ways to leverage `guidance` to implement this pattern:

1. Using the `tools` API of the `gen` function.
2. Using a ReAct-specific stateful guidance function.

## Setup

First let's import the necessary modules and load the LLM:

```python
import math
from huggingface_hub import hf_hub_download
import guidance
from guidance import models, gen, select

repo_id = "TheBloke/Mistral-7B-Instruct-v0.2-GGUF"
filename = "mistral-7b-instruct-v0.2.Q8_0.gguf"
model_kwargs = {"verbose": True, "n_gpu_layers": -1, "n_ctx": 4096}

downloaded_file = hf_hub_download(repo_id=repo_id, filename=filename)
mistral7 = guidance.models.LlamaCpp(downloaded_file, **model_kwargs)
```

We can use the same prompt for both approaches so let's define it here. We will use two simple functions `sqrt` and `age` (returns age of a famous person) as tools to demonstrate the pattern.

```python
prompt = """Answer the following questions as best you can. You have access only to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought 1: you should always think about what to do
Action 1: the action to take, has to be one of {tool_names}
Observation 1: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought N: I now know the final answer.
Final Answer: the final answer to the original input question.
Done.

Example:
Question: What is the square root of the age of Brad Pitt?
Thought 1: I should find out how old Brad Pitt is.
Action 1: age(Brad Pitt)
Observation 1: 56
Thought 2: I should find the square root of 56.
Action 2: sqrt(56)
Observation 2: 7.48
Thought 3: I now know the final answer.
Final Answer: 7.48
Done.

Question: {query}
"""
```

## Implementing ReAct using the `tools` API of the `gen` function

We can define tools that can be used and then pass them as arguments to `gen`. Guidance will identify when the model generates something that matches the grammar of a tool call, execute it and then resume generation.

Let's first define our set of functions that can be used as tools. The output of these functions is inserted back into the program right after the call to the function. For this reason, in order to match the pattern of the prompt above, we'll add "Observation N" before the output of the function.

```python
from guidance import regex

ages_db = {
    "Leonardo DiCaprio": 49,
    "Brad Pitt": 59
}

@guidance
def sqrt(lm, number):
    lm += f'\nObservation {regex(r"[0-9]+")}: ' + f'{math.sqrt(float(number))}\n'
    return lm

@guidance
def log(lm, number):
    lm += f'\nObservation {regex(r"[0-9]+")}: {math.log(float(number)):.4f}\n'
    return lm

@guidance
def age(lm, person):
    lm += f'\nObservation {regex(r"[0-9]+")}: {ages_db.get(person)}\n'
    return lm

tools = {
    "sqrt": "Computes the square root of a number.",
    "age": "Returns the age of a person.",
    "log": "Computes the logarithm of a number."
}
tool_map = {
    "sqrt": sqrt,
    "age": age,
    "log": log
}
```

### Run the Program

Now we can start generation just by adding the model and the prompt to `gen` and passing the tools as arguments.

```python
query = "What is the logarithm of Leonardo DiCaprio's age?"
prompt_with_query = prompt.format(tools=tools, tool_names=list(tools.keys()), query=query)
lm = mistral7 + prompt_with_query + gen(max_tokens=200, tools=[sqrt, age, log], stop="Done.")
```

## Implementing ReAct Directly Using Stateful Control

Instead of passing the tools as arguments to `gen` we can use stateful control to guide the execution of the program. This allows for more fine grained control.

In this case we'll define a function that runs the ReAct loop. Note that now `select` constrains the model to select one of the available tools. Also, we don't need to add prefixes to the tools since all the context is finely controlled inside the loop.

```python
tool_map = {
    "sqrt": lambda x: str(math.sqrt(float(x))),
    "age": lambda x: str(ages_db.get(x)),
    "log": lambda x: str(math.log(float(x)))
}

@guidance
def react_prompt_example(lm, question, tools, max_rounds=10):
    tool_names = list(tools.keys())
    lm += prompt.format(tools=tools, tool_names=tool_names, query=question)
    i = 1
    while True:
        lm += f'Thought {i}: ' + gen(name='thought', suffix='\n')
        if 'final answer' in lm['thought'] or i == max_rounds:
            lm += 'Final Answer: ' + gen(name='answer', suffix='\n')
            break
        lm += f'Act {i}: ' + select(tool_names, name='act')
        lm += '(' + gen(name='arg', suffix=')') + '\n'
        if lm['act'] in tool_map:
            lm += f'Observation {i}: ' + tool_map[lm['act']](lm['arg']) + '\n'
        i += 1
    return lm

lm = mistral7
lm += react_prompt_example("What is the logarithm of Leonardo DiCaprio's age?", tools)
```

### We can access the final answer which we stored in the program state.

```python
print(query)
print(f"Response: {lm['answer']}")
```

This documentation demonstrates practical implementation of the ReAct pattern using the Guidance library, showing both a simpler tools API approach and a more flexible stateful control approach for different use cases.
