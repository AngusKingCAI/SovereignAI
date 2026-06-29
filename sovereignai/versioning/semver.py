"""Parse and compare semantic version strings according to SemVer 2.0.0 specification."""

from dataclasses import dataclass
from typing import Self


@dataclass(frozen=True)
class SemVer:
    """Represent a semantic version with major, minor, patch, and optional prerelease/build metadata."""  # noqa: E501

    major: int
    minor: int
    patch: int
    prerelease: str = ""
    build: str = ""

    @classmethod
    def parse(cls, version_str: str) -> Self:
        """Parse a version string into a SemVer instance according to SemVer 2.0.0 specification.

        Args:
            version_str: A version string like "1.2.3", "1.2.3-alpha", or "1.2.3-alpha+build".

        Returns:
            A SemVer instance.

        Raises:
            ValueError: If the version string is invalid.
        """
        if not version_str:
            raise ValueError("Version string cannot be empty")

        # Split build metadata (after +)
        build = ""
        if "+" in version_str:
            version_str, build = version_str.split("+", 1)

        # Split prerelease (after -)
        prerelease = ""
        if "-" in version_str:
            version_str, prerelease = version_str.split("-", 1)

        # Parse major.minor.patch
        parts = version_str.split(".")
        if len(parts) != 3:
            raise ValueError(f"Invalid version format: {version_str}")

        try:
            major = int(parts[0])
            minor = int(parts[1])
            patch = int(parts[2])
        except ValueError as e:
            raise ValueError(f"Version parts must be integers: {version_str}") from e

        if major < 0 or minor < 0 or patch < 0:
            raise ValueError(f"Version parts must be non-negative: {version_str}")

        return cls(major, minor, patch, prerelease, build)

    def __str__(self) -> str:
        """Return the canonical string representation of this version."""
        result = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            result += f"-{self.prerelease}"
        if self.build:
            result += f"+{self.build}"
        return result

    def __lt__(self, other: Self) -> bool:
        """Compare versions for less-than using SemVer 2.0.0 precedence rules and specification.

        Args:
            other: The version to compare against.

        Returns:
            True if this version is less than other.
        """
        if self.major != other.major:
            return self.major < other.major
        if self.minor != other.minor:
            return self.minor < other.minor
        if self.patch != other.patch:
            return self.patch < other.patch

        # Prerelease comparison: versions with prerelease are less than without
        if self.prerelease and not other.prerelease:
            return True
        if not self.prerelease and other.prerelease:
            return False
        if not self.prerelease and not other.prerelease:
            return False

        # Both have prerelease - compare dot-separated identifiers
        self_identifiers = self.prerelease.split(".")
        other_identifiers = other.prerelease.split(".")

        for self_id, other_id in zip(self_identifiers, other_identifiers, strict=False):
            # Try numeric comparison
            try:
                self_num = int(self_id)
                other_num = int(other_id)
                if self_num != other_num:
                    return self_num < other_num
            except ValueError:
                # Non-numeric comparison (lexicographic)
                if self_id != other_id:
                    return self_id < other_id

        # If all compared identifiers are equal, the shorter list is less
        return len(self_identifiers) < len(other_identifiers)

    def __eq__(self, other: object) -> bool:
        """Check equality of versions (ignoring build metadata)."""
        if not isinstance(other, SemVer):
            return NotImplemented
        return (
            self.major == other.major
            and self.minor == other.minor
            and self.patch == other.patch
            and self.prerelease == other.prerelease
        )

    def __le__(self, other: Self) -> bool:
        """Check if this version is less than or equal to the other version.

        Args:
            other: The version to compare against.

        Returns:
            True if this version is less than or equal to other.
        """
        return self < other or self == other

    def __gt__(self, other: Self) -> bool:
        """Check if this version is greater than the other version.

        Args:
            other: The version to compare against.

        Returns:
            True if this version is greater than other.
        """
        return not self <= other

    def __ge__(self, other: Self) -> bool:
        """Check if this version is greater than or equal to the other version.

        Args:
            other: The version to compare against.

        Returns:
            True if this version is greater than or equal to other.
        """
        return not self < other

    def __ne__(self, other: object) -> bool:
        """Check if this version is not equal to the other version.

        Args:
            other: The version to compare against.

        Returns:
            True if this version is not equal to other.
        """
        return not self == other

    def is_compatible_with(self, other: Self) -> bool:
        """Check if this version is compatible with another for core components.

        For core components, exact match on major version is required.
        Minor and patch must be >= the required version.

        Args:
            other: The required version to check against.

        Returns:
            True if compatible, False otherwise.
        """
        # Major version must match exactly
        if self.major != other.major:
            return False
        # Minor version must be >= other
        if self.minor < other.minor:
            return False
        # If minor matches, patch must be >= other
        return not (self.minor == other.minor and self.patch < other.patch)
