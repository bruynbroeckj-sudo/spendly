# Spec: Login and Logout

## Overview
Let registered users sign in and out of Spendly. `POST /login` checks the submitted email and password against the `users` table and, on success, stores the user's id and name in the Flask session and redirects to `/` (the landing page). `/logout` clears the session and returns to the landing page. The navbar switches between "Sign in / Get started" and "Hi, <name> / Sign out" depending on session state. This is the second half of authentication, built on Step 02 (registration), and every later logged-in feature (profile, expenses) depends on it.

## Depends on
- Step 01 — Database setup (`users` table, `get_db()`).
- Step 02 — Registration (users can be created with werkzeug-hashed passwords).

## Routes
- `GET /login` - render the sign-in form; if already logged in, redirect to `/` - public (already exists)
- `POST /login` - validate credentials, start the session, redirect to `/`; on failure re-render the form with an error - public
- `GET /logout` - clear the session and redirect to `/` - public (safe to call when not logged in). Replaces the current "Logout — coming in Step 3" placeholder.
- `GET /register` - if already logged in, redirect to `/` (small change to the existing route) - public

`/profile` stays a placeholder until Step 4 and is not used as a redirect target in this step.

## Database changes
No database changes. The existing `users` table (`id`, `name`, `email UNIQUE`, `password_hash`, `created_at`) is sufficient; verified against `database/db.py`.

## Templates
- **Create:** none
- **Modify:**
  - `templates/login.html` — change `action="/login"` to `action="{{ url_for('login') }}"`; re-populate the email input with the submitted value after an error (never the password).
  - `templates/base.html` — in the navbar, when `session.user_id` is set show the user's name and a "Sign out" link to `url_for('logout')`; otherwise keep the existing "Sign in" and "Get started" links.

## Files to change
- `app.py` — set `app.secret_key`; import `session` (and `check_password_hash`); make `/login` accept GET and POST and implement the handler; implement `/logout`; redirect logged-in users away from `/login` and `/register`.
- `templates/login.html` — as above.
- `templates/base.html` — as above.

## Files to create
- `tests/test_login_logout.py` — pytest tests for login and logout (temporary database, never `spendly.db`).

## New dependencies
No new dependencies. Sessions use Flask's built-in signed cookie session.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug; verify with `check_password_hash`, never compare plain text, never log or echo the password
- Use CSS variables - never hardcode hex values
- All templates extend `base.html`
- Use `get_db()` from `database/db.py` and always close the connection (`try/finally`)
- Secret key: read from the `SECRET_KEY` environment variable, falling back to a clearly labelled development-only default so the dev server still starts; do not commit a real secret
- Normalise the submitted email (strip, lowercase) before lookup, matching registration
- Validation, in order: email and password non-empty -> "All fields are required."; no matching user or wrong password -> the same generic "Invalid email or password" message (do not reveal which was wrong)
- On failure re-render `login.html` with `error` and `email` set, HTTP status 400 for missing fields and 401 for bad credentials
- On success: `session.clear()` then set `session["user_id"]` and `session["user_name"]`; redirect to `url_for('landing')`
- Logout: `session.clear()` then redirect to `url_for('landing')`
- Do not add a "remember me" or password-reset flow; out of scope
- Keep all routes in `app.py`; follow the existing route style

## Definition of done
- [ ] `GET /login` renders the form; the form posts back to `/login`
- [ ] Logging in as `demo@spendly.com` / `demo123` redirects to `/`
- [ ] A user registered via `/register` can log in with the same email and password
- [ ] Email matching is case-insensitive and ignores surrounding whitespace
- [ ] A wrong password and an unknown email both show "Invalid email or password" and do not start a session
- [ ] Submitting with an empty field shows "All fields are required."
- [ ] After a failed login the email field keeps its value and the password field is empty
- [ ] While logged in, the navbar shows the user's name and "Sign out" instead of "Sign in" and "Get started"
- [ ] While logged in, visiting `/login` or `/register` redirects to `/`
- [ ] Clicking "Sign out" clears the session, redirects to `/`, and the navbar shows "Sign in" again
- [ ] Visiting `/logout` while logged out does not error and redirects to `/`
- [ ] `pytest tests/test_login_logout.py` passes
