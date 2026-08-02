from __future__ import annotations

from pydantic import BaseModel, Field


class ReActConfig(BaseModel):

    max_context_tokens: int = Field(
        default=8192, description="Maximum context tokens for LLM"
    )
    max_iterations: int = Field(default=50, description="Maximum reasoning iterations")
    max_consecutive_errors: int = Field(
        default=5, description="Maximum consecutive errors before abort"
    )
    max_execution_time: int = Field(
        default=600, description="Maximum execution time in seconds"
    )
