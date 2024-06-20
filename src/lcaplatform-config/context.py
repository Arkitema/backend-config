from fastapi_azure_auth.user import User
from sqlmodel.ext.asyncio.session import AsyncSession
from strawberry.types import Info


def get_user(info: Info) -> User:
    return info.context.get("user")


def get_session(info: Info) -> AsyncSession:
    return info.context.get("session")


def get_token(info: Info) -> str:
    return info.context.get("user").access_token
