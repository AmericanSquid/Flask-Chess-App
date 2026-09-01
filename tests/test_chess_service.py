import chess

from app.chess_service.engine import apply_move, board_from_fen


def test_apply_move_advances_position():
    board = board_from_fen(chess.STARTING_FEN)
    result = apply_move(board, "e2", "e4")
    assert result.san == "e4"
    assert board.fen() == result.fen_after
    assert len(board.move_stack) == 1
