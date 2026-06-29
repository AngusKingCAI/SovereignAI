"""Memory backends for SovereignAI.

Per OR87: Each SQLite memory backend owns a separate database file:
- ~/.sovereignai/episodic.db
- ~/.sovereignai/trace.db
Procedural memory uses a JSON file at ~/.sovereignai/procedural_memory.json.
Working memory is in-process only.
"""
