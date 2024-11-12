import logging

from fastapi import Request
from strawberry.fastapi import GraphQLRouter
from strawberry.http import GraphQLHTTPResponse
from strawberry.types import ExecutionResult
from opentelemetry.propagate import inject

try:
    from core.config import settings
except (ImportError, ModuleNotFoundError):
    from lcaplatform_config import config

    settings = config.Settings()

if settings.ENABLE_TELEMETRY:
    # need to use same naming as in logging file for formatters, trace_id
    logger = logging.getLogger("uvicorn.access")
else:
    logger = logging.getLogger(__name__)


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
        email = ""
        if user:
            email = getattr(user, "verified_primary_email", "")

        if settings.ENABLE_TELEMETRY:
            headers = {}  # type: ignore
            inject(headers)  # inject trace info to header

        if result.errors:
            for error in result.errors:
                logger.error(
                    f'User: "{email}", GraphQL path: "{error.path}", msg: "{error.message}", vars: "{variables}"'
                )
        else:
            logger.info(f'User: "{email}", GraphQL path: "{path}", vars: "{variables}"')

        return await super().process_result(request, result)
