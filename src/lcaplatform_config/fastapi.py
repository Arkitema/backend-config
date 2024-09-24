from fastapi import Depends, Security

from lcaplatform_config.security import azure_scheme

try:
    from core.config import settings
except (ImportError, ModuleNotFoundError):
    from lcaplatform_config import config

    settings = config.Settings()


try:
    from lcaplatform_config.connection import get_db

    async def get_context(session=Depends(get_db), user=Security(azure_scheme)):  # type: ignore
        return {"session": session, "user": user}

except (ImportError, ModuleNotFoundError, AttributeError):

    async def get_context(user=Security(azure_scheme)):  # type: ignore
        return {"user": user}
