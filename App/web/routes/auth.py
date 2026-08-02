"""Authentication routes for Plan 31.

Provides bootstrap, login, logout, and rate limiting functionality.
"""

import base64
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
from fastapi import APIRouter, HTTPException, Request, Response

from app.web.schemas import LoginRequest, LoginResponse


router = APIRouter(prefix="/api/auth", tags=["auth"])


# Placeholder for dependencies - will be injected via DI
audit_db = None
users_store = None


def set_dependencies(audit_db_dep=None, users_store_dep=None):
    """Set injected dependencies for auth routes."""
    global audit_db, users_store
    audit_db = audit_db_dep
    users_store = users_store_dep


class RateLimitConfig:
    """Rate limiting configuration."""
    
    MAX_ATTEMPTS_PER_WINDOW = 5
    WINDOW_SECONDS = 60
    LOCKOUT_THRESHOLD = 20
    LOCKOUT_DURATION_SECONDS = 86400  # 24 hours
    
    @staticmethod
    def get_backoff_seconds(consecutive_failures: int) -> int:
        """Calculate exponential backoff delay."""
        if consecutive_failures < 5:
            return 0
        return min(86400, 60 * 2 ** (consecutive_failures - 5))


def generate_setup_token() -> str:
    """Generate a cryptographically random setup token."""
    token_bytes = secrets.token_bytes(32)
    return base64.b64encode(token_bytes).decode('utf-8')


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against a hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


def validate_password_policy(password: str) -> tuple[bool, str]:
    """Validate password meets policy requirements."""
    if len(password) < 12:
        return False, "Password must be at least 12 characters"
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"
    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        return False, "Password must contain at least one special character"
    return True, ""


@router.post("/login", response_model=LoginResponse)
async def login(request: Request, login_data: LoginRequest):
    """Handle user login with rate limiting and session management."""
    if users_store is None or audit_db is None:
        raise HTTPException(status_code=503, detail="Auth service not available")

    # Check for bootstrap mode
    is_bootstrap = not users_store.has_users()
    if is_bootstrap:
        if not login_data.setup_token:
            raise HTTPException(
                status_code=403,
                detail="Setup token required for first login",
            )
        
        # Validate setup token
        if not await audit_db.validate_bootstrap_token(login_data.setup_token):
            raise HTTPException(
                status_code=403,
                detail="Invalid or expired setup token",
            )
        
        # Validate password policy
        is_valid, error_msg = validate_password_policy(login_data.password)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Create user
        hashed_password = hash_password(login_data.password)
        await users_store.create_user(login_data.username, hashed_password)
        
        # Mark setup token as used
        await audit_db.mark_bootstrap_token_used(login_data.setup_token)
    else:
        # Check rate limiting
        rate_limit_info = await audit_db.get_rate_limit_info(login_data.username)
        if rate_limit_info:
            # Check lockout
            if rate_limit_info.get("lockout_until"):
                lockout_until = datetime.fromisoformat(rate_limit_info["lockout_until"])
                if datetime.now(timezone.utc) < lockout_until:
                    raise HTTPException(
                        status_code=423,
                        headers={"Retry-After": str(RateLimitConfig.LOCKOUT_DURATION_SECONDS)},
                        detail="Account locked due to too many failed attempts",
                    )
            
            # Check window
            window_start = datetime.fromisoformat(rate_limit_info["window_start"])
            if datetime.now(timezone.utc) < window_start + timedelta(seconds=RateLimitConfig.WINDOW_SECONDS):
                if rate_limit_info["attempt_count"] >= RateLimitConfig.MAX_ATTEMPTS_PER_WINDOW:
                    backoff = RateLimitConfig.get_backoff_seconds(rate_limit_info["consecutive_failures"])
                    raise HTTPException(
                        status_code=429,
                        headers={"Retry-After": str(backoff)},
                        detail="Too many login attempts",
                    )
        
        # Verify password
        user = await users_store.get_user(login_data.username)
        if not user or not verify_password(login_data.password, user["password_hash"]):
            # Record failed attempt
            await audit_db.record_failed_attempt(login_data.username)
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Reset consecutive failures on success
        await audit_db.reset_consecutive_failures(login_data.username)
    
    # Create session
    session_id = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
    await audit_db.create_session(session_id, login_data.username, expires_at)
    
    # Calculate cookie attributes
    is_https = request.url.scheme == "https"
    is_loopback = request.client.host in ("127.0.0.1", "::1")
    
    # Set cookie
    response = LoginResponse(
        expires_at=expires_at.isoformat(),
        username=login_data.username,
    )
    
    cookie_kwargs = {
        "key": "session_id",
        "value": session_id,
        "httponly": True,
        "samesite": "strict",
        "max_age": 86400,  # 24 hours
    }
    
    if is_https or is_loopback:
        cookie_kwargs["secure"] = True
    
    # Return response with cookie
    http_response = Response(content=response.model_dump_json(), media_type="application/json")
    http_response.set_cookie(**cookie_kwargs)
    
    return http_response


@router.post("/logout")
async def logout(request: Request):
    """Handle user logout."""
    if audit_db is None:
        raise HTTPException(status_code=503, detail="Auth service not available")

    session_id = request.cookies.get("session_id")
    if session_id:
        await audit_db.delete_session(session_id)
    
    return Response(status_code=204)


@router.get("/bootstrap/status")
async def bootstrap_status():
    """Check if bootstrap is required."""
    if users_store is None:
        raise HTTPException(status_code=503, detail="Auth service not available")

    is_bootstrap = not users_store.has_users()
    return {"requires_bootstrap": is_bootstrap}


@router.get("/rate-limit/{username}")
async def get_rate_limit_status(username: str):
    """Get rate limit status for a user (for testing/admin)."""
    if audit_db is None:
        raise HTTPException(status_code=503, detail="Auth service not available")

    rate_limit_info = await audit_db.get_rate_limit_info(username)
    if not rate_limit_info:
        return {"username": username, "attempts": 0, "consecutive_failures": 0}
    
    return rate_limit_info
