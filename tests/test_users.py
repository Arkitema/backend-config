import datetime

import pytest

from arkitema_config import exceptions, user


@pytest.mark.asyncio
async def test_get_aad_user_by_email(mock_graph_client):
    result = await user.get_aad_user_by_email("test@email.com")
    assert result.id == "123"
    assert (await user.cache.get("test@email.com", namespace="azure_emails")).id == "123"

    assert len(mock_graph_client.mock_calls) == 3
    # GraphServiceClient(...)
    assert mock_graph_client.call_count == 1
    assert mock_graph_client.mock_calls[0][2]["scopes"] == ["https://graph.microsoft.com/.default"]
    # graph.users.by_user_id(...)
    assert mock_graph_client.mock_calls[1][1][0] == "test@email.com"
    # graph.users.by_user_id(...).get()
    assert mock_graph_client.mock_calls[2][1] == ()


@pytest.mark.asyncio
async def test_get_aad_user_by_email_with_cache(mock_graph_client):
    assert await user.cache.add("test@email.com", {"id": "1234"}, namespace="azure_emails")

    result = await user.get_aad_user_by_email("test@email.com")

    assert result == {"id": "1234"}
    assert await user.cache.get("test@email.com", namespace="azure_emails") == {"id": "1234"}

    assert mock_graph_client.call_count == 0
    assert mock_graph_client.mock_calls == []


@pytest.mark.asyncio
async def test_invite_user_to_add(mock_graph_client):
    result = await user.invite_user_to_aad("test@email.com", "platform", "https://lca-platform.com/")
    assert result == "RESPONSE"

    assert len(mock_graph_client.mock_calls) == 2
    # GraphServiceClient(...)
    assert mock_graph_client.call_count == 1
    assert mock_graph_client.mock_calls[0][2]["scopes"] == ["https://graph.microsoft.com/.default"]
    # graph.invitations.post(....)
    assert len(mock_graph_client.mock_calls[1][1]) == 1
    assert mock_graph_client.mock_calls[1][1][0].invited_user_email_address == "test@email.com"


@pytest.mark.asyncio
async def test_get_users_from_azure(mock_graph_client):
    result = await user.get_users_from_azure("123")
    assert result == [
        {
            "user_id": "123",
            "name": "test",
            "email": "test@email.com",
            "company": "Name",
            "last_login": datetime.date(2000, 5, 5),
        }
    ]

    assert len(mock_graph_client.mock_calls) == 3
    # GraphServiceClient(...)
    assert mock_graph_client.call_count == 1
    assert mock_graph_client.mock_calls[0][2]["scopes"] == ["https://graph.microsoft.com/.default"]
    # graph.users.by_user_id(...)
    assert mock_graph_client.mock_calls[1][1][0] == "123"
    # graph.users.by_user_id(...).get()
    assert mock_graph_client.mock_calls[2][1] == ()


@pytest.mark.asyncio
async def test_get_users_from_azure_failed_to_fetch(mock_graph_client):
    mock_graph_client.graph_client_obj.users.by_user_id.return_value.get.side_effect = exceptions.MSGraphException

    with pytest.raises(exceptions.MSGraphException):
        await user.get_users_from_azure("123")


@pytest.mark.asyncio
async def test_get_users_from_azure_with_cache(mock_graph_client):
    users = {"123": "test_user"}
    await user.cache.multi_set(pairs=users.items(), ttl=60 * 5, namespace="azure_users")

    result = await user.get_users_from_azure("123")
    assert result == ["test_user"]

    assert len(mock_graph_client.mock_calls) == 1
