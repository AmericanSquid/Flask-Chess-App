from __future__ import annotations

from ..extensions import db
from ..utils.dates import utcnow
from . import repository


def touch_user(username: str):
    user = repository.get_user_by_username(username)
    if user is None:
        return None
    user.last_seen_at = utcnow()
    db.session.add(user)
    db.session.commit()
    return user
