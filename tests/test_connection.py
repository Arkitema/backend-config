from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine


def test_create_postgres_engine(settings_env):
    from arkitema_config.connection import create_postgres_engine

    engine = create_postgres_engine()

    assert engine
    assert isinstance(engine, AsyncEngine)


def test_get_db(settings_env):
    from arkitema_config.connection import get_db

    db = get_db()

    assert db
    assert isinstance(db, AsyncGenerator)
