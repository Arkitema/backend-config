import json
import re
from datetime import datetime

from aiocache import Cache
from msgraph.core import GraphClient
from requests import Response

from arkitema_config import exceptions

try:
    from core.config import settings
except (ImportError, ModuleNotFoundError):
    from arkitema_config import config

    settings = config.Settings()

cache = Cache()


async def get_aad_user_by_email(email: str) -> dict[str, str]:
    """Check if user exists in Azure Active Directory"""
    user_data = await cache.get(email, namespace="azure_emails")
    if user_data:
        return user_data

    graph = GraphClient(credential=settings.AAD_GRAPH_SECRET)
    headers = {"Content-Type": "application/json"}

    # construct user principal name
    user_principal_name = email
    # check if user is an external user
    if not any(domain in email for domain in settings.INTERNAL_EMAIL_DOMAINS_LIST):
        # externals have principal name formatted like
        # xxxx_gmail.com%23EXT%23@cowi.onmicrosoft.com
        user_principal_name = user_principal_name.replace("@", "_")
        user_principal_name += f"%23EXT%23@{settings.DEFAULT_AD_FQDN}"
    response = graph.get(url=f"/users/{user_principal_name}", headers=headers)

    data = response.json()
    await cache.add(email, data, namespace="azure_emails", ttl=60 * 5)
    return data


def invite_user_to_aad(email: str, name: str, platform_url: str) -> Response:
    """
    invites a user to organization's Active Directory

    Parameters
    ----------
    email: str
        user's email to create an AD account and send invitation to
    name: str
        name to be displayed on AD and on the platform
    platform_url: str
        platform url that the invitation will redirect to

    Returns
    -------
    response: requests.Response
        http response received from Graph API
    """

    graph = GraphClient(credential=settings.AAD_GRAPH_SECRET)

    headers = {"Content-Type": "application/json"}

    body = {
        "invitedUserEmailAddress": email,
        "inviteRedirectUrl": platform_url,
        "invitedUserDisplayName": name,
        "sendInvitationMessage": True,
        "userPrincipalName": email,
    }
    # add user
    response = graph.post(url=f"/invitations", data=json.dumps(body), headers=headers)
    return response


async def get_users_from_azure(user_ids: str | list[str]) -> list[dict[str, str]]:
    """Fetch Users from Azure Active Directory"""

    if not user_ids:
        return [{}]

    if not isinstance(user_ids, list):
        user_ids = [user_ids]

    user_data = await cache.multi_get(user_ids, namespace="azure_users")
    users = {user_id: user_data[index] for index, user_id in enumerate(user_ids)}
    missing_users = [user_id for user_id, user_data in users.items() if user_data is None]

    requests = []
    headers = {"Content-Type": "application/json"}
    for user_id in missing_users:
        # graph api Beta supports signInActivity
        request = {
            "id": f"{user_id}",
            "method": "GET",
            "url": f"/users/{user_id}?$select=id,displayName,mail," "userPrincipalName,companyName,signInActivity",
            # signInActivity field requires AuditLog.Read.All permission
            "headers": headers,
        }

        requests.append(request)
    if requests:
        graph = GraphClient(credential=settings.AAD_GRAPH_SECRET)
        # use /beta/$batch url if fetching signInActivity
        responses = graph.post(
            url="https://graph.microsoft.com/beta/$batch",
            data=json.dumps({"requests": requests}),
            headers=headers,
        )
        if not responses.status_code == 200:
            raise exceptions.MSGraphException(f"Failed to fetch users via Graph API: {responses.text}")

        data: dict[str, list[dict]] = responses.json()

        for response in data.get("responses"):
            if not response.get("status") == 200:
                raise exceptions.MSGraphException(f"Failed to fetch the response from responses: {response}")
            body: dict[str, str] = response.get("body")
            email = body.get("mail")
            # some accounts have null emails
            if not email:
                if re.match(
                    r"^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$",
                    body.get("userPrincipalName", ""),
                ):
                    email = body.get("userPrincipalName")
                else:
                    email = "NA"
            if last_login := body.get("signInActivity", {}).get("lastSignInDateTime"):
                last_login = datetime.strptime(last_login, r"%Y-%m-%dT%H:%M:%SZ").date()
            users[body.get("id")] = {
                "user_id": body.get("id"),
                "name": body.get("displayName"),
                "email": email,
                "company": body.get("companyName"),
                "last_login": last_login,
            }
        await cache.multi_set(pairs=users.items(), ttl=60 * 5, namespace="azure_users")
    return list(users.values())
