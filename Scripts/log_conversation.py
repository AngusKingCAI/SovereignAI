"""
Script to log conversation sessions for audit purposes.
Usage: python log_conversation.py <session_id> <summary>
Example: python log_conversation.py workflow-update "Summary of the session"
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))
import src.logging as logging

# Get command line arguments
if len(sys.argv) >= 3:
    session_id = sys.argv[1]
    summary = sys.argv[2]
else:
    session_id = "architect-session"
    summary = "Architect session conversation"

# Get conversation logger
conv_logger = logging.get_conversation_logger()

# Start session for this conversation
session = conv_logger.start_session(
    session_id=session_id,
    trace_id=f"architect-workflow-{int.from_bytes(os.urandom(2), 'big')}",
    context={
        "developer": "AI-Architect",
        "task": "Architect workflow update and gate integration",
        "phase": 0,
        "workflow": "Architect Workflow"
    }
)

# Log a simple session placeholder message
conv_logger.log_user_message("Session started")
conv_logger.log_assistant_message("Architect workflow update session")

# End session
conv_logger.end_session(summary)

print("Conversation logged successfully!")
print(f"Session ID: {session.session_id}")
print(f"Trace ID: {session.trace_id}")
print(f"Storage path: Logs/Architect/Conversations")