import json
from typing import Optional

import pytest
from pydantic import BaseModel
from sqlmodel import Session

from arkitema_config.graphql.input_filters import (
    BaseFilter,
    FilterOptions,
    SortOptions,
    filter_model_query,
    sort_model_query,
)


@pytest.mark.parametrize(
    "filter_options,expected",
    [
        (FilterOptions(equal="70e94ba8-128c-4890-8291-b4982c0fb5f2"), 1),
        (FilterOptions(contains="4890"), 1),
        (FilterOptions(starts_with="70e94ba8"), 1),
        (FilterOptions(ends_with="0fb5f2"), 1),
        (FilterOptions(is_empty=True), 0),
        (FilterOptions(is_not_empty=True), 3),
        (FilterOptions(is_any_of=["70e94ba8-128c-4890-8291-b4982c0fb5f2", "5d02171c-483d-4c27-9cbb-20e9b7c6f802"]), 2),
        (FilterOptions(json_contains=json.dumps({"domains": "design"})), 2),
        (FilterOptions(json_contains="domains"), 3),
        (FilterOptions(is_true=True), 0),
    ],
    ids=[
        "equal",
        "contains",
        "starts_with",
        "ends_with",
        "is_empty",
        "is_not_empty",
        "is_any_of",
        "json_contains",
        "json_contains_error",
    ],
)
def test_filter_model_query(entry_data, entry_model, entries, db_engine, filter_options, expected):
    class ModelFilter(BaseModel, BaseFilter):
        id: Optional[FilterOptions] = None
        name: Optional[FilterOptions] = None
        meta_fields: Optional[FilterOptions] = None

    if filter_options.json_contains:
        filters = ModelFilter(meta_fields=filter_options)
    else:
        filters = ModelFilter(id=filter_options)

    with Session(db_engine) as session:
        query = filter_model_query(entry_model, filters)
        data = session.exec(query).all()

    assert len(data) == expected


@pytest.mark.parametrize(
    "sort_options,expected",
    [
        (SortOptions.ASC, "36485ccc-d395-4a96-8ff9-e6dd713c734e"),
        (SortOptions.DSC, "70e94ba8-128c-4890-8291-b4982c0fb5f2"),
    ],
    ids=["asc", "dsc"],
)
def test_sort_model_query(entry_data, entry_model, entries, db_engine, sort_options, expected):
    class ModelSort(BaseModel, BaseFilter):
        id: Optional[SortOptions] = None
        name: Optional[SortOptions] = None

    sorters = ModelSort(id=sort_options)
    with Session(db_engine) as session:
        query = sort_model_query(entry_model, sorters)
        data = session.exec(query).all()

    assert data[0].id == expected
