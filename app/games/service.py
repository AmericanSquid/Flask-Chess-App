from __future__ import annotations

from dataclasses import dataclass

import chess

from ..chess_service import apply_move, board_from_game, build_pgn
from ..chess_service.rules import draw_claim_reason
from ..extensions import db
from ..models import Game, Move, User, ChatMessage
from ..models.game import DEFAULT_STARTING_FEN
from ..utils.dates import utcnow
from ..utils.enums import GameStatus, ResultCode
from . import repository

class GameServiceError(Exception):
    error_code = "game_error"
    status_code = 400

    def __init__(self, message: str, **payload):
        super().__init__(message)
        self.message = message
        self.payload = payload


class GameNotFoundError(GameServiceError):
    error_code = "game_not_found"
    status_code = 404


class AccessDeniedError(GameServiceError):
    error_code = "forbidden"
    status_code = 403


class NotYourTurnError(GameServiceError):
    error_code = "not_your_turn"
    status_code = 403


class IllegalMoveError(GameServiceError):
    error_code = "illegal_move"
    status_code = 400


class StaleStateError(GameServiceError):
    error_code = "stale_state"
    status_code = 409


class GameFinishedError(GameServiceError):
    error_code = "game_finished"
    status_code = 409


class DrawNotClaimableError(GameServiceError):
    error_code = "draw_not_claimable"
    status_code = 400


@dataclass(slots=True)
class MoveResult:
    game: Game
    board: chess.Board
    move_row: Move


def ensure_player_in_game(game: Game, user: User) -> None:
    if user.id not in {game.white_id, game.black_id}:
        raise AccessDeniedError("You are not a participant in this game.")


def create_or_reuse_game(current_user: User, opponent: User, preferred_color: str | None = None) -> tuple[Game, bool]:
    existing = repository.latest_active_game_between_players(current_user.id, opponent.id)
    if existing is not None:
        return existing, False

    if preferred_color == "black":
        white_id, black_id = opponent.id, current_user.id
    else:
        white_id, black_id = current_user.id, opponent.id

    game = Game(
        white_id=white_id,
        black_id=black_id,
        starting_fen=DEFAULT_STARTING_FEN,
        current_fen=DEFAULT_STARTING_FEN,
    )
    db.session.add(game)
    db.session.commit()
    return game, True


def current_turn_user_id(game: Game, board: chess.Board) -> int:
    return game.white_id if board.turn == chess.WHITE else game.black_id


def finalize_game_from_board(game: Game, board: chess.Board, claim_draw: bool = False) -> None:
    outcome = board.outcome(claim_draw=claim_draw)
    if outcome is None:
        return

    game.status = GameStatus.FINISHED.value
    game.result_code = outcome.result()
    game.termination = outcome.termination.name.lower()
    game.finished_at = utcnow()

    if outcome.winner is chess.WHITE:
        game.winner_id = game.white_id
    elif outcome.winner is chess.BLACK:
        game.winner_id = game.black_id
    else:
        game.winner_id = None

    ChatMessage.query.filter_by(game_id=game.id).delete()

def apply_move_to_game(
    game: Game,
    player: User,
    from_square: str,
    to_square: str,
    promotion: str | None,
    expected_version: int,
) -> MoveResult:
    ensure_player_in_game(game, player)

    if game.status != GameStatus.ACTIVE.value:
        raise GameFinishedError("This game is already finished.")
    if game.version != expected_version:
        raise StaleStateError("The game has changed on another client.", current_version=game.version)

    board = board_from_game(game)
    if current_turn_user_id(game, board) != player.id:
        raise NotYourTurnError("It is not your turn.")

    try:
        applied = apply_move(board, from_square, to_square, promotion)
    except (ValueError, chess.IllegalMoveError):
        raise IllegalMoveError("Illegal move.") from None

    move_row = Move(
        game_id=game.id,
        player_id=player.id,
        ply=len(game.moves) + 1,
        uci=applied.move.uci(),
        san=applied.san,
        fen_after=applied.fen_after,
        promotion_piece=applied.promotion_piece,
        is_capture=applied.is_capture,
        is_check=applied.is_check,
        is_checkmate=applied.is_checkmate,
    )

    game.current_fen = applied.fen_after
    game.version += 1
    game.updated_at = utcnow()
    game.cached_pgn = None
    finalize_game_from_board(game, board)

    db.session.add(move_row)
    db.session.add(game)
    db.session.commit()

    return MoveResult(game=game, board=board, move_row=move_row)


def claim_draw(game: Game, player: User, expected_version: int) -> Game:
    ensure_player_in_game(game, player)

    if game.status != GameStatus.ACTIVE.value:
        raise GameFinishedError("This game is already finished.")
    if game.version != expected_version:
        raise StaleStateError("The game has changed on another client.", current_version=game.version)

    board = board_from_game(game)
    if current_turn_user_id(game, board) != player.id:
        raise NotYourTurnError("Only the side to move can claim a draw.")
    if not board.can_claim_draw():
        raise DrawNotClaimableError("No claimable draw is currently available.")

    finalize_game_from_board(game, board, claim_draw=True)
    if game.status != GameStatus.FINISHED.value:
        raise DrawNotClaimableError("No claimable draw is currently available.")

    game.version += 1
    game.updated_at = utcnow()
    game.cached_pgn = build_pgn(game.starting_fen, game.moves)
    db.session.add(game)
    db.session.commit()
    return game


def ensure_cached_pgn(game: Game) -> str:
    if game.cached_pgn:
        return game.cached_pgn
    game.cached_pgn = build_pgn(game.starting_fen, game.moves)
    db.session.add(game)
    db.session.commit()
    return game.cached_pgn


def draw_status(game: Game) -> str | None:
    board = board_from_game(game)
    return draw_claim_reason(board)
