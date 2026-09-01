from __future__ import annotations

from flask import Blueprint, abort, current_app, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ..leaderboard.service import get_leaderboard_rows
from ..users import repository as user_repository
from ..utils.security import require_csrf
from . import repository
from .serializers import serialize_game_state
from .service import (
    AccessDeniedError,
    DrawNotClaimableError,
    GameFinishedError,
    GameServiceError,
    IllegalMoveError,
    NotYourTurnError,
    StaleStateError,
    apply_move_to_game,
    claim_draw,
    create_or_reuse_game,
)
from ..models import ChatMessage
from ..extensions import db
from ..utils.enums import GameStatus

bp = Blueprint("games", __name__)

def _require_game_member(game):
    if current_user.id not in {game.white_id, game.black_id}:
        abort(403)

@bp.get("/dashboard")
@login_required
def dashboard():
    active_games = repository.active_games_for_user(current_user.id)
    opponents = [user for user in user_repository.list_seeded_users() if user.id != current_user.id]
    return render_template(
        "dashboard.html",
        active_games=active_games,
        opponents=opponents,
        leaderboard_rows=get_leaderboard_rows(),
    )


@bp.post("/games")
@login_required
def create_game():
    require_csrf()
    opponent_id = request.form.get("opponent_id", type=int)
    preferred_color = request.form.get("preferred_color") or "white"
    opponent = user_repository.get_user(opponent_id) if opponent_id else None
    if opponent is None:
        abort(400, description="Opponent is required")

    game, _created = create_or_reuse_game(current_user, opponent, preferred_color)
    return redirect(url_for("games.view_game", game_id=game.id))


@bp.get("/games/latest")
@login_required
def latest_game():
    game = repository.latest_active_game_for_user(current_user.id)
    if game is None:
        return redirect(url_for("games.dashboard"))
    return redirect(url_for("games.view_game", game_id=game.id))


@bp.get("/games/<int:game_id>")
@login_required
def view_game(game_id: int):
    game = repository.get_game(game_id)
    if game is None:
        abort(404)
    if current_user.id not in {game.white_id, game.black_id}:
        abort(403)
    state = serialize_game_state(game, current_user)
    return render_template(
        "games/game.html",
        game=game,
        initial_state=state,
        poll_interval_ms=current_app.config["POLL_INTERVAL_MS"],
    )


@bp.get("/games/<int:game_id>/state")
@login_required
def game_state(game_id: int):
    game = repository.get_game(game_id)
    if game is None:
        abort(404)
    if current_user.id not in {game.white_id, game.black_id}:
        abort(403)

    since_version = request.args.get("since_version", type=int)
    if since_version is not None and since_version == game.version:
        return jsonify({"changed": False, "version": game.version})

    state = serialize_game_state(game, current_user)
    leaderboard_html = render_template(
        "partials/leaderboard.html",
        leaderboard_rows=state["leaderboard"],
    )
    return jsonify({"changed": True, "state": state, "leaderboard_html": leaderboard_html})


@bp.post("/games/<int:game_id>/moves")
@login_required
def submit_move(game_id: int):
    require_csrf()
    game = repository.get_game(game_id)
    if game is None:
        abort(404)
    payload = request.get_json(silent=True) or {}

    try:
        expected_version = int(payload["expected_version"])
        result = apply_move_to_game(
            game=game,
            player=current_user,
            from_square=str(payload["from"]),
            to_square=str(payload["to"]),
            promotion=payload.get("promotion"),
            expected_version=expected_version,
        )
    except (KeyError, TypeError, ValueError):
        return jsonify({"error": "invalid_payload"}), 400
    except GameServiceError as exc:
        body = {"error": exc.error_code, "message": exc.message, **exc.payload}
        return jsonify(body), exc.status_code

    state = serialize_game_state(result.game, current_user)
    leaderboard_html = render_template(
        "partials/leaderboard.html",
        leaderboard_rows=state["leaderboard"],
    )
    return jsonify({"ok": True, "state": state, "leaderboard_html": leaderboard_html}), 201


@bp.post("/games/<int:game_id>/claim-draw")
@login_required
def claim_draw_route(game_id: int):
    require_csrf()
    game = repository.get_game(game_id)
    if game is None:
        abort(404)
    payload = request.get_json(silent=True) or {}
    try:
        expected_version = int(payload["expected_version"])
        game = claim_draw(game, current_user, expected_version)
    except (KeyError, TypeError, ValueError):
        return jsonify({"error": "invalid_payload"}), 400
    except GameServiceError as exc:
        body = {"error": exc.error_code, "message": exc.message, **exc.payload}
        return jsonify(body), exc.status_code

    state = serialize_game_state(game, current_user)
    leaderboard_html = render_template(
        "partials/leaderboard.html",
        leaderboard_rows=state["leaderboard"],
    )
    return jsonify({"ok": True, "state": state, "leaderboard_html": leaderboard_html}), 200

@bp.post("/games/<int:game_id>/chat")
@login_required
def post_chat_message(game_id: int):
    require_csrf()
    game = repository.get_game(game_id)
    if game is None:
        abort(404)

    _require_game_member(game)

    if game.status != GameStatus.ACTIVE.value:
        return jsonify({
            "error": "game_finished",
            "message": "Chat is closed because the game has finished.",
        }), 409

    data = request.get_json(silent=True) or {}
    body = str(data.get("body") or "").strip()

    if not body:
        return jsonify({"error": "empty", "message": "Message cannot be empty."}), 400

    if len(body) > 500:
        return jsonify({
            "error": "too_long",
            "message": "Message must be 500 characters or fewer.",
        }), 400

    msg = ChatMessage(
        game_id=game.id,
        user_id=current_user.id,
        body=body,
    )

    db.session.add(msg)
    db.session.commit()

    return jsonify({
        "id": msg.id,
        "user_id": msg.user_id,
        "display_name": current_user.get_display_name(),
        "body": msg.body,
        "created_at": msg.created_at.isoformat(),
    }), 201
@bp.get("/games/<int:game_id>/chat")
@login_required
def get_chat_messages(game_id: int):
    game = repository.get_game(game_id)
    if game is None:
        abort(404)

    _require_game_member(game)

    since_id = request.args.get("since_id", type=int)
    query = ChatMessage.query.filter_by(game_id=game.id).order_by(ChatMessage.id.asc())

    if since_id:
        query = query.filter(ChatMessage.id > since_id)

    messages = query.limit(100).all()
    return jsonify({
        "messages": [
            {
                "id": message.id,
                "user_id": message.user_id,
                "display_name": message.user.get_display_name(),
                "body": message.body,
                "created_at": message.created_at.isoformat(),
            }
            for message in messages
        ]
    })

