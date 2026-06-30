# Plan 17.5 — Fix Registration Block + Cookie Secure Flag

**Hotfix**: Two API fixes blocking login and registration. Round Table vetoed.

Depends on: prompt-17.4

---

## S0 — Opening

**S0.1** — Run `/open`. Verify `prompt-17.4` tag on origin. Clean working copy on `main`.

**S0.2** — Read `AGENTS.md` in full. Read `close.md` in full (per OR71).

**S0.3** — No new rules. Proceed to S1.

---

## S1 — Fix registration endpoint blocking existing users

**File**: `web/main.py`

The `/api/auth/register` endpoint returns 403 "Registration closed — user already exists" when any users exist. This prevents creating additional accounts. The page redirect was fixed in 17.4 but the API endpoint still blocks.

**Find**:
```python
@app.post("/api/auth/register")
async def register(request: Request) -> dict:
    """First-run registration. Only allowed when no users exist."""
    data = await request.json()
    container: Any = request.app.state.container
    auth: Any = container.retrieve(AuthMiddleware)
    if len(auth._password_hashes) > 0:
        raise HTTPException(status_code=403, detail="Registration closed — user already exists")
    try:
        auth.register_user(data["username"], data["password"])
    except ValueError as exc:
        raise HTTPException(
            status_code=403, detail="Registration closed — user already exists"
        ) from exc
    return {"status": "created"}
```

**Replace with**:
```python
@app.post("/api/auth/register")
async def register(request: Request) -> dict:
    """Register a new user account."""
    data = await request.json()
    container: Any = request.app.state.container
    auth: Any = container.retrieve(AuthMiddleware)
    try:
        auth.register_user(data["username"], data["password"])
    except ValueError as exc:
        raise HTTPException(
            status_code=409, detail=str(exc)
        ) from exc
    return {"status": "created"}
```

**Changes**:
- Removed the "only allowed when no users exist" block (`if len(auth._password_hashes) > 0`)
- Changed HTTP status from 403 (Forbidden) to 409 (Conflict) for duplicate username — 409 is the correct status code for "resource already exists"
- Changed error message from "Registration closed" to the actual ValueError message (e.g., "User 'Angus' already registered") so the user knows what went wrong
- Updated docstring

---

## S2 — Fix cookie `secure=True` breaking localhost login

**File**: `web/main.py`

The login endpoint sets the session cookie with `secure=True`, which means the browser only sends it over HTTPS. On `http://127.0.0.1` (localhost HTTP), the browser never sends the cookie back — every authenticated request after login gets 401 Unauthorized.

**Find** (in the `/api/auth/login` endpoint):
```python
        response.set_cookie(
            key="session_id",
            value=session.token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=86400,
        )
```

**Replace with**:
```python
        response.set_cookie(
            key="session_id",
            value=session.token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=86400,
        )
```

**Change**: `secure=True` → `secure=False`.

**Note**: When deploying with HTTPS in production, change this back to `secure=True`. For local development over HTTP, `secure=False` is required. A future plan should detect the protocol and set this dynamically (`secure=request.url.scheme == "https"`).

---

## S3 — Update test for new registration behavior

**File**: `tests/test_web_auth.py` (or `tests/test_first_run.py`)

Any test that asserts registration returns 403 when a user already exists needs to be updated to expect 409 instead.

**Find** any test like:
```python
    assert response.status_code == 403
    assert "Registration closed" in response.json()["detail"]
```

**Replace with**:
```python
    assert response.status_code == 409
    assert "already registered" in response.json()["detail"]
```

---

## S4 — Run /close (ALL 22 steps per OR96)

Run the full `/close` workflow. Do NOT skip any steps. Do NOT commit with known failures. Do NOT tag until all steps pass.

---

## Files WILL Edit
- `web/main.py` (S1 — registration endpoint, S2 — cookie secure flag)
- `tests/test_web_auth.py` or `tests/test_first_run.py` (S3 — update test expectations)

## Files WILL NOT Edit
- Any other file

---

## Closing

Run `/close`. Tag: `prompt-17.5`. Per OR83, use `git add -A`. Per OR71, re-read `close.md` fresh. Per OR96, complete ALL 22 steps.
