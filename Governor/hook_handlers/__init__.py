"""
Hook handlers for Devin CLI lifecycle events.

Auto-discovered registry for all 8 hooks:
- SessionStart
- UserPromptSubmit
- PreToolUse
- PostToolUse
- PermissionRequest
- Stop
- SessionEnd
- PostCompaction
"""

from .session_start import SessionStartHandler
from .user_prompt_submit import UserPromptSubmitHandler
from .pre_tool_use import PreToolUseHandler

__all__ = ["SessionStartHandler", "UserPromptSubmitHandler", "PreToolUseHandler"]
