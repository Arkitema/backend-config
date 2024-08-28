from typing import Generic, Optional, TypeVar

import strawberry
from strawberry.federation.schema_directives import Shareable

GenericType = TypeVar("GenericType")


@strawberry.type
class Connection(Generic[GenericType]):
    """Represents a paginated relationship between two entities

    This pattern is used when the relationship itself has attributes.
    In a Facebook-based domain example, a friendship between two people
    would be a connection that might have a `friendshipStartTime`
    """

    page_info: "PageInfo[GenericType]"
    edges: list["Edge[GenericType]"]
    num_edges: int


@strawberry.type
class PageInfo(Generic[GenericType]):
    """Pagination context to navigate objects with cursor-based pagination

    Instead of classic offset pagination via `page` and `limit` parameters,
    here we have a cursor of the last object, and we fetch items starting from that one

    Read more at:
        - https://graphql.org/learn/pagination/#pagination-and-edges
        - https://relay.dev/graphql/connections.htm
    """

    # added shareable as workaround for error
    # Non-shareable field "PageInfo.endCursor" is resolved from multiple subgraphs
    # when used in multiple services
    has_next_page: bool = strawberry.field(directives=[Shareable()])
    has_previous_page: bool = strawberry.field(directives=[Shareable()])
    start_cursor: Optional[str] = strawberry.field(directives=[Shareable()])
    end_cursor: Optional[str] = strawberry.field(directives=[Shareable()])


@strawberry.type
class Edge(Generic[GenericType]):
    """An edge may contain additional information of the relationship. This is the trivial case"""

    node: GenericType
    cursor: str


Cursor = str
