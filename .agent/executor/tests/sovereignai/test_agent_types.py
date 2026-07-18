"""Tests for agent types and protocols (Plan 23 S9)."""


from sovereignai.agent.protocols import GraphMemory
from sovereignai.agent.types import AgentErrorObservation, AgentResult, FinalAnswer


def test_agent_error_observation_creation():
    """Test AgentErrorObservation creation."""
    error = AgentErrorObservation(
        error_type="TestError",
        message="Test error message",
        last_response="Last response",
        failure_reasons=["reason1", "reason2"],
        retryable=True,
    )

    assert error.error_type == "TestError"
    assert error.message == "Test error message"
    assert error.last_response == "Last response"
    assert error.failure_reasons == ["reason1", "reason2"]
    assert error.retryable is True


def test_agent_error_observation_defaults():
    """Test AgentErrorObservation default values."""
    error = AgentErrorObservation(
        error_type="TestError",
        message="Test error message",
    )

    assert error.last_response is None
    assert error.failure_reasons == []
    assert error.retryable is False


def test_final_answer_creation():
    """Test FinalAnswer creation."""
    answer = FinalAnswer(content="The answer is 42")

    assert answer.content == "The answer is 42"


def test_agent_result_success():
    """Test AgentResult for success case."""
    result = AgentResult(
        status="success",
        output="Task completed",
        trace=["step1", "step2"],
    )

    assert result.status == "success"
    assert result.output == "Task completed"
    assert result.error is None
    assert result.trace == ["step1", "step2"]


def test_agent_result_error():
    """Test AgentResult for error case."""
    error = AgentErrorObservation(
        error_type="RuntimeError",
        message="Something went wrong",
    )
    result = AgentResult(
        status="error",
        output=None,
        error=error,
        trace=["step1"],
    )

    assert result.status == "error"
    assert result.output is None
    assert result.error is error
    assert result.trace == ["step1"]


def test_graph_memory_protocol_is_runtime_checkable():
    """Test that GraphMemory protocol is runtime_checkable (P23-A)."""
    # Protocol should be runtime_checkable for isinstance checks
    assert hasattr(GraphMemory, "__protocol_attrs__")


def test_graph_memory_protocol_method_signature():
    """Test that GraphMemory protocol has correct method signature."""
    # Protocol should have query method with correct signature
    assert hasattr(GraphMemory, "query")
    # Check method signature (basic check)
    import inspect
    sig = inspect.signature(GraphMemory.query)
    assert "entity_id" in sig.parameters
    assert "depth" in sig.parameters


def test_concrete_class_satisfies_graph_memory_protocol():
    """Test that concrete class can satisfy GraphMemory protocol."""
    class ConcreteMemory:
        def query(self, entity_id: str, depth: int = 2) -> list[dict]:
            return [{"entity": entity_id}]

    concrete = ConcreteMemory()
    # Should satisfy protocol
    assert isinstance(concrete, GraphMemory)


def test_graph_memory_locked_contract():
    """Test that GraphMemory protocol signature is locked per P23-A."""
    # This test documents the locked contract requirement
    # Plan 24 S5 TaskGraphCache.query MUST match exactly
    # Plan 24 S9 MUST include test asserting isinstance(TaskGraphCache(), GraphMemory)

    # The protocol signature is:
    # def query(self, entity_id: str, depth: int = 2) -> list[dict]

    # Any implementation must match this exactly
    class Implementation:
        def query(self, entity_id: str, depth: int = 2) -> list[dict]:
            return []

    impl = Implementation()
    assert isinstance(impl, GraphMemory)
