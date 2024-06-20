import re

from aiocache import Cache
from azure.identity.aio import ClientSecretCredential
from kiota_abstractions.base_request_configuration import RequestConfiguration
from msgraph import GraphServiceClient
from msgraph.generated.models.invitation import Invitation
from msgraph.generated.users.item.user_item_request_builder import UserItemRequestBuilder
from requests import Response

from lcaplatform_config import exceptions

try:
    from core.config import settings
except (ImportError, ModuleNotFoundError):
    from lcaplatform_config import config

    settings = config.Settings()

cache = Cache()


def get_credentials() -> ClientSecretCredential:
    return ClientSecretCredential(settings.AAD_TENANT_ID, settings.AAD_APP_CLIENT_ID, settings.AAD_GRAPH_SECRET)


async def get_aad_user_by_email(email: str) -> dict[str, str]:
    """Check if user exists in Azure Active Directory"""
    user_data = await cache.get(email, namespace="azure_emails")
    if user_data:
        return user_data

    scopes = ["https://graph.microsoft.com/.default"]
    graph = GraphServiceClient(credentials=get_credentials(), scopes=scopes)
    # headers = {"Content-Type": "application/json"}

    # construct user principal name
    user_principal_name = email
    # check if user is an external user
    if not any(domain in email for domain in settings.INTERNAL_EMAIL_DOMAINS_LIST):
        # externals have principal name formatted like
        # xxxx_gmail.com%23EXT%23@cowi.onmicrosoft.com
        user_principal_name = user_principal_name.replace("@", "_")
        user_principal_name += f"%23EXT%23@{settings.DEFAULT_AD_FQDN}"
    user = await graph.users.by_user_id(user_principal_name).get()
    if user:
        await cache.add(email, user, namespace="azure_emails", ttl=60 * 5)
    return user


async def invite_user_to_aad(email: str, name: str, platform_url: str) -> Response:
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

    scopes = ["https://graph.microsoft.com/.default"]
    graph = GraphServiceClient(credentials=get_credentials(), scopes=scopes)

    request_body = Invitation(
        invited_user_email_address=email,
        invite_redirect_url=platform_url,
        invited_user_display_name=name,
        send_invitation_message=True,
        # user_principal_name = email
    )

    # add user
    response = await graph.invitations.post(request_body)
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

    query_params = UserItemRequestBuilder.UserItemRequestBuilderGetQueryParameters(
        select=["id", "displayName", "mail", "userPrincipalName", "companyName", "signInActivity"],
    )

    scopes = ["https://graph.microsoft.com/.default"]
    graph = GraphServiceClient(credentials=get_credentials(), scopes=scopes)

    request_configuration = RequestConfiguration(query_parameters=query_params)

    for user_id in missing_users:
        try:
            user = await graph.users.by_user_id(user_id).get(request_configuration=request_configuration)
        except Exception:
            raise exceptions.MSGraphException(f"Failed to fetch users via Graph API: {user_id}")

        email = user.mail
        # some accounts have null emails
        if not email:
            if re.match(
                r"^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$",
                user.userPrincipalName or "",
            ):
                email = user.userPrincipalName
            else:
                email = "NA"
        if user.sign_in_activity:
            last_login = user.sign_in_activity.last_sign_in_date_time
        users[user.id] = {
            "user_id": user.id,
            "name": user.display_name,
            "email": email,
            "company": user.company_name,
            "last_login": last_login,
        }
    await cache.multi_set(pairs=users.items(), ttl=60 * 5, namespace="azure_users")
    return list(users.values())
