from typing import Annotated

from decouple import config
from fastapi import Depends
from sqlmodel import Session, create_engine

from .models import PaginationInput

DATABASE_URL = config("DATABASE_URL")
DEBUG = config("DEBUG", default=False, cast=bool)
connect_args = {"check_same_thread": False}
engine = create_engine(DATABASE_URL, connect_args=connect_args, echo=DEBUG)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

PaginationDep = Annotated[PaginationInput, Depends()]
