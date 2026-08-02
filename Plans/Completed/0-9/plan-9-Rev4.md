Depends on: prompt-8
Vision principles: P6 (login gate), P9 (no silent failures), P13 (strong/robust)
Open questions resolved: none

---

## Adjudication Log (Rev3 → Rev4)

### Finding 1 — `register_page` still calls `auth.has_users()` (Kimi C1, Qwen — CRITICAL)
**Action**: ACCEPTED. Third call site fixed: `if len(auth._password_hashes) > 0:`.

### Finding 14 — TOCTOU lock is theater (MiniMax Issue 2 — MEDIUM)
**Action**: ACCEPTED. Remove `threading.Lock` reference. Document that `register_user`'s internal `ValueError` is the atomic point. The `try/except ValueError` in the register endpoint handles the race.

### Finding 15 — SSE 401 infinite reconnect (Kimi M1 — MEDIUM)
**Action**: ACCEPTED. Client-side: before opening EventSource, check auth via `fetch('/api/capabilities')`. If 401, redirect to `/login`. On SSE error, close EventSource and re-check auth. Do NOT let browser auto-reconnect infinitely.

### Finding 10 — Fresh-install UX dead-ends at login (Kimi H6 — HIGH)
**Action**: ACCEPTED. `app.js` detects 401 with detail "No user registered" → redirect to `/register` (not `/login`).

### Finding 17 — `secure=True` hardcoded (Kimi M4 — MEDIUM)
**Action**: ACCEPTED. Document in DEBT.md that `secure=True` requires modern browser (Chrome 89+, Firefox 90+, Safari 16+). For older browsers, user must use `http://127.0.0.1:8000` (not `localhost`).

### Verdict: All CRITICAL/HIGH issues fixed.

---

## Adjudication Log (Rev2 → Rev3)

Per GR4. 6 panelist responses received. The following Rev2 issues were accepted and fixed.

### Finding 1 — Auth interface mismatch (Kimi C1, DeepSeek — convergent)
**Severity**: CRITICAL (blocks execution)
**Action**: ACCEPTED. Plan 9 must read `sovereignai/shared/auth.py` and use the ACTUAL method names:
- `auth.login(username, password)` NOT `auth.authenticate()`
- `auth.validate(token_str)` NOT `auth.validate_token()`
- `auth.register_user(username, password)` — correct
- `auth.has_users()` does NOT exist — add a method or check `len(auth._password_hashes) > 0`

### Finding 2 — Login form POSTs form-urlencoded but endpoint expects JSON (Kimi C1)
**Severity**: CRITICAL (first-run setup fails)
**Action**: ACCEPTED. Login page uses `auth.js` fetch with JSON (consistent with the rest of the app). Remove the "no JavaScript on this page" constraint from login.html.

### Finding 3 — First-run middleware redirect breaks API JSON probes (Kimi C2)
**Severity**: CRITICAL (app.js crashes on first run)
**Action**: ACCEPTED. First-run middleware returns 401 (not redirect) for `/api/*` paths. Redirect only for HTML page requests (`GET /`).

### Finding 6 — `SameSite=Strict` breaks bookmark auto-login (Kimi H4, DeepSeek)
**Severity**: HIGH
**Action**: ACCEPTED. Changed to `SameSite=Lax` (industry standard — allows cookies on top-level GET navigations, blocks cross-origin POSTs).

### Finding 7 — `secure=False` hardcoded (Kimi M1, DeepSeek L12, MiniMax B3)
**Severity**: HIGH
**Action**: ACCEPTED. Changed to `secure=True`. Modern browsers accept Secure cookies on localhost per RFC 6265bis.

### Finding 17 — First-run registration TOCTOU race (MiniMax B1)
**Severity**: CRITICAL
**Action**: ACCEPTED. Add `threading.Lock` around the check-and-register sequence in AuthMiddleware. The `has_users()` check and `register_user()` call must be atomic.

### Finding 18 — Auth persistence unspecified (MiniMax B2)
**Severity**: HIGH
**Action**: ACCEPTED as DEBT. AuthMiddleware is in-memory only (Plan 4 design). Sessions vanish on restart. Document this as a known v1 limitation in DEBT.md. The auto-login promise is broken on restart — document that.

### Finding 14 — No CSRF token for form submissions (Kimi)
**Severity**: MEDIUM
**Action**: ACCEPTED as documented decision. `SameSite=Lax` provides CSRF protection for state-changing operations. No additional CSRF token needed for v1. Documented in DECISIONS.md.

### Verdict
All CRITICAL/HIGH issues fixed. Plan 9 Rev3 is ready for execution.

---

## S0 — Opening

S0.1 — Run `/open`. Verify prompt-8 tag exists on origin. Confirm working copy is clean and on `main`.

