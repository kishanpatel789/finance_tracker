from fastapi import APIRouter, HTTPException
from sqlmodel import select

from ..dependencies import SessionDep
from ..models import (
    Category,
    CategoryCreate,
    CategoryRead,
    CategoryUpdate,
    DeleteResponse,
)

router = APIRouter(
    prefix="/categories",
    tags=["categories"],
)


@router.post("/", response_model=CategoryRead)
def create_category(category: CategoryCreate, session: SessionDep):
    db_category = Category.model_validate(category)
    session.add(db_category)
    session.commit()
    session.refresh(db_category)
    return db_category


@router.get("/", response_model=list[CategoryRead])
def read_categories(session: SessionDep):
    categories = session.exec(select(Category)).all()
    return categories


@router.get("/{category_id}", response_model=CategoryRead)
def read_category(category_id: int, session: SessionDep):
    category = session.get(Category, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.patch("/{category_id}", response_model=CategoryRead)
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


@router.delete("/{category_id}")
def delete_category(category_id: int, session: SessionDep) -> DeleteResponse:
    db_category = session.get(Category, category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    session.delete(db_category)
    session.commit()
    return {"detail": f"Category with ID {category_id} deleted successfully"}
