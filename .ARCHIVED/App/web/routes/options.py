"""Options and Model Registry routes for Plan 31.

Mounts existing options and model registry endpoints.
"""

from fastapi import APIRouter

# Import existing routers
from sovereignai.model_registry.api import router as model_registry_router

router = APIRouter(prefix="/api", tags=["options", "models"])


# Mount model registry router
router.include_router(model_registry_router, prefix="/models")


# Placeholder for options routes - these are already in app/web/main.py
# We'll add them here to consolidate all web APIs
def set_options_dependencies(options_backend=None):
    """Set options backend dependency."""
    # This will be used in S8 for DI composition
    pass
