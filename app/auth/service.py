from __future__ import annotations

from flask_login import login_user, logout_user

from ..extensions import db
from ..utils.dates import utcnow
from ..users import repository as user_repository


def sign_in_seeded_user(username: str):
    user = user_repository.get_user_by_username(username)
    if user is None:
        return None
    user.last_seen_at = utcnow()
    db.session.add(user)
    db.session.commit()
    login_user(user, remember=False)
    return user


def sign_out_current_user() -> None:
    logout_user()
