# Plan 17.4 — Fix Register Page Redirect + Autocomplete Attributes

**Hotfix**: Two small UI fixes. Round Table vetoed.

Depends on: prompt-17.3

---

## S0 — Opening

**S0.1** — Run `/open`. Verify `prompt-17.3` tag on origin. Clean working copy on `main`.

**S0.2** — Read `AGENTS.md` in full. Read `close.md` in full (per OR71).

**S0.3** — No new rules. Proceed to S1.

---

## S1 — Fix /register page redirect

**File**: `web/main.py`

The `/register` route redirects to `/login` when users already exist, making the "Create an account" link on the login page appear broken. Remove the redirect — users should be able to create additional accounts.

**Find**:
```python
@app.get("/register")
async def register_page(request: Request) -> Response:
    """Render the registration page. Only accessible when no users exist."""
    container: Any = request.app.state.container
    auth: Any = container.retrieve(AuthMiddleware)
    if len(auth._password_hashes) > 0:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(request, "register.html")
```

**Replace with**:
```python
@app.get("/register")
async def register_page(request: Request) -> Response:
    """Render the registration page."""
    return templates.TemplateResponse(request, "register.html")
```

---

## S2 — Add autocomplete attributes to all input fields

### S2.1 — login.html

**File**: `web/templates/login.html`

**Find**:
```html
<input type="text" id="username" name="username" required>
```
**Replace with**:
```html
<input type="text" id="username" name="username" autocomplete="username" required>
```

**Find**:
```html
<input type="password" id="password" name="password" required>
```
**Replace with**:
```html
<input type="password" id="password" name="password" autocomplete="current-password" required>
```

### S2.2 — register.html

**File**: `web/templates/register.html`

**Find**:
```html
<input type="text" id="username" name="username" required>
```
**Replace with**:
```html
<input type="text" id="username" name="username" autocomplete="username" required>
```

**Find**:
```html
<input type="password" id="password" name="password" required minlength="8">
```
**Replace with**:
```html
<input type="password" id="password" name="password" autocomplete="new-password" required minlength="8">
```

**Find**:
```html
<input type="password" id="confirm-password" name="confirm-password" required minlength="8">
```
**Replace with**:
```html
<input type="password" id="confirm-password" name="confirm-password" autocomplete="new-password" required minlength="8">
```

---

## S3 — Run /close (ALL 22 steps per OR96)

Run the full `/close` workflow. Do NOT skip any steps. Do NOT commit with known failures. Do NOT tag until all steps pass.

---

## Files WILL Edit
- `web/main.py` (S1 — remove register redirect)
- `web/templates/login.html` (S2.1 — autocomplete attributes)
- `web/templates/register.html` (S2.2 — autocomplete attributes)

## Files WILL NOT Edit
- Any other file

---

## Closing

Run `/close`. Tag: `prompt-17.4`. Per OR83, use `git add -A`. Per OR71, re-read `close.md` fresh. Per OR96, complete ALL 22 steps.
