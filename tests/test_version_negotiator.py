"""Test version negotiation between components."""

from pathlib import Path
from unittest.mock import MagicMock

from sovereignai.shared.types import (
    ComponentId,
    ComponentManifest,
)
from sovereignai.versioning.negotiator import (
    FatalIncompatibilityError,
    Incompatibility,
    VersionNegotiator,
)


def test_negotiate_core_compatible() -> None:
    """Negotiate compatible core components."""
    mock_graph = MagicMock()
    mock_trace = MagicMock()

    # Use actual sovereignai package path for core detection
    import sovereignai
    sovereignai_path = str(Path(sovereignai.__file__).resolve().parent)

    core1 = ComponentManifest(
        component_id=ComponentId("core1"),
        version="1.2.0",
        author="test",
        content_hash="hash1",
        provides=(),
        requires=(),
        core=True,
        _source_path=sovereignai_path + "/core1.py",
    )

    core2 = ComponentManifest(
        component_id=ComponentId("core2"),
        version="1.2.0",
        author="test",
        content_hash="hash2",
        provides=(),
        requires=(),
        core=True,
        _source_path=sovereignai_path + "/core2.py",
    )

    mock_graph.list_all_components.return_value = (core1, core2)

    negotiator = VersionNegotiator(capability_graph=mock_graph, trace=mock_trace)
    result = negotiator.negotiate()

    assert result.can_start
    assert len(result.fatal_incompatibilities) == 0
    assert len(result.disabled_plugins) == 0


def test_negotiate_core_incompatible_major() -> None:
    """Negotiate incompatible core components (major version mismatch)."""
    mock_graph = MagicMock()
    mock_trace = MagicMock()

    # Use actual sovereignai package path for core detection
    import sovereignai
    sovereignai_path = str(Path(sovereignai.__file__).resolve().parent)

    core1 = ComponentManifest(
        component_id=ComponentId("core1"),
        version="1.2.0",
        author="test",
        content_hash="hash1",
        provides=(),
        requires=(),
        core=True,
        _source_path=sovereignai_path + "/core1.py",
    )

    core2 = ComponentManifest(
        component_id=ComponentId("core2"),
        version="2.0.0",
        author="test",
        content_hash="hash2",
        provides=(),
        requires=(),
        core=True,
        _source_path=sovereignai_path + "/core2.py",
    )

    mock_graph.list_all_components.return_value = (core1, core2)

    negotiator = VersionNegotiator(capability_graph=mock_graph, trace=mock_trace)
    result = negotiator.negotiate()

    assert not result.can_start
    assert len(result.fatal_incompatibilities) == 1
    assert result.fatal_incompatibilities[0].reason == "major version mismatch or downgrade"


def test_negotiate_core_missing_version() -> None:
    """Negotiate core component missing version field (fatal error)."""
    mock_graph = MagicMock()
    mock_trace = MagicMock()

    # Use actual sovereignai package path for core detection
    import sovereignai
    sovereignai_path = str(Path(sovereignai.__file__).resolve().parent)

    core = ComponentManifest(
        component_id=ComponentId("core1"),
        version="",
        author="test",
        content_hash="hash1",
        provides=(),
        requires=(),
        core=True,
        _source_path=sovereignai_path + "/core1.py",
    )

    other = ComponentManifest(
        component_id=ComponentId("core2"),
        version="1.0.0",
        author="test",
        content_hash="hash2",
        provides=(),
        requires=(),
        core=True,
        _source_path=sovereignai_path + "/core2.py",
    )

    mock_graph.list_all_components.return_value = (core, other)

    negotiator = VersionNegotiator(capability_graph=mock_graph, trace=mock_trace)
    result = negotiator.negotiate()

    assert not result.can_start
    assert len(result.fatal_incompatibilities) == 1
    assert "missing version field" in result.fatal_incompatibilities[0].reason


def test_negotiate_plugin_missing_version_defaults() -> None:
    """Negotiate plugin missing version field (defaults to 0.0.0, passes)."""
    mock_graph = MagicMock()
    mock_trace = MagicMock()

    plugin1 = ComponentManifest(
        component_id=ComponentId("plugin1"),
        version="",
        author="test",
        content_hash="hash1",
        provides=(),
        requires=(),
        core=False,
    )

    plugin2 = ComponentManifest(
        component_id=ComponentId("plugin2"),
        version="",
        author="test",
        content_hash="hash2",
        provides=(),
        requires=(),
        core=False,
    )

    mock_graph.list_all_components.return_value = (plugin1, plugin2)

    negotiator = VersionNegotiator(capability_graph=mock_graph, trace=mock_trace)
    result = negotiator.negotiate()

    assert result.can_start
    assert len(result.fatal_incompatibilities) == 0


def test_negotiate_plugin_outside_sovereignai() -> None:
    """Negotiate plugin outside sovereignai package (core=true ignored)."""
    mock_graph = MagicMock()
    mock_trace = MagicMock()

    # Plugin outside sovereignai with core=true should be treated as plugin
    plugin = ComponentManifest(
        component_id=ComponentId("external_plugin"),
        version="1.0.0",
        author="test",
        content_hash="hash1",
        provides=(),
        requires=(),
        core=True,  # Ignored because outside sovereignai
        _source_path="/some/external/path/manifest.toml",
    )

    mock_graph.list_all_components.return_value = (plugin,)

    negotiator = VersionNegotiator(capability_graph=mock_graph, trace=mock_trace)
    result = negotiator.negotiate()

    assert result.can_start


def test_fatal_incompatibility_error() -> None:
    """Test FatalIncompatibilityError exception."""
    incompatibilities = [
        Incompatibility(
            component_a=ComponentId("core1"),
            version_a="1.0.0",
            component_b=ComponentId("core2"),
            version_b="2.0.0",
            reason="major version mismatch",
        )
    ]

    error = FatalIncompatibilityError(incompatibilities)

    assert "Fatal incompatibilities detected:" in str(error)
    assert "major version mismatch" in str(error)
    assert error.incompatibilities == incompatibilities
