from typing import Annotated

from fastapi import APIRouter, Query
from pydantic import AfterValidator
from sqlmodel import case, func, nulls_last, outerjoin, select

from ..dependencies import SessionDep
from ..helpers import get_month_range, validate_year_month
from ..models import (
    Category,
    MonthlySummary,
    Transaction,
)

router = APIRouter(
    prefix="/reports",
    tags=["reports"],
)

YearMonthParam = Annotated[
    str, Query(pattern=r"\d{4}-\d{2}"), AfterValidator(validate_year_month)
]


@router.get("/monthly_budget", response_model=list[MonthlySummary])
def get_monthly_report(year_month: YearMonthParam, session: SessionDep):
    month_range = get_month_range(year_month)

    # subquery to aggregate transactions
    subq = (
        select(
            Transaction.category_id, func.sum(Transaction.amount).label("amount_spent")
        )
        .where(
            Transaction.trans_date >= month_range.start,
            Transaction.trans_date <= month_range.end,
        )
        .group_by(Transaction.category_id)
        .subquery()
    )

    # final query to get category info
    query = (
        select(
            Category.id.label("category_id"),
            Category.name.label("category_name"),
            func.coalesce(subq.c.amount_spent, 0).label("amount_spent"),
            Category.budget,
        )
        .select_from(
            outerjoin(Category, subq, Category.id == subq.c.category_id, full=True)
        )
        .order_by(
            case((Category.budget.is_(None), 1), else_=0), nulls_last(Category.name)
        )
    )

    data = session.exec(query).all()

    return data
