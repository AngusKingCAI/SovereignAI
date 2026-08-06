"""
Debug script to trace permission behavior
"""
import sys
import json
import os

# Test if PermissionRequest hook is being called
print("Testing PermissionRequest hook behavior...")

# Simulate what happens when a tool is used
print("\n1. Checking if PermissionRequest hook is in hooks.v1.json...")
import json
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
hooks_file = os.path.join(project_root, ".devin", "hooks.v1.json")
with open(hooks_file, 'r') as f:
    hooks = json.load(f)
    print(f"PermissionRequest hook: {hooks.get('PermissionRequest', 'NOT FOUND')}")

print("\n2. Testing PermissionRequest handler directly...")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hook_handlers.permission_request import PermissionRequestHandler
from state_machine import StateMachine

handler = PermissionRequestHandler()
sm = StateMachine()

# Test with a typical file read permission
payload = {
    'permission_type': 'read',
    'resource': 'src/test.py',
    'operation': 'file_read',
    'reason': 'Test'
}

response = handler.execute(payload, sm, None)
print(f"Response decision: {response.get('decision')}")
print(f"Permission decision: {response.get('hookSpecificOutput', {}).get('permissionDecision')}")

print("\n3. Checking config.local.json...")
config_path = os.path.join(project_root, ".devin", "config.local.json")
with open(config_path, 'r') as f:
    config = json.load(f)
    print(f"Current permissions: {config.get('permissions', {})}")

print("\n4. Checking state.json permissions...")
import json
state_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state", "state.json")
with open(state_path, 'r') as f:
    state = json.load(f)
    print(f"State permissions: {state.get('permissions', {})}")
