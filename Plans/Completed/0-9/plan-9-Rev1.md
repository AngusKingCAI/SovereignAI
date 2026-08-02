Depends on: prompt-8
Vision principles: P6 (login gate), P9 (no silent failures), P13 (strong/robust)
Open questions resolved: none

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
- No JavaScript on this page (form POSTs directly, server redirects on success).
- Error display: server-rendered flash message if login fails.
- Link to register page (for first-run).

### S2 — Create web/templates/register.html

Create `web/templates/register.html`:
- Centered registration form.
- Fields: username, password, confirm password.
- Submit button: "Create Account".
- Server validates: password match, username not empty.
- On success: redirect to login page with "Account created — please log in" message.
- This page is accessible ONLY when no users exist (first-run gate).

### S3 — Create web/static/auth.js

Create `web/static/auth.js`:
```javascript
// Auth module — handles session token storage and API authentication
const Auth = {
  getToken() { return localStorage.getItem('sovereignai_token'); },
  setToken(t) { localStorage.setItem('sovereignai_token', t); },
  clearToken() { localStorage.removeItem('sovereignai_token'); },

  async login(username, password) {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({username, password})
    });
    if (!res.ok) throw new Error('Login failed');
    const data = await res.json();
    this.setToken(data.token);
    return data;
  },

  logout() {
    this.clearToken();
    window.location.href = '/login';
  },

  getAuthHeaders() {
    const token = this.getToken();
    return token ? {'Authorization': `Bearer ${token}`} : {};
  }
};
```

### S4 — Add auth endpoints and middleware to web/main.py

Add to `web/main.py`:

```python
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    auth = container.retrieve(AuthMiddleware)
    token = auth.validate_token(credentials.credentials)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return token

@app.post("/api/auth/login")
async def login(request: Request):
    data = await request.json()
    auth = container.retrieve(AuthMiddleware)
    try:
        token = auth.authenticate(data["username"], data["password"])
        return {"token": token.token, "expires_at": token.expires_at.isoformat()}
    except AuthError:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/api/auth/register")
async def register(request: Request):
    data = await request.json()
    auth = container.retrieve(AuthMiddleware)
    # First-run check: only allow if no users exist
    if auth.has_users():
        raise HTTPException(status_code=403, detail="Registration closed — user already exists")
    auth.register_user(data["username"], data["password"])
    return {"status": "created"}

@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register")
async def register_page(request: Request):
    auth = container.retrieve(AuthMiddleware)
    if auth.has_users():
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("register.html", {"request": request})
```

Protect all existing API endpoints with `Depends(get_current_user)`:
```python
@app.get("/api/capabilities", dependencies=[Depends(get_current_user)])
```

**WebSocket auth**: The WebSocket endpoint reads `?token=` from query params and validates it before accepting the connection. If invalid, close with 1008.

### S5 — Update web/static/app.js for auth integration

Modify `app.js`:
1. On page load: check `Auth.getToken()`. If missing, redirect to `/login`.
2. On API calls: include `Auth.getAuthHeaders()` in fetch options.
3. On 401 response: call `Auth.logout()`.
4. WebSocket connection: append `?token=${Auth.getToken()}` to URL.
5. Add logout button to `#app-header`.

### S6 — First-run flow

In `web/main.py`, add middleware:
```python
@app.middleware("http")
async def first_run_redirect(request: Request, call_next):
    if request.url.path in ("/login", "/register", "/static/*"):
        return await call_next(request)
    auth = container.retrieve(AuthMiddleware)
    if not auth.has_users():
        return RedirectResponse(url="/register")
    return await call_next(request)
```

This ensures:
- Fresh install → all requests redirect to `/register`.
- After registration → `/register` redirects to `/login`.
- After login → normal app access.

### S7 — End-to-end task submission flow

The Orchestrator panel now uses the full flow:
1. User types "search for Python tutorials" in chat input.
2. Frontend POSTs to `/api/orchestrate` with `{message: "..."}`.
3. `Orchestrator.handle_message()` routes to WebSearch skill.
4. Task created, state transitions visible in UI.
5. Result returned and displayed in chat panel.
6. Traces streamed to Log drawer via WebSocket.

### S8 — Error handling in UI

Add to `app.js`:
- **Network error overlay**: If fetch fails (no connection), show semi-transparent overlay with "Connection lost — retrying..." and auto-retry every 5s.
- **Server error**: If response is 500, show toast: "Server error — check Log drawer for details."
- **Task failure**: If task state is FAILED, show error message in chat with retry button.
- **Auth error**: On 401, redirect to login.

### S9 — Tests

- `tests/test_web_auth.py`:
  - `test_login_success`: POST valid credentials, assert token returned.
  - `test_login_failure`: POST invalid credentials, assert 401.
  - `test_register_first_run`: No users exist, register succeeds, assert 200.
  - `test_register_after_user_exists`: Register again, assert 403.
  - `test_protected_endpoint_without_token`: GET `/api/capabilities` without auth, assert 401.
  - `test_protected_endpoint_with_token`: GET with valid token, assert 200.
  - `test_websocket_auth_valid`: Connect with `?token=valid`, assert accepted.
  - `test_websocket_auth_invalid`: Connect with `?token=invalid`, assert 1008 close.

- `tests/test_e2e_task_submission.py`:
  - `test_search_task_end_to_end`: Mock Orchestrator to return search results, POST to `/api/orchestrate`, assert result contains expected data.
  - `test_task_state_updates_visible`: Submit task, poll `/api/tasks/{id}`, assert state transitions.
  - `test_traces_appear_in_websocket`: Submit task, connect WebSocket, assert trace events received.

- `tests/test_first_run.py`:
  - `test_no_users_redirects_to_register`: GET `/`, assert redirect to `/register`.
  - `test_after_register_redirects_to_login`: Register, then GET `/register`, assert redirect to `/login`.

---

## STOP Conditions

- If auth middleware allows access to `/api/*` without a valid token, STOP — security critical.
- If first-run registration allows creating multiple users, STOP — single user only per P6.
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
