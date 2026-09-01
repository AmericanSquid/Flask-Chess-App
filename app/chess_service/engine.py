from __future__ import annotations

from dataclasses import dataclass

import chess


PROMOTION_MAP = {
    None: None,
    "": None,
    "q": chess.QUEEN,
    "r": chess.ROOK,
    "b": chess.BISHOP,
    "n": chess.KNIGHT,
}


@dataclass(slots=True)
class AppliedMove:
    move: chess.Move
    san: str
    fen_after: str
    is_capture: bool
    is_check: bool
    is_checkmate: bool
    promotion_piece: str | None


def board_from_fen(fen: str) -> chess.Board:
    return chess.Board(fen)


def board_from_game(game) -> chess.Board:
    return board_from_fen(game.current_fen)


def turn_name(board: chess.Board) -> str:
    return "white" if board.turn == chess.WHITE else "black"


def serialize_board(board: chess.Board) -> list[list[dict[str, str | None]]]:
    rows: list[list[dict[str, str | None]]] = []
    for rank in range(8, 0, -1):
        row: list[dict[str, str | None]] = []
        for file_name in "abcdefgh":
            square_name = f"{file_name}{rank}"
            piece = board.piece_at(chess.parse_square(square_name))
            row.append(
                {
                    "square": square_name,
                    "piece": piece.symbol() if piece else None,
                    "color": (
                        "white" if piece and piece.color == chess.WHITE else "black" if piece else None
                    ),
                }
            )
        rows.append(row)
    return rows


def legal_moves_map(board: chess.Board) -> dict[str, list[str]]:
    mapping: dict[str, list[str]] = {}
    for move in board.legal_moves:
        origin = chess.square_name(move.from_square)
        target = chess.square_name(move.to_square)
        mapping.setdefault(origin, []).append(target)
    for targets in mapping.values():
        targets.sort()
    return mapping


def apply_move(
    board: chess.Board,
    from_square: str,
    to_square: str,
    promotion: str | None = None,
) -> AppliedMove:
    move = board.find_move(
        chess.parse_square(from_square),
        chess.parse_square(to_square),
        PROMOTION_MAP.get((promotion or "").lower(), None),
    )
    is_capture = board.is_capture(move)
    san = board.san(move)
    board.push(move)
    return AppliedMove(
        move=move,
        san=san,
        fen_after=board.fen(),
        is_capture=is_capture,
        is_check=board.is_check(),
        is_checkmate=board.is_checkmate(),
        promotion_piece=(promotion or None),
    )
