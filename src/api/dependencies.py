from typing import Annotated

from decouple import config
from fastapi import Depends
from sqlmodel import Session, create_engine

DATABASE_URL = config("DATABASE_URL")
DEBUG = config("DEBUG", default=False, cast=bool)
engine = create_engine(DATABASE_URL, echo=DEBUG)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
