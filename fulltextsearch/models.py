from typing import Optional
from sqlmodel import Field, SQLModel, Relationship, Column
from sqlalchemy_utils.types import TSVectorType
from .db import stand_by_models, stand_by_db


stand_by_models()


class Hero(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    content: str
    age: Optional[int] = None
    search_vector: Optional[str] = Field(
        sa_column=Column(
            TSVectorType(
                "name",
                "content",
                # weights={"name": "A", "secret_name": "B", "age": "D"},
            )
        )
    )


class Parents(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    # children = orm.relationship("Children")


class Children(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    parent_id: Optional[int] = Field(default=None, foreign_key="parents.id")


stand_by_db()
