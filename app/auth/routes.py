from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user

from ..utils.security import require_csrf
from ..users import repository as user_repository
from .service import sign_in_seeded_user, sign_out_current_user


bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.get("/login")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("games.dashboard"))
    users = user_repository.list_seeded_users()
    return render_template("auth/login.html", users=users)


@bp.post("/login")
def login_post():
    require_csrf()
    username = request.form.get("username", "").strip()
    user = sign_in_seeded_user(username)
    if user is None:
        flash("Unknown user selection.", "error")
        return redirect(url_for("auth.login"))
    flash(f"Signed in as {user.get_display_name()}.", "success")
    return redirect(url_for("games.dashboard"))


@bp.post("/logout")
def logout():
    require_csrf()
    if current_user.is_authenticated:
        sign_out_current_user()
    flash("Signed out.", "info")
    return redirect(url_for("auth.login"))
