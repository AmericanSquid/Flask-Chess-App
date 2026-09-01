from __future__ import annotations

import click
from flask import Flask

from ..extensions import db
from ..models import User
from .service import DEFAULT_USERS, seed_users


def register_seed_commands(app: Flask) -> None:
    @app.cli.command("init-db")
    def init_db_command() -> None:
        db.create_all()
        click.echo("Database initialized.")

    @app.cli.command("seed-users")
    @click.argument("entries", nargs=-1)
    @click.option("--replace", is_flag=True, help="Replace existing users before seeding.")
    def seed_users_command(entries: tuple[str, ...], replace: bool) -> None:
        db.create_all()
        parsed = []
        if entries:
            for entry in entries:
                if ":" in entry:
                    username, display_name = entry.split(":", 1)
                else:
                    username, display_name = entry, entry.title()
                parsed.append((username.strip(), display_name.strip()))
        else:
            parsed = DEFAULT_USERS

        users = seed_users(parsed, replace=replace)
        click.echo(f"Seeded {len(users)} users.")

    @app.cli.command("create-user")
    @click.argument("username")
    @click.argument("display_name")
    def create_user_command(username: str, display_name: str) -> None:
        db.create_all()

        existing = User.query.filter_by(username=username).first()
        if existing:
            click.echo(f"User '{username}' already exists.")
            return

        user = User(
            username=username,
            display_name=display_name,
            is_seeded=True,
        )
        db.session.add(user)
        db.session.commit()
        click.echo(f"Created user '{username}'.")
