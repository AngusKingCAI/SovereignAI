"""Additional tests for semver to improve coverage."""
import pytest

from sovereignai.versioning.semver import SemVer


def test_semver_parse_with_negative_version() -> None:
    """Test that negative version parts raise ValueError."""
    with pytest.raises(ValueError):
        SemVer.parse("1.-1.0")


def test_semver_parse_with_invalid_format() -> None:
    """Test that invalid version format raises ValueError."""
    with pytest.raises(ValueError, match="must be integers"):
        SemVer.parse("1.x.0")


def test_semver_comparison_with_prerelease_identifiers() -> None:
    """Test prerelease identifier comparison."""
    v1 = SemVer.parse("1.0.0-alpha.1")
    v2 = SemVer.parse("1.0.0-alpha.beta")

    assert v1 < v2


def test_semver_comparison_with_build_metadata() -> None:
    """Test that build metadata is ignored in comparison."""
    v1 = SemVer.parse("1.0.0+build.1")
    v2 = SemVer.parse("1.0.0+build.2")

    assert v1 == v2


def test_semver_equality() -> None:
    """Test version equality."""
    v1 = SemVer.parse("1.0.0")
    v2 = SemVer.parse("1.0.0")

    assert v1 == v2


def test_semver_not_equal() -> None:
    """Test version inequality."""
    v1 = SemVer.parse("1.0.0")
    v2 = SemVer.parse("1.0.1")

    assert v1 != v2
