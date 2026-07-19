from __future__ import annotations

import pytest
from sovereignai.orchestrator.classifier import (
    ClassificationResult,
    Department,
    LLMClassifier,
    LLMClientProtocol,
    RuleBasedClassifier,
)


class MockLLMClient(LLMClientProtocol):

    def __init__(self, response: str = "coding") -> None:
        self._response = response

    async def generate(
        self,
        prompt: str,
        model: str = "llama3.2",
        timeout_seconds: float = 30.0,
    ) -> str:
        return self._response


@pytest.mark.asyncio
async def test_rule_based_classifier_coding() -> None:
    classifier = RuleBasedClassifier()
    result = await classifier.classify("fix the login bug")
    assert result.department == Department.CODING
    assert result.confidence > 0


@pytest.mark.asyncio
async def test_rule_based_classifier_research() -> None:
    classifier = RuleBasedClassifier()
    result = await classifier.classify("research the latest AI models")
    assert result.department == Department.RESEARCH
    assert result.confidence > 0


@pytest.mark.asyncio
async def test_rule_based_classifier_unknown() -> None:
    classifier = RuleBasedClassifier()
    result = await classifier.classify("hello world")
    assert result.department == Department.UNKNOWN
    assert result.confidence == 0.0


@pytest.mark.asyncio
async def test_rule_based_classifier_case_insensitive() -> None:
    classifier = RuleBasedClassifier()
    result = await classifier.classify("FIX THE BUG")
    assert result.department == Department.CODING


@pytest.mark.asyncio
async def test_llm_classifier_success() -> None:
    mock_client = MockLLMClient("coding")
    fallback = RuleBasedClassifier()
    classifier = LLMClassifier(mock_client, fallback)
    result = await classifier.classify("write some code")
    assert result.department == Department.CODING
    assert result.metadata["classifier"] == "llm"


@pytest.mark.asyncio
async def test_llm_classifier_timeout_fallback() -> None:
    class SlowLLMClient(LLMClientProtocol):
        async def generate(
            self,
            prompt: str,
            model: str = "llama3.2",
            timeout_seconds: float = 30.0,
        ) -> str:
            import asyncio
            await asyncio.sleep(20)
            return "coding"

    mock_client = SlowLLMClient()
    fallback = RuleBasedClassifier()
    classifier = LLMClassifier(mock_client, fallback)
    result = await classifier.classify("write some code")
    assert result.department == Department.CODING
    assert result.metadata["classifier"] == "rule"


@pytest.mark.asyncio
async def test_llm_classifier_error_fallback() -> None:
    class BrokenLLMClient(LLMClientProtocol):
        async def generate(
            self,
            prompt: str,
            model: str = "llama3.2",
            timeout_seconds: float = 30.0,
        ) -> str:
            raise RuntimeError("LLM failed")

    mock_client = BrokenLLMClient()
    fallback = RuleBasedClassifier()
    classifier = LLMClassifier(mock_client, fallback)
    result = await classifier.classify("fix the bug")
    assert result.department == Department.CODING
    assert result.metadata["classifier"] == "rule"


@pytest.mark.asyncio
async def test_llm_classifier_parse_failure() -> None:
    mock_client = MockLLMClient("invalid response")
    fallback = RuleBasedClassifier()
    classifier = LLMClassifier(mock_client, fallback)
    result = await classifier.classify("hello world")
    assert result.department == Department.UNKNOWN
    assert result.metadata["classifier"] == "llm"
    assert result.metadata["reason"] == "parse_failed"


def test_department_enum() -> None:
    assert Department.CODING.value == "coding"
    assert Department.RESEARCH.value == "research"
    assert Department.EDUCATION.value == "education"
    assert Department.COMMUNICATION.value == "communication"
    assert Department.SECURITY.value == "security"
    assert Department.OPERATIONS.value == "operations"
    assert Department.UNKNOWN.value == "unknown"


def test_classification_result() -> None:
    result = ClassificationResult(
        department=Department.CODING,
        confidence=0.9,
        metadata={"key": "value"}
    )
    assert result.department == Department.CODING
    assert result.confidence == 0.9
    assert result.metadata == {"key": "value"}
