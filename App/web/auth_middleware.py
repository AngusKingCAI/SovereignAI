"""Authentication middleware for Plan 33.

Provides public route allowlist and authentication enforcement.
"""

from fastapi import Request, HTTPException
from typing import Callable


PUBLIC_ROUTES = [
    "/api/lifecycle/ready",
    "/health",
]


def is_public_route(path: str) -> bool:
    """Check if path is in public allowlist."""
    for public_route in PUBLIC_ROUTES:
        if path == public_route or path.startswith(public_route):
            return True
    return False


async def require_auth(request: Request) -> None:
    """Require authentication for protected routes."""
    path = request.url.path
    
    # Skip auth for public routes
    if is_public_route(path):
        return
    
    # Placeholder for real auth logic (S8)
    pass
