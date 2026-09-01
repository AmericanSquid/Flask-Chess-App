from __future__ import annotations

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from flask_login import UserMixin

from ..extensions import db
from ..utils.dates import utcnow


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(100))
    password_hash: Mapped[str | None] = mapped_column(String(255))
    is_seeded: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    last_seen_at: Mapped[object | None] = mapped_column(DateTime(timezone=True))

    white_games: Mapped[list["Game"]] = relationship(
        "Game",
        foreign_keys="Game.white_id",
        back_populates="white_player",
    )
    black_games: Mapped[list["Game"]] = relationship(
        "Game",
        foreign_keys="Game.black_id",
        back_populates="black_player",
    )
    moves: Mapped[list["Move"]] = relationship("Move", back_populates="player")

    def get_display_name(self) -> str:
        return self.display_name or self.username