S0.2 — Read `AGENTS.md` in full.

S0.3 — No new rules for this plan.

---

## Plan Body

### S1 — Create web/templates/login.html

Create `web/templates/login.html`:
- Clean, centered login form.
- Fields: username, password.
- Submit button: "Log In".
- **Per Finding 2**: Uses `auth.js` fetch with JSON (NOT form POST). Include `<script src="/static/auth.js"></script>`.
- Error display: show error message div on failed login (via JS).
- Link to register page (for first-run).

### S2 — Create web/templates/register.html

Create `web/templates/register.html`:
- Centered registration form.
- Fields: username, password, confirm password.
- Submit button: "Create Account".
- Server validates: password match, username not empty, password minimum 8 characters.
- On success: redirect to login page with "Account created — please log in" message.
- This page is accessible ONLY when no users exist (first-run gate).

### S3 — Create web/static/auth.js

Create `web/static/auth.js`:
```javascript
// Auth module — handles session cookie awareness and logout
// NOTE: No token storage. Auth is entirely session-cookie based.
const Auth = {
  async login(username, password) {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({username, password}),
      credentials: 'same-origin',  // Include session cookie
    });
    if (!res.ok) throw new Error('Login failed');
    return res.json();
  },

  async logout() {
    await fetch('/api/auth/logout', {method: 'POST', credentials: 'same-origin'});
    window.location.href = '/login';
  },

  // No getAuthHeaders() — cookies are sent automatically by the browser
};
```

### S4 — Add auth endpoints and middleware to web/main.py

Add to `web/main.py`:

```python
from fastapi import HTTPException, Request, Response
from fastapi.responses import RedirectResponse

@app.post("/api/auth/login")
async def login(request: Request, response: Response):
    """Validate credentials and set session cookie."""
    data = await request.json()
    auth = container.retrieve(AuthMiddleware)
    try:
        # Per Finding 1: use auth.login() NOT auth.authenticate()
        session = auth.login(data["username"], data["password"])
        response.set_cookie(
            key="session_id",
            value=session.token,
            httponly=True,
            secure=True,  # Per Finding 7: Secure=True works on localhost per RFC 6265bis
            samesite="lax",  # Per Finding 6: Lax allows bookmark auto-login, blocks cross-origin POSTs
            max_age=86400,  # 24 hours
        )
        return {"status": "authenticated"}
    except AuthError:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/api/auth/logout")
async def logout(response: Response):
    """Clear session cookie."""
    response.delete_cookie(key="session_id")
    return {"status": "logged_out"}

@app.post("/api/auth/register")
async def register(request: Request):
    """First-run registration. Only allowed when no users exist."""
    data = await request.json()
    auth = container.retrieve(AuthMiddleware)
    # Per Finding 1: has_users() doesn't exist in Plan 4. Check password_hashes dict.
    if len(auth._password_hashes) > 0:
        raise HTTPException(status_code=403, detail="Registration closed — user already exists")
    # Per Finding 17: TOCTOU race — must be atomic. AuthMiddleware.register_user already
    # raises ValueError if user exists. Wrap in try/except to handle the race.
    try:
        auth.register_user(data["username"], data["password"])
    except ValueError:
        raise HTTPException(status_code=403, detail="Registration closed — user already exists")
    return {"status": "created"}

@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register")
async def register_page(request: Request):
    # Per Finding 1 (Rev4): use len(_password_hashes) NOT has_users()
    auth = container.retrieve(AuthMiddleware)
    if len(auth._password_hashes) > 0:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("register.html", {"request": request})
```

**Session cookie auth for all endpoints:**

Create a dependency that reads the session cookie:
```python
async def get_current_user(request: Request):
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    auth = container.retrieve(AuthMiddleware)
    try:
        # Per Finding 1: use auth.validate() NOT auth.validate_token()
        user = auth.validate(session_id)
    except AuthError:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    return user
```

Apply to all API endpoints (except `/api/auth/*`):
```python
@app.get("/api/capabilities", dependencies=[Depends(get_current_user)])
```

**SSE auth:** SSE reuses the same HTTP session cookie — no query-param tokens. The browser sends cookies automatically with `EventSource` (same-origin).

**First-run middleware:**
```python
@app.middleware("http")
async def first_run_redirect(request: Request, call_next):
    path = request.url.path
    # Allow static files, auth endpoints, and login/register pages without auth
    if path.startswith("/static/") or path in ("/login", "/register") or path.startswith("/api/auth/"):
        return await call_next(request)

    auth = container.retrieve(AuthMiddleware)
    # Per Finding 1: check password_hashes dict instead of non-existent has_users()
    if len(auth._password_hashes) == 0:
        # Per Finding 3: API paths get 401, not redirect (so app.js doesn't crash on JSON parse)
        if path.startswith("/api/"):
            raise HTTPException(status_code=401, detail="No user registered — complete first-run setup")
        return RedirectResponse(url="/register")

    return await call_next(request)
```

