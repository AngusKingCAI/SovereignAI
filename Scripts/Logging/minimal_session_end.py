"""Minimal SessionEnd test - just writes to a file."""

import json
import sys
from datetime import datetime
from pathlib import Path

def main():
    """Minimal SessionEnd test."""
    try:
        data = json.load(sys.stdin)
        session_id = data.get("session_id", "unknown")
        reason = data.get("reason", "unknown")
        
        # Write to test file
        log_dir = Path("Logs/Architect/Session")
        log_dir.mkdir(parents=True, exist_ok=True)
        test_file = log_dir / "session_end_minimal_test.txt"
        
        with open(test_file, 'a', encoding='utf-8') as f:
            f.write(f"SessionEnd fired: {datetime.now().isoformat()}\n")
            f.write(f"Session ID: {session_id}\n")
            f.write(f"Reason: {reason}\n")
            f.write(f"---\n")
        
        print(f"SessionEnd test: SUCCESS - {session_id}", file=sys.stderr)
    except Exception as e:
        print(f"SessionEnd test: ERROR - {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)

if __name__ == "__main__":
    main()