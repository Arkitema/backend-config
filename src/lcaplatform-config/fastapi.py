from fastapi import Depends, Security

from arkitema_config.security import azure_scheme

try:
    from core.config import settings
except (ImportError, ModuleNotFoundError):
    from arkitema_config import config

    settings = config.Settings()


try:
    from arkitema_config.connection import get_db

    db_url = settings.SQLALCHEMY_DATABASE_URI

    async def get_context(session=Depends(get_db), user=Security(azure_scheme)):
        return {"session": session, "user": user}

except (ImportError, ModuleNotFoundError, AttributeError):

    async def get_context(user=Security(azure_scheme)):
        return {"user": user}
