import datetime
import os
from unittest.mock import AsyncMock

import pytest

from arkitema_config import config, user


@pytest.fixture()
def settings_env():
    envs = {
        "SERVER_NAME": "Arkitema Test",
        "SERVER_HOST": "http://api.arktema.com",
        "POSTGRES_HOST": "localhost",
        "POSTGRES_USER": "postgresuser",
        "POSTGRES_PASSWORD": "mypassword",
        "POSTGRES_DB": "arkitema",
        "POSTGRES_PORT": "5632",
        "AAD_APP_CLIENT_ID": "40c35f10-9d17-43dc-bf6c-6208945c98c6",
        "AAD_TENANT_ID": "11be1538-79d8-4939-82b8-b767805d825b",
        "AAD_TEST_CLIENT_SECRET": "RmQ7Q~ejj0xaB566qjekYB6Oivq06Sk4Q69Hw",
        "DEFAULT_AD_FQDN": "cowi.onmicrosoft.com",
        "SENDGRID_SECRET": "c2VjcmV0",
        "EMAIL_NOTIFICATION_FROM": "no-reply@arkitema.com",
        "INTERNAL_EMAIL_DOMAINS_LIST": "arkitema,cowi,cowicloud",
    }
    for key, value in envs.items():
        os.environ[key] = value

    yield envs


@pytest.fixture
async def mock_graph_client(mocker):
    graph_client_mock = mocker.patch(
        "arkitema_config.user.GraphServiceClient",
    )
    graph_client_obj = graph_client_mock.return_value

    return_user = mocker.MagicMock()
    setattr(return_user, "mail", "test@email.com")
    setattr(return_user, "id", "123")
    setattr(return_user, "display_name", "test")
    setattr(return_user, "company_name", "Name")
    sign_in_mock = mocker.MagicMock()
    setattr(return_user, "sign_in_activity", sign_in_mock)
    setattr(sign_in_mock, "last_sign_in_date_time", datetime.date(2000, 5, 5))

    get_mock = AsyncMock()
    get_mock.get = AsyncMock(return_value=return_user)
    graph_client_obj.users.by_user_id.return_value = get_mock

    graph_client_obj.invitations.post = AsyncMock(return_value="RESPONSE")

    graph_client_mock.graph_client_obj = graph_client_obj

    config.Settings()

    yield graph_client_mock

    await user.cache.clear()
