from asyncio import current_task
from typing import AsyncGenerator

from pydantic import PostgresDsn
from sqlalchemy.ext.asyncio import async_scoped_session, async_sessionmaker, create_async_engine
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
    local_session = async_sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=create_postgres_engine(),
        class_=AsyncSession,
        expire_on_commit=False,
    )
    scoped_session = async_scoped_session(local_session, scopefunc=current_task)
    async with scoped_session() as session:
        try:
            yield session
        except Exception as e:
            session.rollback()
            raise e
        finally:
            await session.close()