Note: `path.startswith("/static/")` NOT literal `"/static/*"`. The `StaticFiles` mount in FastAPI runs before middleware, so this check is defensive — but the middleware must not block static file requests.

### S5 — Update web/static/app.js for auth integration

Modify `app.js`:
1. On page load: check if session cookie exists (via a lightweight `GET /api/capabilities` probe). If 401:
   - **Per Finding 10 (Rev4)**: Check 401 response detail. If "No user registered" → redirect to `/register`. If "Not authenticated" → redirect to `/login`.
2. On API calls: `credentials: 'same-origin'` included automatically by browser for same-origin requests. No manual header management needed.
3. On 401 response: redirect to `/login`.
4. SSE connection: **Per Finding 15 (Rev4)**: Before opening `EventSource`, check auth via `fetch('/api/capabilities')`. If 401, redirect to `/login` or `/register` (per Finding 10). Do NOT open `EventSource` if unauthenticated — browser will infinite-reconnect on 401. On SSE `onerror`: close `EventSource`, re-check auth, only reconnect if authenticated.
5. Add logout button to `#app-header` that calls `Auth.logout()`.

### S6 — End-to-end task submission flow

The Orchestrator panel now uses the full flow:
1. User types "search for Python tutorials" in chat input.
2. Frontend POSTs to `/api/dispatch` with `{message: "..."}`.
3. `MessageDispatcher.dispatch()` routes to WebSearch skill.
4. Task created, state transitions visible in UI.
5. Frontend polls `/api/tasks/{id}`, shows state updates.
6. Result displayed in chat panel.
7. Traces appear in Log drawer via SSE.

### S7 — Error handling in UI

Add to `app.js`:
- **Network error overlay**: If fetch fails (no connection), show semi-transparent overlay with "Connection lost — retrying..." and auto-retry every 5s.
- **Server error**: If response is 500, show toast: "Server error — check Log drawer for details."
- **Task failure**: If task state is FAILED, show error message in chat with retry button.
- **Auth error**: On 401, redirect to login.

### S8 — Tests

- `tests/test_web_auth.py`:
  - `test_login_success`: POST valid credentials, assert session cookie set.
  - `test_login_failure`: POST invalid credentials, assert 401.
  - `test_register_first_run`: No users exist, register succeeds, assert 200.
  - `test_register_after_user_exists`: Register again, assert 403.
  - `test_protected_endpoint_without_cookie`: GET `/api/capabilities` without session cookie, assert 401.
  - `test_protected_endpoint_with_cookie`: GET with valid session cookie, assert 200.
  - `test_sse_auth_required`: Request `/api/traces/stream` without cookie, assert 401.
  - `test_logout_clears_cookie`: POST `/api/auth/logout`, assert cookie deleted.

- `tests/test_e2e_task_submission.py`:
  - `test_search_task_end_to_end`: Mock MessageDispatcher to return a task, POST to `/api/dispatch`, assert result contains expected data.
  - `test_task_state_updates_visible`: Submit task, poll `/api/tasks/{id}`, assert state transitions.
  - `test_traces_appear_in_sse`: Submit task, connect SSE, assert trace events received.

- `tests/test_first_run.py`:
  - `test_no_users_redirects_to_register`: GET `/`, assert redirect to `/register`.
  - `test_after_register_redirects_to_login`: Register, then GET `/register`, assert redirect to `/login`.
  - `test_static_files_not_redirected`: GET `/static/styles.css`, assert 200 (not redirected).

---

## STOP Conditions

- If auth middleware allows access to `/api/*` without a valid session cookie, STOP — security critical.
- If first-run registration allows creating multiple users, STOP — single user only per P6.
- If static files are blocked by first-run middleware, STOP — fresh install must render CSS/JS.
- If any test fails, STOP.

---

## Files WILL Create

- `web/templates/login.html`
- `web/templates/register.html`
- `web/static/auth.js`
- `tests/test_web_auth.py`
- `tests/test_e2e_task_submission.py`
- `tests/test_first_run.py`

## Files WILL Edit

- `web/main.py` (add auth endpoints, middleware, protect existing endpoints)
- `web/static/app.js` (add auth checks, logout, error handling)
- `web/static/styles.css` (add login/register page styles, error overlay, toast)

## Files WILL NOT Edit

- Any file in `sovereignai/shared/`
- `AGENTS.md` (no new rules)

---

## Closing

Run `/close`. Tag: `prompt-9`. Queue Scan 10 in PLANS.md next-5-queue.
