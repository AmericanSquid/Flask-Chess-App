from app.extensions import db
from app.models import Game
from app.models.game import DEFAULT_STARTING_FEN
from app.leaderboard.service import get_leaderboard_rows
from app.utils.enums import GameStatus, ResultCode


def test_leaderboard_counts_finished_games(app):
    with app.app_context():
        game = Game(
            white_id=1,
            black_id=2,
            winner_id=1,
            status=GameStatus.FINISHED.value,
            result_code=ResultCode.WHITE_WIN.value,
            starting_fen=DEFAULT_STARTING_FEN,
            current_fen=DEFAULT_STARTING_FEN,
        )
        db.session.add(game)
        db.session.commit()

        rows = get_leaderboard_rows()
        assert rows[0]["wins"] == 1
