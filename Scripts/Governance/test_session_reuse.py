#!/usr/bin/env python3
"""Test session reuse logic."""
import os
import subprocess
import json

# First call - should create new session
print("First call (should create new session):")
result1 = subprocess.run(
    ['python', 'C:/SovereignAI/Scripts/Governance/Hooks/unified_session_logger.py'],
    input='{"hook_event_name":"SessionStart"}',
    capture_output=True,
    text=True
)
print(result1.stdout)

# Extract session file from first call
if result1.returncode == 0:
    try:
        output_data = json.loads(result1.stdout)
        session_file = output_data.get('hookSpecificOutput', {}).get('additionalContext', '').split('Session File: ')[1].split('\n')[0]
        print(f"Session file created: {session_file}")
        
        # Second call - should reuse session
        print("\nSecond call (should reuse session):")
        env = os.environ.copy()
        env['DEVIN_SESSION_FILE'] = session_file
        result2 = subprocess.run(
            ['python', 'C:/SovereignAI/Scripts/Governance/Hooks/unified_session_logger.py'],
            input='{"hook_event_name":"SessionStart"}',
            capture_output=True,
            text=True,
            env=env
        )
        print(result2.stdout)
        
        # Check if same session file was used
        if result2.returncode == 0:
            output_data2 = json.loads(result2.stdout)
            session_file2 = output_data2.get('hookSpecificOutput', {}).get('additionalContext', '').split('Session File: ')[1].split('\n')[0]
            if session_file == session_file2:
                print("SUCCESS: Session file reused correctly")
            else:
                print(f"PROBLEM: Different session files: {session_file} vs {session_file2}")
    except Exception as e:
        print(f"Error parsing output: {e}")