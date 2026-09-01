from __future__ import annotations

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db
from ..utils.dates import utcnow
from ..utils.enums import GameStatus, ResultCode


DEFAULT_STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


class Game(db.Model):
    __tablename__ = "games"
    __table_args__ = (
        Index("ix_games_status_updated", "status", "updated_at"),
        Index("ix_games_white_status", "white_id", "status"),
        Index("ix_games_black_status", "black_id", "status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    white_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    black_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    winner_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))

    status: Mapped[str] = mapped_column(String(20), default=GameStatus.ACTIVE.value, nullable=False)
    result_code: Mapped[str] = mapped_column(String(10), default=ResultCode.ONGOING.value, nullable=False)
    termination: Mapped[str | None] = mapped_column(String(50))

    starting_fen: Mapped[str] = mapped_column(Text, default=DEFAULT_STARTING_FEN, nullable=False)
    current_fen: Mapped[str] = mapped_column(Text, default=DEFAULT_STARTING_FEN, nullable=False)
    cached_pgn: Mapped[str | None] = mapped_column(Text)
    version: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[object] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)
    finished_at: Mapped[object | None] = mapped_column(DateTime(timezone=True))

    white_player: Mapped["User"] = relationship(
        "User",
        foreign_keys=[white_id],
        back_populates="white_games",
    )
    black_player: Mapped["User"] = relationship(
        "User",
        foreign_keys=[black_id],
        back_populates="black_games",
    )
    winner: Mapped["User | None"] = relationship("User", foreign_keys=[winner_id])
    moves: Mapped[list["Move"]] = relationship(
        "Move",
        back_populates="game",
        cascade="all, delete-orphan",
        order_by="Move.ply",
    )

    def other_player_id(self, user_id: int) -> int | None:
        if user_id == self.white_id:
            return self.black_id
        if user_id == self.black_id:
            return self.white_id
        return None
