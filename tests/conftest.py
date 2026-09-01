from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from app import create_app
from app.extensions import db
from app.models import User
from app.seed.service import seed_users


@pytest.fixture()
def app():
    with tempfile.TemporaryDirectory() as tmpdir:
        database_path = Path(tmpdir) / "test.sqlite3"
        app = create_app(
            {
                "TESTING": True,
                "CSRF_ENABLED": False,
                "SQLALCHEMY_DATABASE_URI": f"sqlite:///{database_path}",
            }
        )
        with app.app_context():
            db.create_all()
            seed_users([("alice", "Alice"), ("bob", "Bob")], replace=True)
            yield app
            db.session.remove()
            db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


def login_as(client, username: str):
    return client.post("/auth/login", data={"username": username}, follow_redirects=True)
