from __future__ import annotations

from ..chess_service import board_from_game, legal_moves_map, serialize_board, turn_name
from ..chess_service.rules import draw_claim_reason
from ..leaderboard.service import get_leaderboard_rows
from ..utils.enums import GameStatus


def serialize_moves(game) -> list[dict[str, object]]:
    return [
        {
            "ply": move.ply,
            "move_number": (move.ply + 1) // 2,
            "side": "white" if move.ply % 2 else "black",
            "san": move.san,
            "uci": move.uci,
        }
        for move in game.moves
    ]


def serialize_game_state(game, viewer) -> dict[str, object]:
    board = board_from_game(game)
    viewer_color = (
        "white" if viewer.id == game.white_id else "black" if viewer.id == game.black_id else None
    )
    your_turn = (
        game.status == GameStatus.ACTIVE.value
        and viewer_color is not None
        and turn_name(board) == viewer_color
    )

    return {
        "game_id": game.id,
        "version": game.version,
        "status": game.status,
        "result_code": game.result_code,
        "termination": game.termination,
        "fen": game.current_fen,
        "turn": turn_name(board),
        "board": serialize_board(board),
        "player_color": viewer_color,
        "orientation": viewer_color or "white",
        "your_turn": your_turn,
        "can_claim_draw": board.can_claim_draw(),
        "draw_claim_reason": draw_claim_reason(board),
        "legal_moves": legal_moves_map(board) if your_turn else {},
        "moves": serialize_moves(game),
        "players": {
            "white": game.white_player.get_display_name(),
            "black": game.black_player.get_display_name(),
        },
        "leaderboard": get_leaderboard_rows(),
    }
