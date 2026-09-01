from __future__ import annotations

from flask import Blueprint, jsonify, render_template, request
from flask_login import login_required

from .service import get_leaderboard_rows


bp = Blueprint("leaderboard", __name__, url_prefix="/leaderboard")


@bp.get("")
@login_required
def leaderboard_index():
    rows = get_leaderboard_rows()
    wants_json = request.args.get("format") == "json" or request.accept_mimetypes.best == "application/json"
    if wants_json:
        return jsonify({"leaderboard": rows})
    return render_template("partials/leaderboard.html", leaderboard_rows=rows)
