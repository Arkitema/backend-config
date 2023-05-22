import logging

from fastapi import Request
from strawberry.fastapi import GraphQLRouter
from strawberry.http import GraphQLHTTPResponse
from strawberry.types import ExecutionResult

logger = logging.getLogger(__name__)


class ArkitemaGraphQLRouter(GraphQLRouter):
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

        query = (await request.json())["query"]

        path = query.split("{")[1].replace("{", "").replace("query", "").strip().split("(")[0]
        logger.info(f'Calling GraphQL path: "{path}"')

        return await super().process_result(request, result)
