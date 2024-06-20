from typing import AsyncGenerator

from pydantic import PostgresDsn
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import create_engine
from sqlmodel.ext.asyncio.session import AsyncSession

try:
    from core.config import settings
except (ImportError, ModuleNotFoundError):
    from lcaplatform_config import config

    settings = config.Settings()


def create_postgres_engine(as_async=True):
    if as_async:
        return create_async_engine(
            str(settings.SQLALCHEMY_DATABASE_URI),
            pool_pre_ping=True,
            future=True,
            pool_size=settings.POSTGRES_POOL_SIZE,
            max_overflow=settings.POSTGRES_MAX_OVERFLOW,
            connect_args={"ssl": settings.POSTGRES_SSL},
        )
    else:
        return create_engine(
            str(
                PostgresDsn.build(
                    scheme="postgresql",
                    username=settings.POSTGRES_USER,
                    password=settings.POSTGRES_PASSWORD,
                    host=settings.POSTGRES_HOST,
                    path=settings.POSTGRES_DB,
                    port=int(settings.POSTGRES_PORT) if settings.POSTGRES_PORT else None,
                )
            ),
            pool_pre_ping=True,
        )


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    local_session = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=create_postgres_engine(),
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with local_session() as session:
        yield session
