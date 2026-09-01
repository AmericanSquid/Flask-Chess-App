from __future__ import annotations

import secrets
from hmac import compare_digest

from flask import abort, current_app, request, session


CSRF_SESSION_KEY = "_csrf_token"


def ensure_csrf_token() -> str:
    token = session.get(CSRF_SESSION_KEY)
    if token is None:
        token = secrets.token_urlsafe(32)
        session[CSRF_SESSION_KEY] = token
    return token


def extract_csrf_token() -> str | None:
    if request.headers.get("X-CSRFToken"):
        return request.headers["X-CSRFToken"]
    if request.form.get("csrf_token"):
        return request.form["csrf_token"]
    payload = request.get_json(silent=True) or {}
    token = payload.get("csrf_token")
    return token if isinstance(token, str) else None


def validate_csrf_token(token: str | None) -> bool:
    expected = session.get(CSRF_SESSION_KEY)
    if not token or not expected:
        return False
    return compare_digest(token, expected)


def require_csrf() -> None:
    if not current_app.config.get("CSRF_ENABLED", True):
        return
    if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
        if not validate_csrf_token(extract_csrf_token()):
            abort(400, description="Invalid CSRF token")


def install_security(app) -> None:
    @app.context_processor
    def inject_csrf() -> dict[str, object]:
        return {"csrf_token": ensure_csrf_token}
