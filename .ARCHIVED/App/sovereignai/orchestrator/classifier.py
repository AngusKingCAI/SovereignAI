from __future__ import annotations

import asyncio
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Protocol


class Department(Enum):
    CODING = "coding"
    RESEARCH = "research"
    EDUCATION = "education"
    COMMUNICATION = "communication"
    SECURITY = "security"
    OPERATIONS = "operations"
    UNKNOWN = "unknown"


@dataclass
class ClassificationResult:
    department: Department
    confidence: float
    metadata: dict[str, str]


class IntentClassifier(ABC):

    @abstractmethod
    async def classify(self, user_message: str) -> ClassificationResult:
        ...


class LLMClientProtocol(Protocol):

    async def generate(
        self,
        prompt: str,
        model: str = "llama3.2",
        timeout_seconds: float = 30.0,
    ) -> str:
        ...


class RuleBasedClassifier(IntentClassifier):

    def __init__(self) -> None:
        self._keyword_map = {
            Department.CODING: [
                "code", "coding", "implement", "function", "class", "bug", "fix",
                "debug", "refactor", "test", "script", "program", "develop",
                "software", "api", "endpoint", "database", "query", "algorithm",
            ],
            Department.RESEARCH: [
                "research", "investigate", "study", "analyze", "find", "search",
                "explore", "discover", "learn", "understand", "explain", "information",
                "data", "report", "survey", "experiment", "hypothesis",
            ],
            Department.EDUCATION: [
                "teach", "train", "learn", "education", "tutorial", "course",
                "lesson", "explain", "guide", "instruction", "study", "curriculum",
                "mentor", "coach", "skill", "knowledge",
            ],
            Department.COMMUNICATION: [
                "write", "document", "blog", "post", "article", "content",
                "communicate", "announce", "publish", "email", "message",
                "presentation", "report", "summary", "draft",
            ],
            Department.SECURITY: [
                "security", "secure", "protect", "encrypt", "auth", "authenticate",
                "permission", "access", "vulnerability", "threat", "audit",
                "compliance", "policy", "firewall", "intrusion",
            ],
            Department.OPERATIONS: [
                "deploy", "operations", "monitor", "scale", "infrastructure",
                "server", "cloud", "devops", "ci", "cd", "pipeline", "log",
                "performance", "uptime", "availability", "backup",
            ],
        }

    async def classify(self, user_message: str) -> ClassificationResult:
        message_lower = user_message.lower()
        scores = {}

        for department, keywords in self._keyword_map.items():
            score = 0
            matched_keywords = []
            for keyword in keywords:
                pattern = rf'\b{re.escape(keyword)}\b'
                if re.search(pattern, message_lower):
                    score += 1
                    matched_keywords.append(keyword)
            if score > 0:
                scores[department] = (score, matched_keywords)

        if not scores:
            return ClassificationResult(
                department=Department.UNKNOWN,
                confidence=0.0,
                metadata={"reason": "no_keywords_matched", "classifier": "rule"}
            )

        best_department, (best_score, matched) = max(
            scores.items(),
            key=lambda item: item[1][0]
        )

        confidence = min(best_score / 3.0, 1.0)

        return ClassificationResult(
            department=best_department,
            confidence=confidence,
            metadata={
                "matched_keywords": ",".join(matched),
                "match_count": str(best_score),
                "classifier": "rule",
            }
        )


class LLMClassifier(IntentClassifier):

    def __init__(self, llm_client: LLMClientProtocol, fallback: RuleBasedClassifier) -> None:
        self._llm_client = llm_client
        self._fallback = fallback
        self._timeout = 10.0

    async def classify(self, user_message: str) -> ClassificationResult:
        try:
            result = await asyncio.wait_for(
                self._classify_with_llm(user_message),
                timeout=self._timeout
            )
            return result
        except TimeoutError:
            from sovereignai.shared.trace_emitter import TraceEmitter, TraceLevel
            trace = TraceEmitter()
            trace.emit(
                component="LLMClassifier",
                level=TraceLevel.WARN,
                message="LLM classification timed out, falling back to rule-based"
            )
            return await self._fallback.classify(user_message)
        except Exception:
            from sovereignai.shared.trace_emitter import TraceEmitter, TraceLevel
            trace = TraceEmitter()
            trace.emit(
                component="LLMClassifier",
                level=TraceLevel.WARN,
                message="LLM classification failed, falling back to rule-based"
            )
            return await self._fallback.classify(user_message)

    async def _classify_with_llm(self, user_message: str) -> ClassificationResult:
        prompt = self._build_classification_prompt(user_message)
        response = await self._llm_client.generate(prompt)
        return self._parse_llm_response(response)

    def _build_classification_prompt(self, user_message: str) -> str:
        departments = ", ".join([d.value for d in Department if d != Department.UNKNOWN])
        return f"""Classify the following user message into one of these departments: {departments}

User message: {user_message}

Respond with only the department name (e.g., "coding", "research", etc.).
If unsure, respond with "unknown".
"""

    def _parse_llm_response(self, response: str) -> ClassificationResult:
        response_lower = response.strip().lower()
        for department in Department:
            if department.value in response_lower:
                return ClassificationResult(
                    department=department,
                    confidence=0.8,
                    metadata={"classifier": "llm", "raw_response": response[:100]}
                )
        return ClassificationResult(
            department=Department.UNKNOWN,
            confidence=0.0,
            metadata={"classifier": "llm", "raw_response": response[:100], "reason": "parse_failed"}
        )
