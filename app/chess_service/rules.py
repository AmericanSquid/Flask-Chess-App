from __future__ import annotations

import chess


def draw_claim_reason(board: chess.Board) -> str | None:
    if board.can_claim_threefold_repetition():
        return "threefold_repetition"
    if board.can_claim_fifty_moves():
        return "fifty_moves"
    return None
