from __future__ import annotations

"""
Reusable action plugins for rule enforcement.

Auto-discovered registry for action classes.
"""

import importlib
import pkgutil
from ._base import RuleAction

# Auto-discover and register all actions
_ACTIONS = {}

for _, module_name, _ in pkgutil.iter_modules(__path__):
    # Skip private modules
    if module_name.startswith("_"):
        continue
    
    try:
        # Import the module
        module = importlib.import_module(f".{module_name}", package=__name__)
        
        # Find all RuleAction subclasses
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (isinstance(attr, type) and 
                issubclass(attr, RuleAction) and 
                attr is not RuleAction):
                # Instantiate the action
                instance = attr()
                _ACTIONS[instance.name] = instance
    except Exception as e:
        # Skip modules that fail to import
        pass

# Export class names for backward compatibility
__all__ = [type(a).__name__ for a in _ACTIONS.values()]

# Re-export classes for direct import
from .block_command import BlockCommandAction
from .ghost_template import GhostTemplateAction
from .present_bypass_menu import PresentBypassMenuAction
