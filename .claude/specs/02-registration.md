# Spec: Registration

## Overview
Wire the existing `/register` form to the database so a visitor can create a Spendly account. The route currently only renders the template. This step adds a POST handler that validates input (including a confirm-password field), hashes the password with werkzeug, inserts a row into `users`, and then sends the new user to the login page. It is the first half of authentication and must exist before login (Step 3) can be built.

## Depends on
- Step 01 — Database setup (`users` table, `get_db()`, `init_db()`).

## Routes
- GET /register - render the registration form - public (already exists, unchanged)
- POST /register - validate the form, create the user, redirect to `/login` on success; re-render the form with an error message on failure - public

## Database changes
No database changes. The existing `users` table (`id`, `name`, `email UNIQUE`, `password_hash`, `created_at`) already covers everything needed; the `UNIQUE` constraint on `email` is the final guard against duplicates.

## Templates
- Create: none
- Modify:
  - `templates/register.html`:
    - change `action="/register"` to `action="{{ url_for('register') }}"`
    - add a "Confirm password" input (`name="confirm_password"`, `type="password"`, `required`) after the password field
    - remove the "Min. 8 characters" placeholder from the password field (no minimum length)
    - re-populate the `name` and `email` inputs with the submitted values after an error (never the passwords)
    - keep the existing `{% if error %}` block

## Files to change
- `app.py` — import `request`, `redirect`, `url_for`, `sqlite3`, `generate_password_hash`; change `@app.route("/register")` to accept `GET` and `POST` and implement the handler.
- `templates/register.html` — as described above.

## Files to create
- `tests/test_registration.py` — pytest tests for the registration flow (uses a temporary database, never `spendly.db`).
- `pytest.ini` — sets `pythonpath = .` so tests can import `app`.

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug (`generate_password_hash`); never store or log the plain password
- Use CSS variables - never hardcode hex values
- All templates extend base.html
- Use `get_db()` from `database/db.py` and always close the connection (`try/finally`)
- Server-side validation, in this order (do not rely on HTML `required`):
  1. name, email, password and confirm_password are all non-empty (name and email are stripped, email lowercased) -> "All fields are required."
  2. password equals confirm_password -> otherwise "Passwords do not match"
  3. email not already in `users` (`SELECT` by email) -> otherwise "Email already registered"
- There is no minimum password length; short passwords such as "1234" are allowed
- Also catch `sqlite3.IntegrityError` on insert as a guard against a race on the `UNIQUE` email, returning the same "Email already registered" error
- On any failure re-render `register.html` with `error`, `name` and `email` set (passwords are never passed back); HTTP status 400 for validation errors, 409 for a duplicate email
- On success redirect to `url_for('login')`; do not log the user in (sessions arrive in the login step)
- `register()` has a single `@app.route` decorator and no unreachable code
- Keep all routes in `app.py`; follow the existing route style

## Definition of done
- [ ] `GET /register` still renders the form, now with a "Confirm password" field
- [ ] Submitting valid name, email, password and matching confirm password creates a row in `users` and redirects to `/login`
- [ ] A short password such as `1234` is accepted
- [ ] The stored `password_hash` is a werkzeug hash, not the plain password
- [ ] Email is stored lowercased and trimmed
- [ ] Mismatched passwords show "Passwords do not match" and create no row
- [ ] Registering `demo@spendly.com` (already seeded) shows "Email already registered" and creates no new row
- [ ] Submitting with any field empty shows "All fields are required." and creates no row
- [ ] After an error, the name and email fields keep their values and the password fields are empty
- [ ] A newly registered user can later be found in `spendly.db` via `SELECT * FROM users`
- [ ] `pytest tests/test_registration.py` passes
