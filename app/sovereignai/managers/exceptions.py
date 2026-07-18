"""Exceptions for department managers."""


class SymbolMapUnavailableError(Exception):
    """Raised when SymbolMap is unavailable (e.g., tree-sitter not installed)."""
    pass
