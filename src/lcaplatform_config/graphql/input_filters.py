import json
from enum import Enum
from typing import Any

import strawberry
from sqlalchemy import desc
from sqlmodel import col, or_, select
from sqlmodel.main import SQLModelMetaclass
from sqlmodel.sql.expression import SelectOfScalar


@strawberry.input
class FilterOptions:
    equal: str | None = None
    contains: str | None = None
    starts_with: str | None = None
    ends_with: str | None = None
    is_empty: bool | None = None
    is_not_empty: bool | None = None
    is_any_of: list[str] | None = None
    is_true: bool | None = None
    json_contains: str | None = None


class BaseFilter:  # pragma: no cover
    def dict(self) -> dict[str, Any]:
        return self.__dict__

    def keys(self) -> list[str]:
        return [key for key, value in self.dict().items() if value]


def filter_model_query(
    model: SQLModelMetaclass, filters: BaseFilter, query: SelectOfScalar | None = None
) -> SelectOfScalar:
    if query is None:
        query = select(model)

    for filter_key in filters.keys():
        _filter = getattr(filters, filter_key)
        field = getattr(model, filter_key)

        if _filter.equal:
            query = query.where(field == _filter.equal)
        elif _filter.is_true is not None:
            query = query.where(field == _filter.is_true)
        elif _filter.contains:
            query = query.where(col(field).contains(_filter.contains))
        elif _filter.starts_with:
            query = query.where(col(field).startswith(_filter.starts_with))
        elif _filter.ends_with:
            query = query.where(col(field).endswith(_filter.ends_with))
        elif _filter.is_empty:
            query = query.where(or_(field == "", field == None))  # noqa: E711
        elif _filter.is_not_empty:
            query = query.where(or_(field != "", field != None))  # noqa: E711
        elif _filter.is_any_of:
            query = query.where(col(field).in_(_filter.is_any_of))
        elif _filter.json_contains and str(field.type) == "JSON":
            try:
                obj_filter = json.loads(_filter.json_contains)
                for key, value in obj_filter.items():
                    query = query.where(col(field)[key].astext.contains(value))
            except json.decoder.JSONDecodeError:
                continue
            except AttributeError:
                query = query.where(col(field)[key].contains(value))

    return query


@strawberry.enum
class SortOptions(Enum):
    ASC = "asc"
    DSC = "dsc"


def sort_model_query(
    model: SQLModelMetaclass, sorters: BaseFilter, query: SelectOfScalar | None = None
) -> SelectOfScalar:
    if query is None:
        query = select(model)

    for sort_key in sorters.keys():
        sort_by = getattr(sorters, sort_key)
        field = getattr(model, sort_key)

        if sort_by == SortOptions.DSC:
            query = query.order_by(desc(field))
        else:
            query = query.order_by(field)

    return query
