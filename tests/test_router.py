import logging
from unittest.mock import AsyncMock, MagicMock

import pytest
from strawberry.types import ExecutionResult

from lcaplatform_config.router import LCAGraphQLRouter


@pytest.fixture
def mock_router(mocker) -> None:
    """Mock out the GraphQLRouter class to isolate the system under test.

    Mock self.__init__ to allow creating an instance.
    Mock self.process_result because only the overridden method on the child class is of interest.
    """

    mocker.patch("strawberry.fastapi.GraphQLRouter.__init__", return_value=None)
    yield mocker.patch("lcaplatform_config.router.GraphQLRouter.process_result")


@pytest.fixture
def mock_response(mocker) -> MagicMock:
    """Mock the strawberry ExecutionResult class as it is not needed for the test."""
    return_dict = {"data": {"test": "test"}, "errors": None, "extensions": None}
    yield ExecutionResult(**return_dict)


@pytest.fixture
def error_response(mocker) -> MagicMock:
    """Mock the strawberry ExecutionResult class as it is not needed for the test."""
    error_mock = mocker.MagicMock()
    error_mock.path = "/path"
    error_mock.message = "error"
    return_dict = {"data": {"test": "test"}, "errors": [error_mock], "extensions": None}
    yield ExecutionResult(**return_dict)


@pytest.fixture
def mock_request_0(mocker) -> MagicMock:
    """Mock out fastapi.Request.json method to return the query dict

    Query does not contain variables.
    """

    query = """
        query {
            tags {
                id
            }
        }
    """
    response = {"query": query, "variables": None}
    json_mock = AsyncMock(return_value=response)
    request_mock = mocker.patch("fastapi.Request")
    request_mock.state.user.preferred_username = "user@mail.com"
    request_mock.json = json_mock
    yield request_mock


@pytest.fixture
def mock_request_1(mocker) -> MagicMock:
    """Mock out fastapi.Request.json method to return the query dict

    Query contains variables.
    """

    query = """query getArkitemaProject($projectId: String!) {
        lcaProject(projectId: $projectId) {
            id
            name
            __typename
        }
    }"""
    response = {"query": query, "variables": {"projectId": "COWI ATR"}}
    json_mock = AsyncMock(return_value=response)
    request_mock = mocker.patch("fastapi.Request")
    request_mock.state.user.preferred_username = "user@mail.com"
    request_mock.json = json_mock
    yield request_mock


@pytest.mark.asyncio
async def test_router_logs_graphql_path_no_variables(
    mock_request_0: MagicMock, mock_response: MagicMock, mock_router: MagicMock, caplog
):
    """Test that the logger outputs the GraphQL path at INFO level when the query contains no variables."""
    with caplog.at_level(logging.INFO):
        await LCAGraphQLRouter().process_result(mock_request_0, mock_response)

    assert (log := [record for record in caplog.records if record.funcName == "process_result"][0])  # noqa: RUF015
    assert log.levelname == "INFO"
    assert log.message == 'User: "user@mail.com", GraphQL path: "tags", vars: "None"'


@pytest.mark.asyncio
async def test_router_logs_graphql_path_with_variables(
    mock_request_1: MagicMock, mock_response: MagicMock, mock_router: MagicMock, caplog
):
    """Test that the logger outputs the GraphQL path at INFO level when the query contains variables."""
    with caplog.at_level(logging.INFO):
        await LCAGraphQLRouter().process_result(mock_request_1, mock_response)

    assert (log := [record for record in caplog.records if record.funcName == "process_result"][0])  # noqa: RUF015
    assert log.levelname == "INFO"
    assert log.message == 'User: "user@mail.com", GraphQL path: "lcaProject", vars: "{\'projectId\': \'COWI ATR\'}"'


@pytest.mark.asyncio
async def test_router_logs_graphql_path_with_error(
    mock_request_1: MagicMock, error_response: MagicMock, mock_router: MagicMock, caplog
):
    """Test that the logger outputs the GraphQL path at INFO level when the query contains variables."""
    with caplog.at_level(logging.INFO):
        await LCAGraphQLRouter().process_result(mock_request_1, error_response)

    assert (log := [record for record in caplog.records if record.funcName == "process_result"][0])  # noqa: RUF015
    assert log.levelname == "ERROR"
    assert (
        log.message
        == 'User: "user@mail.com", GraphQL path: "/path", msg: "error", vars: "{\'projectId\': \'COWI ATR\'}"'
    )
