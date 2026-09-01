from __future__ import annotations

from ..extensions import db
from ..models import Game, Move, User


DEFAULT_USERS = [
    ("matt", "Matt"),
    ("christina", "Christina"),
]


def seed_users(entries: list[tuple[str, str]], replace: bool = False) -> list[User]:
    if replace:
        db.session.query(Move).delete()
        db.session.query(Game).delete()
        db.session.query(User).delete()
        db.session.commit()

    seeded: list[User] = []
    for username, display_name in entries:
        existing = db.session.query(User).filter_by(username=username).one_or_none()
        if existing is not None:
            existing.display_name = display_name
            existing.is_seeded = True
            seeded.append(existing)
            continue
        user = User(username=username, display_name=display_name, is_seeded=True)
        db.session.add(user)
        seeded.append(user)
    db.session.commit()
    return seeded
