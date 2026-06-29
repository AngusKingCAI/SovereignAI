"""Test SemVer parsing and comparison."""

import pytest

from sovereignai.versioning.semver import SemVer


def test_parse_basic_version() -> None:
    """Parse a basic version string without prerelease or build metadata."""
    version = SemVer.parse("1.2.3")
    assert version.major == 1
    assert version.minor == 2
    assert version.patch == 3
    assert version.prerelease == ""
    assert version.build == ""
    assert str(version) == "1.2.3"


def test_parse_with_prerelease() -> None:
    """Parse a version string with prerelease identifier."""
    version = SemVer.parse("1.2.3-alpha")
    assert version.major == 1
    assert version.minor == 2
    assert version.patch == 3
    assert version.prerelease == "alpha"
    assert version.build == ""
    assert str(version) == "1.2.3-alpha"


def test_parse_with_build() -> None:
    """Parse a version string with build metadata."""
    version = SemVer.parse("1.2.3+build.123")
    assert version.major == 1
    assert version.minor == 2
    assert version.patch == 3
    assert version.prerelease == ""
    assert version.build == "build.123"
    assert str(version) == "1.2.3+build.123"


def test_parse_with_prerelease_and_build() -> None:
    """Parse a version string with both prerelease and build metadata."""
    version = SemVer.parse("1.2.3-alpha+build.123")
    assert version.major == 1
    assert version.minor == 2
    assert version.patch == 3
    assert version.prerelease == "alpha"
    assert version.build == "build.123"
    assert str(version) == "1.2.3-alpha+build.123"


def test_parse_empty_string_raises() -> None:
    """Raise ValueError when parsing an empty string."""
    with pytest.raises(ValueError, match="Version string cannot be empty"):
        SemVer.parse("")


def test_parse_invalid_format_raises() -> None:
    """Raise ValueError when parsing an invalid format."""
    with pytest.raises(ValueError, match="Invalid version format"):
        SemVer.parse("1.2")


def test_parse_non_integer_parts_raises() -> None:
    """Raise ValueError when version parts are not integers."""
    with pytest.raises(ValueError, match="Version parts must be integers"):
        SemVer.parse("a.b.c")


def test_parse_negative_parts_raises() -> None:
    """Raise ValueError when version parts are negative."""
    with pytest.raises(ValueError, match="Version parts must be integers"):
        SemVer.parse("1.2.-3")


def test_comparison_major_version() -> None:
    """Compare versions by major version."""
    v1 = SemVer.parse("2.0.0")
    v2 = SemVer.parse("1.9.9")
    assert v1 > v2
    assert v2 < v1


def test_comparison_minor_version() -> None:
    """Compare versions by minor version when major is equal."""
    v1 = SemVer.parse("1.2.0")
    v2 = SemVer.parse("1.1.9")
    assert v1 > v2
    assert v2 < v1


def test_comparison_patch_version() -> None:
    """Compare versions by patch version when major and minor are equal."""
    v1 = SemVer.parse("1.2.3")
    v2 = SemVer.parse("1.2.2")
    assert v1 > v2
    assert v2 < v1


def test_comparison_prerelease_less_than_release() -> None:
    """Compare prerelease versions as less than release versions."""
    v1 = SemVer.parse("1.2.3-alpha")
    v2 = SemVer.parse("1.2.3")
    assert v1 < v2
    assert v2 > v1


def test_comparison_prerelease_numeric() -> None:
    """Compare prerelease versions with numeric identifiers."""
    v1 = SemVer.parse("1.2.3-alpha.2")
    v2 = SemVer.parse("1.2.3-alpha.1")
    assert v1 > v2
    assert v2 < v1


def test_comparison_prerelease_alphanumeric() -> None:
    """Compare prerelease versions with alphanumeric identifiers."""
    v1 = SemVer.parse("1.2.3-alpha.beta")
    v2 = SemVer.parse("1.2.3-alpha.alpha")
    assert v1 > v2
    assert v2 < v1


def test_comparison_prerelease_shorter_list() -> None:
    """Compare prerelease versions where shorter list is less."""
    v1 = SemVer.parse("1.2.3-alpha.1")
    v2 = SemVer.parse("1.2.3-alpha")
    assert v1 > v2
    assert v2 < v1


def test_equality() -> None:
    """Check version equality (build metadata is ignored)."""
    v1 = SemVer.parse("1.2.3")
    v2 = SemVer.parse("1.2.3")
    assert v1 == v2

    v3 = SemVer.parse("1.2.3+build.123")
    v4 = SemVer.parse("1.2.3+build.456")
    assert v3 == v4  # Build metadata ignored


def test_is_compatible_with_same_major() -> None:
    """Check compatibility when major versions match (directional: this >= other)."""
    v1 = SemVer.parse("1.2.3")
    v2 = SemVer.parse("1.2.4")
    # v1 (1.2.3) is NOT compatible with v2 (1.2.4) because patch is lower
    assert not v1.is_compatible_with(v2)
    # v2 (1.2.4) IS compatible with v1 (1.2.3) because patch is higher
    assert v2.is_compatible_with(v1)


def test_is_compatible_with_minor_upgrade() -> None:
    """Check compatibility when minor version is upgraded (directional: this >= other)."""
    v1 = SemVer.parse("1.2.3")
    v2 = SemVer.parse("1.3.0")
    # v1 (1.2.3) is NOT compatible with v2 (1.3.0) because minor is lower
    assert not v1.is_compatible_with(v2)
    # v2 (1.3.0) IS compatible with v1 (1.2.3) because minor is higher
    assert v2.is_compatible_with(v1)


def test_is_compatible_with_major_mismatch() -> None:
    """Check incompatibility when major versions differ."""
    v1 = SemVer.parse("1.2.3")
    v2 = SemVer.parse("2.0.0")
    assert not v1.is_compatible_with(v2)
    assert not v2.is_compatible_with(v1)


def test_is_compatible_with_patch_downgrade() -> None:
    """Check incompatibility when patch version is downgraded (directional: this >= other)."""
    v1 = SemVer.parse("1.2.3")
    v2 = SemVer.parse("1.2.2")
    # v1 (1.2.3) IS compatible with v2 (1.2.2) because patch is higher
    assert v1.is_compatible_with(v2)
    # v2 (1.2.2) is NOT compatible with v1 (1.2.3) because patch is lower
    assert not v2.is_compatible_with(v1)
