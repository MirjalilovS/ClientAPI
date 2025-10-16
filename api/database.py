from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine
from . import models

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args, pool_pre_ping=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine, echo=True)


def get_session():
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()


SessionDep = Annotated[Session, Depends(get_session)]
