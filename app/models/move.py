from __future__ import annotations

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db
from ..utils.dates import utcnow


class Move(db.Model):
    __tablename__ = "moves"
    __table_args__ = (
        UniqueConstraint("game_id", "ply", name="uq_moves_game_ply"),
        Index("ix_moves_game_created", "game_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"), nullable=False, index=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    ply: Mapped[int] = mapped_column(Integer, nullable=False)

    uci: Mapped[str] = mapped_column(String(8), nullable=False)
    san: Mapped[str] = mapped_column(String(32), nullable=False)
    fen_after: Mapped[str] = mapped_column(Text, nullable=False)
    promotion_piece: Mapped[str | None] = mapped_column(String(1))
    is_capture: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_check: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_checkmate: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    game: Mapped["Game"] = relationship("Game", back_populates="moves")
    player: Mapped["User"] = relationship("User", back_populates="moves")
