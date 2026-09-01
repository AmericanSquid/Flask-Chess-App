from __future__ import annotations

import chess
import chess.pgn


DEFAULT_STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


def build_pgn(starting_fen: str, moves) -> str:
    game = chess.pgn.Game()
    if starting_fen != DEFAULT_STARTING_FEN:
        initial_board = chess.Board(starting_fen)
        game.setup(initial_board)
        game.headers["SetUp"] = "1"
        game.headers["FEN"] = starting_fen

    node = game
    for move_row in moves:
        node = node.add_variation(chess.Move.from_uci(move_row.uci))

    exporter = chess.pgn.StringExporter(headers=True, variations=False, comments=False)
    return game.accept(exporter)
