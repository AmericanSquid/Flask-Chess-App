# Highly Modular Flask Chess App

A modular Flask chess application scaffold based on your architecture report. It includes:

- Application factory + unbound extensions
- Blueprint-oriented route layout
- Flask-SQLAlchemy models for `User`, `Game`, and `Move`
- `python-chess` service layer for move validation, FEN handling, PGN export, and draw claims
- Server-rendered Jinja templates with small vanilla-JS modules
- Versioned polling for two-player live updates
- SQLite defaults for foreign keys, WAL, and busy timeout
- CLI commands for database initialization and seeding
- Starter pytest coverage

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scriptsctivate
pip install -r requirements.txt

flask --app "app:create_app" init-db
flask --app "app:create_app" seed-users --replace
flask --app "app:create_app" run --debug
```

Then visit `/auth/login`, choose a seeded user, and start a game from the dashboard.

## Seeded users

By default, `seed-users --replace` creates:

- `alice` / Alice
- `bob` / Bob

You can also add named users:

```bash
flask --app "app:create_app" seed-users alice:Alice bob:Bob charlie:"Charlie C."
```

## Production notes

This is a clean MVP scaffold. Before internet-facing deployment, add:

- real password auth
- TLS
- stronger secret key management
- stricter CSP / security headers
- deeper test coverage
- Alembic once the schema begins to churn

## Project layout

```text
app/
  auth/
  chess_service/
  games/
  leaderboard/
  models/
  seed/
  static/
  templates/
  users/
  utils/
tests/
```
