from typing import Literal
from pydantic import BaseSettings
from sqlmodel import SQLModel, create_engine, Session, select, update, delete
from sqlalchemy_searchable import make_searchable


class DbConfig(BaseSettings):
    class Config:
        env_prefix = ""
        env_file = ".env"

    _TYPE: Literal["", "postgresql", "sqlite"] = "postgresql"
    _ADAPTER: Literal["", "psycopg2", "asyncpg"] = "psycopg2"
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    DB_HOST: str
    DB_TEST_HOST: str = ""
    is_test: bool = False

    @property
    def connection_string(self) -> str:
        return "{TYPE}+{ADAPTER}://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DB_HOST}/{POSTGRES_DB}".format(
            TYPE=self._TYPE,
            ADAPTER=self._ADAPTER,
            DB_HOST=self.DB_HOST if not self.is_test else self.DB_TEST_HOST,
            POSTGRES_DB=self.POSTGRES_DB,
            POSTGRES_USER=self.POSTGRES_USER,
            POSTGRES_PASSWORD=self.POSTGRES_PASSWORD,
        )


def get_connection_string(is_test: bool = False):
    return DbConfig(is_test=is_test).connection_string


DB_URL = get_connection_string(is_test=False)
DB_TEST_URL = get_connection_string(is_test=True)
engine = create_engine(DB_URL, echo=True)
test_engine = create_engine(DB_TEST_URL, echo=False)


def stand_by_models():
    # イベントをフックするのに必要
    # モデル定義が読み込まれる前に実行しておく必要がある

    # options1 = {regconfig="pg_catalog.english"}  # default
    # options2 = {regconfig="pg_catalog.japanese"}  # textsearch_jaを導入すると使える
    make_searchable(SQLModel.metadata, options={})


def stand_by_db():
    import sqlalchemy as sa

    # モデル読み込み後、かつ、テーブルを作成する前に呼び出す
    sa.orm.configure_mappers()


def create_all(engine):
    SQLModel.metadata.create_all(engine)


def drop_all(engine):
    SQLModel.metadata.drop_all(engine)


class Repository:
    def __init__(self, model) -> None:
        self.model = model

    def get(self, db, id):
        return db.get(self.model, id)

    def create(self, db, **kwargs):
        obj = self.model(**kwargs)
        db.add(obj)
        db.flush()
        return obj

    def update(self, db, **kwargs):
        id = kwargs.pop("id")
        stmt = update(self.model).where(id=id).values(**kwargs)
        return db.execute(stmt)

    def delete(self, db, id):
        stmt = delete(self.model).where(id=id)
        return db.execute(stmt)
