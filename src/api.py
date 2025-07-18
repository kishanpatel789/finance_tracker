from typing import Annotated

from decouple import config
from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import Session, create_engine, select

from .models import (
    Category,
    CategoryCreate,
    CategoryRead,
    CategoryUpdate,
    DeleteResponse,
)

DATABASE_URL = config("DATABASE_URL")
connect_args = {"check_same_thread": False}
engine = create_engine(DATABASE_URL, connect_args=connect_args)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Finance Tracker is alive!"}


@app.post("/categories/", response_model=CategoryRead)
def create_category(category: CategoryCreate, session: SessionDep):
    db_category = Category.model_validate(category)
    session.add(db_category)
    session.commit()
    session.refresh(db_category)
    return db_category


@app.get("/categories/", response_model=list[CategoryRead])
def read_categories(session: SessionDep):
    categories = session.exec(select(Category)).all()
    return categories


@app.get("/categories/{category_id}", response_model=CategoryRead)
def read_category(category_id: int, session: SessionDep):
    category = session.get(Category, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@app.patch("/categories/{category_id}", response_model=CategoryRead)
def update_category(category_id: int, category: CategoryUpdate, session: SessionDep):
    db_category = session.get(Category, category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    category_data = category.model_dump(exclude_unset=True)
    for key, value in category_data.items():
        setattr(db_category, key, value)

    session.add(db_category)
    session.commit()
    session.refresh(db_category)
    return db_category


@app.delete("/categories/{category_id}")
def delete_category(category_id: int, session: SessionDep) -> DeleteResponse:
    db_category = session.get(Category, category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    session.delete(db_category)
    session.commit()
    return {"detail": f"Category with ID {category_id} deleted successfully"}


# TODO: CRUD operations for Transactions
