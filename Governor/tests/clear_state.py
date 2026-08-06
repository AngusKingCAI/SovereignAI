from state_machine import StateMachine
import json

# Clear the state.json session permissions
sm = StateMachine()
sm.clear_permissions(scope='session')
print('Cleared session permissions')

# Check state
state = sm.get_state_snapshot()
print(f'State permissions: {state.get("permissions", {})}')
