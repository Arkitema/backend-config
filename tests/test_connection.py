from typing import AsyncGenerator

import pytest
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncEngine


@pytest.mark.parametrize("as_async", [True, False])
def test_create_postgres_engine(settings_env, as_async):
    from arkitema_config.connection import create_postgres_engine

    engine = create_postgres_engine(as_async=as_async)

    assert engine
    if as_async:
        assert isinstance(engine, AsyncEngine)
    else:
        assert isinstance(engine, Engine)


def test_get_db(settings_env):
    from arkitema_config.connection import get_db

    db = get_db()

    assert db
    assert isinstance(db, AsyncGenerator)
