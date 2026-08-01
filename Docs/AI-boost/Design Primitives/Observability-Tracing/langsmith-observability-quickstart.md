# LangSmith Tracing Quickstart

**Source:** https://docs.langchain.com/langsmith/observability-quickstart

## Overview
Add LangSmith tracing to an LLM application in minutes. LangSmith gives you end-to-end visibility into your LLM application by capturing traces; a complete record of every step that ran during a request, from the inputs passed in to the final output returned.

## Prerequisites
- A LangSmith account: Sign up or log in at smith.langchain.com
- A LangSmith API key: Follow the Create an API key guide
- An OpenAI API key: Generate this from the OpenAI dashboard

## 1. Set up your environment

### Python Setup
```bash
mkdir ls-quickstart && cd ls-quickstart
python -m venv .venv && source .venv/bin/activate
pip install -U langsmith openai
```

### Environment Variables
```bash
export LANGSMITH_TRACING=true
export LANGSMITH_API_KEY="<your-langsmith-api-key>"
export OPENAI_API_KEY="<your-openai-api-key>"
```

To send traces to a specific project, use the `LANGSMITH_PROJECT` environment variable. If this is not set, LangSmith will create a default tracing project automatically on trace ingestion.

### Regional Configuration
If your account is in a region other than US (the default), also set `LANGSMITH_ENDPOINT` to the API URL for your region:
- GCP US: `api.smith.langchain.com`
- GCP EU: `eu.api.smith.langchain.com`
- GCP APAC: `apac.api.smith.langchain.com`
- AWS US: `aws.api.smith.langchain.com`

## 2. Build the app

The app uses two LangSmith tools:
- **OpenAI wrapper**: wraps the OpenAI client so every LLM call is automatically logged as a nested span
- **Traceable wrapper**: wraps a function so its inputs, outputs, and any nested spans appear as a single trace in LangSmith

### Python Example
```python
from openai import OpenAI
from langsmith.wrappers import wrap_openai
from langsmith import traceable

client = wrap_openai(OpenAI())  # log every OpenAI call automatically

@traceable(run_type="tool")  # trace this as a tool span
def get_context(question: str) -> str:
    # In a real app, this would query a knowledge base or vector store
    return "LangSmith traces are stored for 14 days on the Developer plan."

@traceable  # capture the full pipeline as a single trace
def assistant(question: str) -> str:
    context = get_context(question)
    response = client.chat.completions.create(
        model="gpt-5.4-mini",
        messages=[
            {
                "role": "system",
                "content": f"Answer using the context below.\n\nContext: {context}",
            },
            {"role": "user", "content": question},
        ],
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    print(assistant("How long are LangSmith traces stored?"))
```

## 3. View traces
Run the application and then view the traces in the LangSmith UI at smith.langchain.com.

## Additional Notes
- If you're building with LangChain or LangGraph, you can enable LangSmith tracing with a single environment variable
- For Anthropic, use the Anthropic wrapper
- For Google Gemini, use the Gemini wrapper
- For other providers, use the `@traceable` decorator to trace calls manually
