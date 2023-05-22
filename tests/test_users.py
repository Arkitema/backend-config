import datetime

import pytest

from arkitema_config import exceptions, user


@pytest.mark.asyncio
async def test_get_aad_user_by_email(mock_graph_client):
    result = await user.get_aad_user_by_email("test@email.com")

    assert result == {"id": "123"}
    assert await user.cache.get("test@email.com", namespace="azure_emails") == {"id": "123"}

    assert len(mock_graph_client.mock_calls) == 3
    # GraphClient(...)
    assert mock_graph_client.call_count == 1
    assert mock_graph_client.mock_calls[0][2] == {"credential": "PLACEHOLDER"}
    # graph.get(...)
    assert len(mock_graph_client.mock_calls[1][2]) == 2
    assert mock_graph_client.mock_calls[1][2]["headers"] == {"Content-Type": "application/json"}
    assert mock_graph_client.mock_calls[1][2]["url"] == "/users/test_email.com%23EXT%23@PLACEHOLDER"
    # response.json(...)
    assert mock_graph_client.mock_calls[2][2] == {}


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
    mock_graph_client.graph_obj.post.return_value = "Response"

    result = user.invite_user_to_aad("test@email.com", "test", "platform")
    assert result == "Response"

    assert len(mock_graph_client.mock_calls) == 2
    # GraphClient(...)
    assert mock_graph_client.call_count == 1
    assert mock_graph_client.mock_calls[0][2] == {"credential": "PLACEHOLDER"}
    # graph.post(....)
    assert len(mock_graph_client.mock_calls[1][2]) == 3
    assert mock_graph_client.mock_calls[1][2]["url"] == "/invitations"
    assert (
        mock_graph_client.mock_calls[1][2]["data"]
        == '{"invitedUserEmailAddress": "test@email.com", "inviteRedirectUrl": "platform", "invitedUserDisplayName": "test", "sendInvitationMessage": true, "userPrincipalName": "test@email.com"}'
    )
    assert mock_graph_client.mock_calls[1][2]["headers"] == {"Content-Type": "application/json"}


@pytest.mark.asyncio
async def test_get_users_from_azure(mock_graph_client):
    result = await user.get_users_from_azure("123")
    assert result == [
        {"user_id": "123", "name": "test", "email": "NA", "company": "Name", "last_login": datetime.date(2000, 5, 5)}
    ]

    assert len(mock_graph_client.mock_calls) == 3
    # GraphClient(...)
    assert mock_graph_client.call_count == 1
    assert mock_graph_client.mock_calls[0][2] == {"credential": "PLACEHOLDER"}
    # graph.post(....)
    assert len(mock_graph_client.mock_calls[1][2]) == 3
    assert mock_graph_client.mock_calls[1][2]["url"] == "https://graph.microsoft.com/beta/$batch"
    assert mock_graph_client.mock_calls[1][2]["headers"] == {"Content-Type": "application/json"}
    assert mock_graph_client.mock_calls[1][2]["data"] == (
        '{"requests": [{"id": "123", "method": "GET", "url": '
        '"/users/123?$select=id,displayName,mail,userPrincipalName,companyName,signInActivity", '
        '"headers": {"Content-Type": "application/json"}}]}'
    )

    assert mock_graph_client.mock_calls[2][2] == {}


@pytest.mark.asyncio
async def test_get_users_from_azure_failed_to_fetch(mock_graph_client):
    mock_graph_client.post_response.status_code = 404

    with pytest.raises(exceptions.MSGraphException):
        result = await user.get_users_from_azure("123")


@pytest.mark.asyncio
async def test_get_users_from_azure_with_cache(mock_graph_client):
    users = {"123": "test_user"}
    await user.cache.multi_set(pairs=users.items(), ttl=60 * 5, namespace="azure_users")

    result = await user.get_users_from_azure("123")
    assert result == ["test_user"]

    assert len(mock_graph_client.mock_calls) == 0
