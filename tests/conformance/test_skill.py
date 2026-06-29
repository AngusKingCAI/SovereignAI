"""Conformance tests for skill components."""
from sovereignai.conformance.base import BaseConformanceTest
from sovereignai.conformance.registry import register


@register("skill")
class SkillConformanceTest(BaseConformanceTest):
    """Verify skill components implement the required interface."""

    def test_component_has_required_interface(self, instance) -> None:
        """Verify the skill has a manifest attribute."""
        assert hasattr(instance, "manifest"), "Skill must have manifest attribute"

    def test_skill_has_execute_method(self, instance) -> None:
        """Verify the skill has an execute method."""
        assert hasattr(instance, "execute"), "Skill must have execute method"
        assert callable(instance.execute), "execute must be callable"
