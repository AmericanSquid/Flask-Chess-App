from __future__ import annotations

from sqlalchemy import or_, select

from ..extensions import db
from ..models import Game, User
from ..utils.enums import GameStatus, ResultCode


def get_leaderboard_rows() -> list[dict[str, object]]:
    users = list(db.session.scalars(select(User).order_by(User.username)).all())
    rows: list[dict[str, object]] = []
    for user in users:
        finished_games = list(
            db.session.scalars(
                select(Game).where(
                    or_(Game.white_id == user.id, Game.black_id == user.id),
                    Game.status == GameStatus.FINISHED.value,
                )
            ).all()
        )
        wins = sum(1 for game in finished_games if game.winner_id == user.id)
        draws = sum(1 for game in finished_games if game.result_code == ResultCode.DRAW.value)
        losses = len(finished_games) - wins - draws
        rows.append(
            {
                "user_id": user.id,
                "username": user.username,
                "display_name": user.get_display_name(),
                "wins": wins,
                "draws": draws,
                "losses": losses,
                "games_played": len(finished_games),
                "score": wins + draws * 0.5,
            }
        )
    rows.sort(key=lambda row: (-row["score"], -row["wins"], row["username"]))
    return rows
