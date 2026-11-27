# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

"Spendly" — a Flask expense-tracker web app built as a step-by-step teaching scaffold. Many pieces are intentionally stubs labelled "Step N" (placeholder routes in `app.py`). Implement them when asked rather than assuming they exist.

## Commands

Uses the local `venv/` (git-ignored).

```
source venv/bin/activate
pip install -r requirements.txt
python app.py            # dev server, debug mode, http://localhost:5001
pytest                   # tests (pytest + pytest-flask); no tests exist yet
pytest path/to/test_file.py::test_name   # single test
```

No linter or build step is configured.

## Architecture

- `app.py` — single Flask module holding every route. Real routes (`/`, `/register`, `/login`, `/terms`, `/privacy`) only render templates; the register/login forms are not wired to the database yet. Placeholder routes (`/logout`, `/profile`, `/expenses/add`, `/expenses/<id>/edit`, `/expenses/<id>/delete`) return strings and are marked for later steps.
- `database/db.py` — SQLite data layer: `get_db()` (connection to `spendly.db` in the project root, with `sqlite3.Row` row factory and foreign keys enabled), `init_db()` (creates the `users` and `expenses` tables with `CREATE TABLE IF NOT EXISTS`), `seed_db()` (inserts a demo user `demo@spendly.com` / `demo123` and 8 sample expenses, skipped if users already exist) and the fixed `CATEGORIES` list. `app.py` calls `init_db()` and `seed_db()` at startup. The SQLite file `spendly.db` is git-ignored; delete it to reseed.
- `templates/` — Jinja templates extending `base.html` (navbar, footer, `title`/`head`/`content` blocks). Use `url_for('<function name>')` for links, so route function names (e.g. `landing`, `login`, `register`) are referenced from templates.
- `static/css/style.css` — single stylesheet; fonts are DM Serif Display / DM Sans from Google Fonts. `static/js/main.js` is essentially empty; landing-page behaviour (e.g. the YouTube modal) is handled in the templates.

## Conventions

Commit messages follow a `landing: <change>` style prefix for landing-page work.
