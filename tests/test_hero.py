import pytest

from fastapi.testclient import TestClient

from sqlmodel import Session, SQLModel
from fulltextsearch.db import test_engine


@pytest.fixture
def init_session():
    try:
        SQLModel.metadata.drop_all(test_engine)
    except:
        pass
    SQLModel.metadata.create_all(test_engine)
    with Session(test_engine) as session:
        yield session
        session.commit()


@pytest.fixture
def client(init_session: Session):
    from fulltextsearch.api import app, get_session

    def get_session_override():
        return init_session

    app.dependency_overrides[get_session] = get_session_override

    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def depends_1():
    yield 1


@pytest.fixture
def depends_2(depends_1):
    yield depends_1 + 2


def test_depend(depends_2):
    assert depends_2 == 3


def test_create_hero(client: TestClient):
    post = {"name": "山田太郎", "content": "ヤマダタロウ"}
    res = client.post("/heroes", json=post)
    create = res.json()
    res.raise_for_status()

    assert res.status_code == 200
    assert create["name"] == post["name"]
    assert create["content"] == post["content"]
    assert create["age"] is None
    assert create["id"] is not None

    id = create["id"]
    res = client.get(f"/heroes/{id}")
    get = res.json()

    assert get["id"] == create["id"]
    assert get["name"] == create["name"]
    assert get["content"] == create["content"]
    assert get["age"] == create["age"]

    res = client.get(f"/heroes")
    pages = res.json()
    assert len(pages) == 1
    obj = pages[0]
    assert obj["id"] == create["id"]
    assert obj["name"] == create["name"]
    assert obj["content"] == create["content"]
    assert obj["age"] == create["age"]

    res = client.get(f"/heroes?query=山田太郎")
    res.raise_for_status()
    pages = res.json()
    assert len(pages) == 1

    res = client.get(f"/heroes?query=xxxxxxx")
    res.raise_for_status()
    pages = res.json()
    assert len(pages) == 0

    res = client.get(f"/heroes?query=山")
    res.raise_for_status()
    pages = res.json()
    assert len(pages) == 1

    res = client.get(f"/heroes?query=ヤマダ")
    res.raise_for_status()
    pages = res.json()
    assert len(pages) == 1

    res = client.get(f"/heroes?query=郎")
    res.raise_for_status()
    pages = res.json()
    assert len(pages) == 1
