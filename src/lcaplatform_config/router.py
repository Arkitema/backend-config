from fastapi import Request
from strawberry.fastapi import GraphQLRouter
from strawberry.http import GraphQLHTTPResponse
from strawberry.types import ExecutionResult
from opentelemetry.propagate import inject
from lcaplatform_config.logging import config_logging

try:
    from core.config import settings
except (ImportError, ModuleNotFoundError):
    from lcaplatform_config import config

    settings = config.Settings()

logger = config_logging(__name__)


class LCAGraphQLRouter(GraphQLRouter):
    async def process_result(self, request: Request, result: ExecutionResult) -> GraphQLHTTPResponse:
        """
        Override method of parent class to log the GraphQL path that is called.

        Cleans the raw query string to obtain the GraphQL path.

        Args:
            request (Request): Request body object.
            result (ExecutionResult): Response data.

        Returns:
            GraphQLHTTPResponse: HTTP response object.
        """
        parsed_request = await request.json()
        query = parsed_request["query"]
        path = query.split("{")[1].replace("{", "").replace("query", "").strip().split("(")[0]

        variables = parsed_request.get("variables", "")
        user = getattr(request.state, "user", "")
        user_name = ""
        if user:
            p_name = getattr(user, "preferred_username", "")
            email = getattr(user, "email", "")
            name = getattr(user, "name", "")
            user_name = p_name or email or name

        if settings.ENABLE_TELEMETRY:
            headers = {}  # type: ignore
            inject(headers)  # inject trace info to header

        if result.errors:
            for error in result.errors:
                logger.error(
                    f'User: "{user_name}", GraphQL path: "{error.path}", msg: "{error.message}", vars: "{variables}"'
                )
        else:
            logger.info(f'User: "{user_name}", GraphQL path: "{path}", vars: "{variables}"')

        return await super().process_result(request, result)
