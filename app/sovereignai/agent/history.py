from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class TokenBudgetExceededError(Exception):

    def __init__(self, minimum: int, maximum: int) -> None:
        self.minimum = minimum
        self.maximum = maximum
        super().__init__(
            f"Pinned minimum ({minimum}) exceeds adapter max_context_tokens ({maximum})"
        )


@dataclass
class TokenBudgetHistory:

    max_context_tokens: int = 8192
    history: list[dict[str, Any]] = field(default_factory=list)

    def add_turn(self, role: str, content: str) -> None:
        self.history.append({"role": role, "content": content})

    def to_messages(self, budget: int) -> list[dict[str, str]]:
        if not self.history:
            return []

        # Estimate token count (rough approximation: 4 chars per token)
        def estimate_tokens(text: str) -> int:
            return len(text) // 4

        # Pinned minimum: system prompt (first turn) + task description (second turn) + last 2 turns
        if len(self.history) >= 4:
            pinned = [self.history[0], self.history[1]] + self.history[-2:]
            middle_turns = self.history[2:-2]
        elif len(self.history) >= 2:
            pinned = self.history[:2] + self.history[-2:]
            middle_turns = []
        else:
            pinned = self.history.copy()
            middle_turns = []

        # Check if pinned minimum exceeds budget
        pinned_tokens = sum(estimate_tokens(turn["content"]) for turn in pinned)
        if pinned_tokens > budget:
            raise TokenBudgetExceededError(minimum=pinned_tokens, maximum=budget)

        # Start with pinned messages
        messages = pinned.copy()

        # Add middle turns if budget allows (insert before the last 2 turns)
        remaining_budget = budget - pinned_tokens
        insert_position = len(pinned) - 2  # Before last 2 turns
        for turn in reversed(middle_turns):  # Reverse to maintain order when inserting
            turn_tokens = estimate_tokens(turn["content"])
            if turn_tokens <= remaining_budget:
                messages.insert(insert_position, turn)
                remaining_budget -= turn_tokens
            else:
                break

        return messages
