import json
from enum import Enum
from typing import Optional

import strawberry
from sqlalchemy import desc
from sqlmodel import col, or_, select
from sqlmodel.main import SQLModelMetaclass
from sqlmodel.sql.expression import SelectOfScalar


@strawberry.input
class FilterOptions:
    equal: Optional[str] = None
    contains: Optional[str] = None
    starts_with: Optional[str] = None
    ends_with: Optional[str] = None
    is_empty: Optional[bool] = None
    is_not_empty: Optional[bool] = None
    is_any_of: Optional[list[str]] = None
    is_true: Optional[bool] = None
    json_contains: Optional[str] = None


class BaseFilter:  # pragma: no cover
    def dict(self):
        return self.__dict__

    def keys(self):
        return [key for key, value in self.dict().items() if value]


def filter_model_query(model: SQLModelMetaclass, filters: BaseFilter, query: Optional[SelectOfScalar] = None):
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
            query = query.where(or_(field == "", field == None))
        elif _filter.is_not_empty:
            query = query.where(or_(field != "", field != None))
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
    model: SQLModelMetaclass, sorters: BaseFilter, query: Optional[SelectOfScalar] = None
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
