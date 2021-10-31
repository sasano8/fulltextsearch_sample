from fastapi import FastAPI
from fastapi.params import Depends
from .db import (
    Session,
    Repository,
    drop_all,
    create_all,
    engine,
)
from .models import Hero, Children, Parents
from sqlmodel import select, Session

app = FastAPI()


def get_session():
    with Session(engine) as session:
        yield session
        session.commit()


def init_db():
    drop_all(engine)
    create_all(engine)


@app.on_event("startup")
async def startup():
    init_db()


@app.on_event("shutdown")
async def shutdown():
    ...


@app.post("/system/load_test_data")
def post_test_data(db: Session = Depends(get_session)):
    """テストデータをロードするには、このAPIを実行してください。"""
    hero_1 = Hero(name="Deadpond", content="Dive Wilson")
    hero_2 = Hero(name="Spider-Boy", content="Pedro Parqueador")
    hero_3 = Hero(name="Rusty-Man", content="Tommy Sharp", age=48)
    hero_4 = Hero(name="1", content="1", age=1)
    hero_5 = Hero(name="山田太郎", content="ヤマダタロウ", age=1)

    db.add(hero_1)
    db.add(hero_2)
    db.add(hero_3)
    db.add(hero_4)
    db.add(hero_5)
    db.commit()


@app.post("/heroes")
def post_hero(db: Session = Depends(get_session), *, obj: Hero):
    return Repository(Hero).create(db, **obj.dict())


@app.get("/heroes/{id}")
def get_hero(db: Session = Depends(get_session), *, id: int):

    return db.exec(select(Hero).where(Hero.id == id)).one()


@app.get("/heroes")
def list_hero(db: Session = Depends(get_session), *, query=None):
    from sqlalchemy_searchable import search

    if query:
        q = search(select(Hero), query, sort=True)
    else:
        q = select(Hero)
    return db.exec(q).all()
