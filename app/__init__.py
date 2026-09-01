from __future__ import annotations

from pathlib import Path

from flask import Flask, redirect, url_for

from .config import Config
from .extensions import db, login_manager
from .auth.routes import bp as auth_bp
from .games.routes import bp as games_bp
from .leaderboard.routes import bp as leaderboard_bp
from .seed.cli import register_seed_commands
from .utils.security import install_security


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"

    from .models import User

    @login_manager.user_loader
    def load_user(user_id: str) -> User | None:
        if not user_id.isdigit():
            return None
        return db.session.get(User, int(user_id))

    install_security(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(games_bp)
    app.register_blueprint(leaderboard_bp)
    register_seed_commands(app)

    @app.get("/")
    def index():
        return redirect(url_for("games.dashboard"))

    return app
