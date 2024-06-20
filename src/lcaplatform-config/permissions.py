import typing

from fastapi_azure_auth.user import User
from strawberry.permission import BasePermission
from strawberry.types import Info


class IsAuthenticated(BasePermission):
    message = "User is not authenticated"

    def has_permission(self, source: typing.Any, info: Info, **kwargs) -> bool:
        if info.context.get("user"):
            return True
        else:
            raise PermissionError("User is not authenticated")


def is_super_admin(user: User) -> bool:
    """Checks whether the user is an Admin and so can access all resources."""

    return "lca_super_admin" in user.roles
