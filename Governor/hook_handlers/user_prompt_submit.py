"""
UserPromptSubmit Hook Handler for Governor.py v1.5

This handler processes the UserPromptSubmit hook event, which is triggered
when the user submits a prompt to the agent. It detects user intent,
parses bypass commands, and enriches the prompt with research context.

Key Responsibilities:
- Intent detection (question vs task keywords)
- Research worksheet enrichment
- Bypass command parsing (/bypass <rule_id>:<tool>)
- Mode detection (App vs Harness review)
- Flag setting (research_required)
- Protocol-compliant response

This implements the UserPromptSubmit handler specified in v1.5 spec §4.3.
"""

import re
from typing import Dict, Any, Optional, Tuple

# Import base class (package-relative)
try:
    from ._base import HookHandler
except ImportError:
    from hook_handlers._base import HookHandler


class UserPromptSubmitHandler(HookHandler):
    """
    Handler for UserPromptSubmit hook events.
    
    UserPromptSubmit is triggered when the user submits a prompt to the agent.
    This handler detects user intent, parses bypass commands, and enriches
    the prompt with research context.
    """
    
    @property
    def hook_name(self) -> str:
        """Return the hook name this handler processes."""
        return "UserPromptSubmit"
    
    @property
    def can_block(self) -> bool:
        """
        Indicate if this handler can block operations.
        
        UserPromptSubmit cannot block - it's always an allow operation.
        """
        return False
    
    def execute(self, payload: Dict[str, Any], state_machine: Any, 
               engine: Any) -> Dict[str, Any]:
        """
        Execute the UserPromptSubmit handler logic.
        
        This method:
        1. Detects user intent (question vs task)
        2. Parses bypass commands from the prompt
        3. Detects mode (App vs Harness review)
        4. Sets research_required flag if needed
        5. Enriches prompt with research worksheet
        6. Returns a protocol-compliant allow response
        
        Args:
            payload: UserPromptSubmit hook event payload
            state_machine: Governor state machine instance
            engine: Rule engine instance (not used in UserPromptSubmit)
            
        Returns:
            Protocol-compliant allow response with enriched context
        """
        # Extract user prompt from payload
        user_prompt = payload.get("user_prompt", "")
        
        # Detect intent (question vs task)
        intent = self._detect_intent(user_prompt)
        
        # Parse bypass commands
        bypass_commands = self._parse_bypass_commands(user_prompt)
        
        # Process bypass commands
        additional_context = ""
        for bypass_key in bypass_commands:
            # Parse bypass key to extract rule_id and tool_name
            # Format: "bypass:rule_id:tool:uuid" or just "rule_id" or "all"
            if bypass_key == "all":
                # Special case: bypass all for next tool call only
                state_machine.add_bypass(
                    rule_id="*",
                    tool_name="*",
                    scope="once",
                    reason="User requested bypass all via command",
                    source="user_command",
                    user_prompt_text=user_prompt[:200]
                )
                additional_context += "\n✓ Bypass registered: next tool call only"
            else:
                # Parse rule_id:tool format or just rule_id
                parts = bypass_key.split(":")
                if len(parts) >= 2:
                    rule_id = parts[0]
                    tool_name = parts[1]
                else:
                    rule_id = bypass_key
                    tool_name = "*"
                
                state_machine.add_bypass(
                    rule_id=rule_id,
                    tool_name=tool_name,
                    scope="session",
                    reason="User requested bypass via command",
                    source="user_command",
                    user_prompt_text=user_prompt[:200]
                )
                additional_context += f"\n✓ Bypass registered: {bypass_key}"
        
        # Detect mode (App vs Harness review)
        mode = self._detect_mode(user_prompt, payload)
        
        # Set mode in state machine for persistence
        state_machine.set_mode(mode)
        
        # Set research_required flag if intent is question
        if intent == "question":
            state_machine.set_flag("research_required", True)
            additional_context += "\n⚠️ Research phase recommended for this query."
        
        # Enrich with research worksheet if needed
        if intent == "question" or mode == "harness":
            research_context = self._build_research_worksheet(user_prompt, mode)
            additional_context += research_context
        
        # Build response
        return self._build_allow_response(
            reason=f"User prompt processed. Intent: {intent}, Mode: {mode}",
            additional_context=additional_context
        )
    
    def _detect_intent(self, user_prompt: str) -> str:
        """
        Detect user intent from the prompt.
        
        Intent detection logic:
        - Question: Prompt ends with "?" or contains question words
        - Task: Prompt contains action verbs (implement, create, fix, etc.)
        
        Args:
            user_prompt: User's prompt text
            
        Returns:
            Intent string ("question" or "task")
        """
        # Check for question markers
        question_words = ["what", "how", "why", "when", "where", "who", "which", "can", "could", "would", "should"]
        question_pattern = r"\?$"
        
        if re.search(question_pattern, user_prompt.strip()):
            return "question"
        
        # Check for question words at start
        first_word = user_prompt.strip().split()[0].lower() if user_prompt.strip() else ""
        if first_word in question_words:
            return "question"
        
        # Default to task
        return "task"
    
    def _parse_bypass_commands(self, user_prompt: str) -> list:
        """
        Parse bypass commands from the user prompt.
        
        Bypass command format: /bypass <rule_id>:<tool>
        Example: /bypass block_destructive:exec
        
        Args:
            user_prompt: User's prompt text
            
        Returns:
            List of bypass keys
        """
        bypass_pattern = r"/bypass\s+(\S+)"
        matches = re.findall(bypass_pattern, user_prompt)
        return matches
    
    def _detect_mode(self, user_prompt: str, payload: Dict[str, Any]) -> str:
        """
        Detect execution mode (App vs Harness review).
        
        Mode detection logic (ENHANCED per spec §4.3):
        - Primary: Command prefix (mode:harness or mode:app)
        - Fallback: Explicit review keywords (with deprecation warning)
        
        Args:
            user_prompt: User's prompt text
            payload: Hook event payload
            
        Returns:
            Mode string ("app" or "harness")
        """
        prompt_lower = user_prompt.strip().lower()
        
        # Primary: explicit command prefix
        if prompt_lower.startswith("mode:harness"):
            return "harness"
        if prompt_lower.startswith("mode:app"):
            return "app"
        
        # Fallback: keyword detection (with deprecation warning)
        review_keywords = [
            "review harness", "audit governor", "check harness rules",
            "inspect harness", "harness review", "governor audit"
        ]
        for keyword in review_keywords:
            if keyword in prompt_lower:
                # Log deprecation warning (would use logger in production)
                # logger.warning("mode_detected_via_keyword", keyword=keyword,
                #     message="Consider using mode:harness or mode:app for explicit mode control")
                return "harness"
        
        # Default to app mode
        return "app"
    
    def _build_research_worksheet(self, user_prompt: str, mode: str) -> str:
        """
        Build research worksheet context for enrichment.
        
        The research worksheet provides structured guidance for
        research-phase activities based on the current mode.
        
        Args:
            user_prompt: User's prompt text
            mode: Current execution mode
            
        Returns:
            Research worksheet context string
        """
        worksheet = f"""
=== RESEARCH WORKSHEET ===
Query: {user_prompt[:100]}{'...' if len(user_prompt) > 100 else ''}

Research Tasks:
1. Analyze the query and identify key components
2. Search for relevant information using allowed tools
3. Synthesize findings into a coherent response
4. Document sources and evidence
5. Prepare for planning phase if action is required

Mode: {mode.upper()}
- If APP: Focus on task-specific research
- If HARNESS: Focus on governance compliance and security analysis

Research Guidelines:
- Use web_search for external information
- Use read for local codebase exploration
- Document all sources
- Maintain traceability of findings
=== END WORKSHEET ===
"""
        return worksheet
