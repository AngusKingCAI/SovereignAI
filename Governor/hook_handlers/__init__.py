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
from .post_tool_use import PostToolUseHandler
from .permission_request import PermissionRequestHandler
from .stop import StopHandler

__all__ = ["SessionStartHandler", "UserPromptSubmitHandler", "PreToolUseHandler", "PostToolUseHandler", "PermissionRequestHandler", "StopHandler"]
