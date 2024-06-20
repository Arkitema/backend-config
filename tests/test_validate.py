import pytest
from pytest_httpx import HTTPXMock

from lcaplatform_config import validate

try:
    from core.config import settings
except (ImportError, ModuleNotFoundError):
    from lcaplatform_config import config

    settings = config.Settings()


@pytest.mark.asyncio
async def test_project_exists(httpx_mock: HTTPXMock):
    mock_data = {
        "data": {
            "projects": [
                {
                    "id": "f8a9e659-ce95-49cf-b45d-5b0a867a4a17",
                }
            ]
        }
    }

    httpx_mock.add_response(url=f"{settings.ROUTER_URL}/graphql", json=mock_data)
    check = await validate.project_exists("f8a9e659-ce95-49cf-b45d-5b0a867a4a17", "mytoken")

    assert check


async def test_project_doesnt_exist(httpx_mock: HTTPXMock):
    mock_data = {"errors": {"errors": "error"}}

    httpx_mock.add_response(url=f"{settings.ROUTER_URL}/graphql", json=mock_data)
    check = await validate.project_exists("badProject", "mytoken")

    assert check is False


async def test_group_exists(httpx_mock: HTTPXMock):
    mock_data = {
        "data": {
            "projectGroups": [
                {
                    "id": "f8a9e659-ce95-49cf-b45d-5b0a867a4a17",
                }
            ]
        }
    }

    httpx_mock.add_response(url=f"{settings.ROUTER_URL}/graphql", json=mock_data)
    check = await validate.group_exists("projectid0", "group1", "mytoken")
    assert check is True


async def test_group_doesnt_exist(httpx_mock: HTTPXMock):
    mock_data = {"errors": {"error": "error"}}

    httpx_mock.add_response(url=f"{settings.ROUTER_URL}/graphql", json=mock_data)
    check = await validate.group_exists("projectId0", "badGroup", "mytoken")

    assert check is False
