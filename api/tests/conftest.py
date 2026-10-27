import pytest
from sqlmodel import Session

from api.db import init_db, make_engine


@pytest.fixture
def engine(tmp_path):
    engine = make_engine(str(tmp_path / "test.db"))
    init_db(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def session(engine):
    with Session(engine) as session:
        yield session
