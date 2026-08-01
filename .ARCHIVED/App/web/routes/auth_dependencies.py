"""Placeholder implementations for auth dependencies.

These will be replaced by real implementations via DI in S8.
"""

import sqlite3
from datetime import datetime, timezone
from typing import Any
import secrets
import base64
import platformdirs


class UsersStore:
    """Placeholder users store."""
    
    def __init__(self):
        self.config_dir = platformdirs.user_config_dir("sovereignai")
        self.users_file = self.config_dir / "users.json"
    
    def has_users(self) -> bool:
        """Check if any users exist."""
        return self.users_file.exists()
    
    async def create_user(self, username: str, password_hash: str):
        """Create a new user."""
        # Placeholder implementation
        pass
    
    async def get_user(self, username: str) -> dict[str, Any] | None:
        """Get user by username."""
        # Placeholder implementation
        return None


class AuditDB:
    """Placeholder audit database."""
    
    def __init__(self):
        self.data_dir = platformdirs.user_data_dir("sovereignai")
        self.db_file = self.data_dir / "audit.db"
    
    async def validate_bootstrap_token(self, token: str) -> bool:
        """Validate bootstrap token."""
        # Placeholder implementation
        return False
    
    async def mark_bootstrap_token_used(self, token: str):
        """Mark bootstrap token as used."""
        # Placeholder implementation
        pass
    
    async def record_failed_attempt(self, username: str):
        """Record failed login attempt."""
        # Placeholder implementation
        pass
    
    async def reset_consecutive_failures(self, username: str):
        """Reset consecutive failures on successful login."""
        # Placeholder implementation
        pass
    
    async def get_rate_limit_info(self, username: str) -> dict[str, Any] | None:
        """Get rate limit info for username."""
        # Placeholder implementation
        return None
    
    async def create_session(self, session_id: str, username: str, expires_at: datetime):
        """Create a new session."""
        # Placeholder implementation
        pass
    
    async def delete_session(self, session_id: str):
        """Delete a session."""
        # Placeholder implementation
        pass