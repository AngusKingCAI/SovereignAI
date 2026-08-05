"""
Hook handlers for Devin CLI lifecycle events.

Auto-discovered registry for all 8 hooks:
- SessionStart
- UserPromptSubmit
- PreToolUse
- PostToolUse
- PermissionRequest
- Stop
- SessionEnd
- PostCompaction
"""

import importlib
import pkgutil
from ._base import HookHandler

# Auto-discover and register all hook handlers
_HOOK_HANDLERS = {}

# Get the current package path
__path__ = __path__ if hasattr(__name__, '__path__') else []

for _, module_name, _ in pkgutil.iter_modules(__path__):
    # Skip private modules
    if module_name.startswith("_"):
        continue
    
    try:
        # Import the module
        module = importlib.import_module(f".{module_name}", package=__name__)
        
        # Find all HookHandler subclasses
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (isinstance(attr, type) and 
                issubclass(attr, HookHandler) and 
                attr is not HookHandler):
                # Instantiate the handler
                instance = attr()
                _HOOK_HANDLERS[instance.hook_name] = instance
    except Exception as e:
        # Skip modules that fail to import
        pass

# Export all discovered handlers
__all__ = list(_HOOK_HANDLERS.values())
