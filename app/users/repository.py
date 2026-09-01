from __future__ import annotations

from sqlalchemy import select

from ..extensions import db
from ..models import User


def list_users() -> list[User]:
    return list(db.session.scalars(select(User).order_by(User.username)).all())


def list_seeded_users() -> list[User]:
    stmt = select(User).where(User.is_seeded.is_(True)).order_by(User.username)
    return list(db.session.scalars(stmt).all())


def get_user(user_id: int) -> User | None:
    return db.session.get(User, user_id)


def get_user_by_username(username: str) -> User | None:
    stmt = select(User).where(User.username == username)
    return db.session.scalar(stmt)
