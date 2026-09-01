from __future__ import annotations

from sqlalchemy import and_, or_, select

from ..extensions import db
from ..models import Game
from ..utils.enums import GameStatus


def player_pair_clause(user_a_id: int, user_b_id: int):
    return or_(
        and_(Game.white_id == user_a_id, Game.black_id == user_b_id),
        and_(Game.white_id == user_b_id, Game.black_id == user_a_id),
    )


def get_game(game_id: int) -> Game | None:
    return db.session.get(Game, game_id)


def latest_active_game_between_players(user_a_id: int, user_b_id: int) -> Game | None:
    stmt = (
        select(Game)
        .where(player_pair_clause(user_a_id, user_b_id), Game.status == GameStatus.ACTIVE.value)
        .order_by(Game.updated_at.desc())
    )
    return db.session.scalar(stmt)


def latest_game_for_user(user_id: int) -> Game | None:
    stmt = (
        select(Game)
        .where(or_(Game.white_id == user_id, Game.black_id == user_id))
        .order_by(Game.updated_at.desc())
    )
    return db.session.scalar(stmt)


def latest_active_game_for_user(user_id: int) -> Game | None:
    stmt = (
        select(Game)
        .where(
            or_(Game.white_id == user_id, Game.black_id == user_id),
            Game.status == GameStatus.ACTIVE.value,
        )
        .order_by(Game.updated_at.desc())
    )
    return db.session.scalar(stmt)

def active_games_for_user(user_id: int) -> list[Game]:
    return (
        Game.query
        .filter(
            Game.status == "active",
            or_(
                Game.white_id == user_id,
                Game.black_id == user_id,
            ),
        )
        .order_by(Game.updated_at.desc())
        .all()
    )
