import typing

from strawberry.permission import BasePermission
from strawberry.types import Info


class IsAuthenticated(BasePermission):
    message = "User is not authenticated"

    def has_permission(self, source: typing.Any, info: Info, **kwargs) -> bool:
        if info.context.get("user"):
            return True
        else:
            raise PermissionError("User is not authenticated")
