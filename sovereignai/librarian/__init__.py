"""Librarian — the memory router for all SovereignAI components.

Per AR10: All memory access routes through the Librarian. No component
may query a memory backend directly.
"""
from sovereignai.librarian.librarian import Librarian

__all__ = ["Librarian"]
