from __future__ import annotations

from datetime import datetime, UTC
from sqlalchemy import ForeignKey, Integer, Text, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db


def utcnow() -> datetime:
    return datetime.now(UTC)


class ChatMessage(db.Model):
    __tablename__ = "chat_messages"
    __table_args__ = (
        Index("ix_chat_messages_game_created", "game_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)

    body: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    game = relationship("Game", backref="chat_messages")
    user = relationship("User")
