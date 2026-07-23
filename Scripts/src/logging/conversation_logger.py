"""
Conversation logger for capturing and logging AI conversations for audit trails.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import json


@dataclass
class ConversationMessage:
    """Represents a single message in a conversation."""
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: str
    message_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp,
            "message_id": self.message_id,
            "metadata": self.metadata
        }


@dataclass
class ConversationSession:
    """Represents a complete conversation session with audit trail."""
    session_id: str
    trace_id: str
    start_time: str
    end_time: Optional[str] = None
    messages: List[ConversationMessage] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    summary: Optional[str] = None

    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add a message to the conversation session."""
        message = ConversationMessage(
            role=role,
            content=content,
            timestamp=datetime.now(timezone.utc).isoformat(),
            message_id=self._generate_message_id(),
            metadata=metadata or {}
        )
        self.messages.append(message)

    def set_context(self, key: str, value: Any) -> None:
        """Set context information for the session."""
        self.context[key] = value

    def end_session(self, summary: Optional[str] = None) -> None:
        """Mark the session as ended."""
        self.end_time = datetime.now(timezone.utc).isoformat()
        self.summary = summary

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "session_id": self.session_id,
            "trace_id": self.trace_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "messages": [msg.to_dict() for msg in self.messages],
            "context": self.context,
            "summary": self.summary
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    def _generate_message_id(self) -> str:
        """Generate a unique message ID."""
        return f"{self.session_id}-{len(self.messages)}"


class ConversationLogger:
    """Manages conversation logging for audit trails and observability."""
    
    def __init__(self, storage_path: str = "Logs/Architect/Conversations"):
        self.storage_path = storage_path
        self._current_session: Optional[ConversationSession] = None
        self._sessions: List[ConversationSession] = []

    def start_session(
        self,
        session_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> ConversationSession:
        """Start a new conversation session."""
        import uuid
        
        session_id = session_id or str(uuid.uuid4())
        trace_id = trace_id or str(uuid.uuid4())
        
        session = ConversationSession(
            session_id=session_id,
            trace_id=trace_id,
            start_time=datetime.now(timezone.utc).isoformat(),
            context=context or {}
        )
        
        self._current_session = session
        self._sessions.append(session)
        
        return session

    def log_user_message(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Log a user message in the current session."""
        if self._current_session is None:
            raise RuntimeError("No active conversation session. Call start_session() first.")
        
        self._current_session.add_message("user", content, metadata)

    def log_assistant_message(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Log an assistant message in the current session."""
        if self._current_session is None:
            raise RuntimeError("No active conversation session. Call start_session() first.")
        
        self._current_session.add_message("assistant", content, metadata)

    def log_system_message(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Log a system message in the current session."""
        if self._current_session is None:
            raise RuntimeError("No active conversation session. Call start_session() first.")
        
        self._current_session.add_message("system", content, metadata)

    def end_session(self, summary: Optional[str] = None) -> None:
        """End the current conversation session and save it."""
        if self._current_session is None:
            raise RuntimeError("No active conversation session to end.")
        
        self._current_session.end_session(summary)
        self._save_session(self._current_session)
        self._current_session = None

    def get_current_session(self) -> Optional[ConversationSession]:
        """Get the current active session."""
        return self._current_session

    def _save_session(self, session: ConversationSession) -> None:
        """Save a session to storage."""
        import os
        
        os.makedirs(self.storage_path, exist_ok=True)
        
        filename = f"{session.session_id}.json"
        filepath = os.path.join(self.storage_path, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(session.to_json())


# Global conversation logger instance
_global_conversation_logger = ConversationLogger()


def get_conversation_logger() -> ConversationLogger:
    """Get the global conversation logger instance."""
    return _global_conversation_logger