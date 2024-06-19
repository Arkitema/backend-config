import os
from typing import Optional

import pytest
from sqlalchemy import JSON, Column
from sqlmodel import Field, Session, SQLModel, create_engine

from arkitema_config.formatting import string_uuid


@pytest.fixture(scope="session")
def db_engine():
    sqlite_file_name = "database.db"
    sqlite_url = f"sqlite:///{sqlite_file_name}"

    yield create_engine(sqlite_url)

    os.remove(sqlite_file_name)


@pytest.fixture(scope="session")
def entry_model(db_engine):
    class Entry(SQLModel, table=True):
        id: Optional[str] = Field(default_factory=string_uuid, primary_key=True)
        name: str
        meta_fields: dict = Field(default=dict, sa_column=Column(JSON))

    yield Entry


@pytest.fixture()
def init_db(db_engine, entry_model):
    SQLModel.metadata.create_all(db_engine)

    yield

    SQLModel.metadata.drop_all(db_engine)


@pytest.fixture()
def entry_data():
    yield [
        ("Test 0", "70e94ba8-128c-4890-8291-b4982c0fb5f2", {"domains": "[design]"}),
        ("Test 1", "36485ccc-d395-4a96-8ff9-e6dd713c734e", {"test": "test"}),
        ("Test 2", "5d02171c-483d-4c27-9cbb-20e9b7c6f802", {"domains": '{"design": "a1"}'}),
    ]


@pytest.fixture()
def entries(db_engine, entry_model, init_db, entry_data):
    with Session(db_engine) as session:
        entries = [entry_model(id=_id, name=name, meta_fields=meta_fields) for name, _id, meta_fields in entry_data]
        [session.add(entry) for entry in entries]
        session.commit()
        [session.refresh(entry) for entry in entries]

    yield entries
