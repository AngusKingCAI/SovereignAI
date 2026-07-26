"""Simple test for SessionEnd hook."""

import json
import sys
from datetime import datetime
from pathlib import Path

def main():
    """Test SessionEnd hook with simple logging."""
    try:
        data = json.load(sys.stdin)
        print(f"SessionEnd hook fired at {datetime.now().isoformat()}", file=sys.stderr)
        print(f"Session ID: {data.get('session_id', 'unknown')}", file=sys.stderr)
        print(f"Reason: {data.get('reason', 'unknown')}", file=sys.stderr)
        print(f"Full data: {data}", file=sys.stderr)
        
        # Write to a test file
        log_dir = Path("Logs/Architect/Session")
        log_dir.mkdir(parents=True, exist_ok=True)
        test_file = log_dir / "session_end_test.txt"
        with open(test_file, 'a', encoding='utf-8') as f:
            f.write(f"SessionEnd fired: {datetime.now().isoformat()}\n")
            f.write(f"Session ID: {data.get('session_id', 'unknown')}\n")
            f.write(f"Reason: {data.get('reason', 'unknown')}\n")
            f.write(f"---\n")
        
        print(f"Test file created: {test_file}", file=sys.stderr)
    except Exception as e:
        print(f"Error in SessionEnd test: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)

if __name__ == "__main__":
    main()