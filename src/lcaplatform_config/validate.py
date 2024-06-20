from typing import Union

import httpx
from aiocache import cached
from fastapi_azure_auth.user import User

try:
    from core.config import settings
except (ImportError, ModuleNotFoundError):
    from lcaplatform_config import config

    settings = config.Settings()


@cached(ttl=60)
async def project_exists(project_id: str, token: str) -> Union[bool, list[dict]]:
    """
    Checks whether the project exists. The function is cached with a decorator.
    Args:
        project_id: the ProjectID that the user is navigating inside.
        token: the user's PAT

    Returns:
        boolean:
            True if the user trying to access the resources is a member of that Project
            else False
    """

    query = """
        query($id: String!) {
            projects(filters: {id: {equal: $id}}) {
                id
                public
            }
        }
    """

    async with httpx.AsyncClient(
        headers={"authorization": f"Bearer {token}"},
    ) as client:
        response = await client.post(
            f"{settings.ROUTER_URL}/graphql",
            json={
                "query": query,
                "variables": {"id": project_id},
            },
        )
        data = response.json()
        if response.is_error or data.get("errors"):
            return False
        return data.get("data")


def is_super_admin(user: User) -> bool:
    """Checks whether the user is an Admin and so can access all resources."""

    return "lca_super_admin" in user.roles


@cached(ttl=60)
async def group_exists(project_id: str, group_id: str, token: str) -> bool:
    """
    Checks whether the group exists. The function is cached with a decorator.
    Args:
        project_id: the ProjectID that the user is navigating inside.
        group_id: the GroupID of the Project Group the user is interacting with.
        token: the user's PAT

    Returns:
        True if the user trying to access the resources is a member of that Project Group
        else False
    """

    query = """
    query($projectId: String!, $id: String!) {
        projectGroups(projectId: $projectId, filters: {id: {equal: $id}}) {
            id
        }
    }
    """

    async with httpx.AsyncClient(
        headers={"authorization": f"Bearer {token}"},
    ) as client:
        response = await client.post(
            f"{settings.ROUTER_URL}/graphql",
            json={
                "query": query,
                "variables": {"projectId": project_id, "id": group_id},
            },
        )
        data = response.json()
        if response.is_error or data.get("errors"):
            return False
        return True
