import json
import os

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
    graphClient_mock = mocker.patch(
        "arkitema_config.user.GraphClient",
    )
    graph_obj = graphClient_mock.return_value

    get_response = graph_obj.get.return_value
    get_response.json.return_value = {"id": "123"}

    post_response = graph_obj.post.return_value
    post_response.status_code = 200
    post_response.json.return_value = json.loads(
        """{
            "responses": [
                {
                    "status": 200,
                    "body": {
                        "email": "email@mail.com",
                        "id": "123",
                        "displayName": "test",
                        "companyName": "Name",
                        "signInActivity": {
                            "lastSignInDateTime": "2000-05-05T12:00:00Z"
                        }
                    }
                }
            ]
        }"""
    )

    graphClient_mock.post_response = post_response
    graphClient_mock.graph_obj = graph_obj

    config.Settings()

    yield graphClient_mock

    await user.cache.clear()
