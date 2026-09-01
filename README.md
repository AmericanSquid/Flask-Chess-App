# The Court of Crowns & Castles

A small, server-rendered Flask chess application for two-player games. It uses
`python-chess` for rules and move validation, Flask-SQLAlchemy for persistence,
and vanilla JavaScript for the interactive board, polling, and in-game chat.

## What it includes

- Flask application factory with blueprints for authentication, games, and the leaderboard
- SQLite by default, with SQLAlchemy support for another database URL
- Seeded-user sign-in for local/demo sessions (there is no password flow yet)
- Head-to-head games with selectable white/black color and active-game reuse
- Legal move validation, promotion, check/checkmate, FEN state, move history, and PGN generation
- Threefold-repetition and fifty-move draw claims
- Versioned polling to keep two players' boards synchronized
- Per-game chat while a game is active (messages are limited to 500 characters)
- Leaderboard with wins, draws, losses, games played, and score
- CSRF protection for state-changing form and JSON requests
- Pytest coverage for the core chess, route, seed, and leaderboard behavior

## Requirements

- Python 3.11 or newer
- `pip`

## Quick start

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate       # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt

flask --app "app:create_app" init-db
flask --app "app:create_app" seed-users --replace
flask --app "app:create_app" run --debug
```

Open <http://127.0.0.1:5000/auth/login>. Choose a seeded user, start a game
against another seeded user, and open the game page. The root URL (`/`) redirects
to the dashboard.

Run the test suite with:

```bash
pytest
```

## Users and local sign-in

With no arguments, `seed-users` creates or updates these demo users:

| Username | Display name |
| --- | --- |
| `matt` | Matt |
| `christina` | Christina |

The login page lets you select one of these users; it does not ask for a
password. To replace the existing users and related games:

```bash
flask --app "app:create_app" seed-users --replace
```

To seed a custom set without replacing existing records, use `username:Display
Name` arguments:

```bash
flask --app "app:create_app" seed-users alice:Alice bob:Bob "charlie:Charlie C."
```

To add one user without replacing anything:

```bash
flask --app "app:create_app" create-user alice "Alice Example"
```

## Configuration

The application reads these environment variables:

| Variable | Default | Purpose |
| --- | --- | --- |
| `SECRET_KEY` | `dev-secret-change-me` | Flask session signing key; set a strong value outside local development |
| `DATABASE_URL` | `sqlite:///instance/chess.sqlite3` | SQLAlchemy database URL |
| `FLASK_ENV` | unset | When set to `production`, marks session and remember cookies as secure |

The `instance/` directory is created automatically. The default SQLite database
is `instance/chess.sqlite3`, and the directory/database are intentionally not
created until the app is initialized or a seed command runs.

## Main routes

All dashboard, game, and leaderboard routes require a signed-in user.

| Route | Method | Purpose |
| --- | --- | --- |
| `/auth/login` | GET/POST | Display seeded users and sign in |
| `/auth/logout` | POST | Sign out |
| `/dashboard` | GET | Show active games and the leaderboard |
| `/games` | POST | Create or reuse a game against another user |
| `/games/<id>` | GET | Render a game page |
| `/games/<id>/state` | GET | Return current game state; supports `since_version` polling |
| `/games/<id>/moves` | POST | Submit a move using `from`, `to`, and `expected_version` JSON fields |
| `/games/<id>/claim-draw` | POST | Claim an available draw using `expected_version` |
| `/games/<id>/chat` | GET/POST | Read or post active-game chat messages |
| `/leaderboard` | GET | Render standings, or return JSON with `?format=json` |

State-changing requests require the CSRF token supplied in the page, form data,
JSON payload, or `X-CSRFToken` header.

## Project layout

```text
app/
  __init__.py          application factory and route registration
  auth/                seeded-user login and logout
  chess_service/       chess rules, board state, and PGN helpers
  games/               game routes, persistence, serialization, and service logic
  leaderboard/         leaderboard route and calculations
  models/              User, Game, Move, and ChatMessage models
  seed/                Flask CLI commands and seed logic
  static/               CSS and browser JavaScript modules
  templates/            server-rendered Jinja templates
  users/               user persistence helpers
  utils/               security, dates, and enum helpers
tests/                 pytest suite
```

## Deployment notes

This is an MVP/demo scaffold, not a production-ready chess service. Before
exposing it to the internet, add real authentication and account management,
provide a strong secret through the environment, use HTTPS, configure a
production WSGI server and database, add migrations, and review security
headers/CSP, rate limiting, validation, observability, and concurrency handling.

## License

This project is licensed under the GNU General Public License, version 3 or
later. See [LICENSE](LICENSE) for the full license text.
