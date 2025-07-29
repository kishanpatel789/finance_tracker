import tomllib
from collections import namedtuple
from pathlib import Path
from urllib.parse import urlencode

from fastapi import Request
from pydantic import HttpUrl, TypeAdapter
from sqlmodel import Session, func, select
from sqlmodel.sql.expression import SelectOfScalar

from .models import PageBase, PageLinks, PaginationInput

ProjectInfo = namedtuple("ProjectInfo", ["version", "author_name", "author_email"])


def parse_pyproject_toml() -> ProjectInfo:
    project_root = Path(__file__).parents[2]
    with open(project_root / "pyproject.toml", "rb") as f:
        pyproject = tomllib.load(f)

    project_info = ProjectInfo(
        version=pyproject["project"]["version"],
        author_name=pyproject["project"]["authors"][0]["name"],
        author_email=pyproject["project"]["authors"][0]["email"],
    )

    return project_info


def generate_url_query(query_map: dict) -> str:
    return urlencode({k: v for k, v in query_map.items() if v is not None})


def required_url(url: str) -> HttpUrl:
    return TypeAdapter(HttpUrl).validate_python(url)


def optional_url(url: str | None) -> HttpUrl | None:
    if url is not None:
        return TypeAdapter(HttpUrl).validate_python(url)


def get_query_stats(
    query: SelectOfScalar, session: Session, pagination_input: PaginationInput
) -> tuple[int, int]:
    count_query = select(func.count(1).label("cnt")).select_from(query.subquery())
    total_row_count = session.exec(count_query).one() or 0

    total_page_count = (
        total_row_count + pagination_input.size - 1
    ) // pagination_input.size

    return total_row_count, total_page_count


def get_page_num_to_return(
    pagination_input: PaginationInput, total_page_count: int
) -> int:
    """Determine actual page to give; give last page if requested page is out of bounds"""
    page = min(
        pagination_input.page,
        max(total_page_count, 1),  # give at least page 1 if no records
    )

    return page


def generate_links(
    current_page: int,
    total_page_count: int,
    request: Request,
    query_map: dict,
) -> PageLinks:
    base_url = request.url_for("read_transactions")

    current = f"{base_url}?{generate_url_query(query_map)}"

    if current_page > 1:
        query_map.update(dict(page=current_page - 1))
        prev = f"{base_url}?{generate_url_query(query_map)}"
    else:
        prev = None

    if current_page < total_page_count:
        query_map.update(dict(page=current_page + 1))
        next_ = f"{base_url}?{generate_url_query(query_map)}"
    else:
        next_ = None

    return PageLinks(
        current=required_url(current),
        prev=optional_url(prev),
        next=optional_url(next_),
    )


def create_page(
    query: SelectOfScalar,
    query_map: dict,
    pagination_input: PaginationInput,
    session: Session,
    request: Request,
) -> PageBase:
    """Paginate a SQLModel query and return the results along with pagination links."""

    total_row_count, total_page_count = get_query_stats(
        query, session, pagination_input
    )
    page = get_page_num_to_return(pagination_input, total_page_count)

    # build links
    query_map.update(dict(page=page, size=pagination_input.size))
    links = generate_links(
        current_page=page,
        total_page_count=total_page_count,
        request=request,
        query_map=query_map,
    )

    # get paginated data
    offset = (page - 1) * pagination_input.size
    query = query.offset(offset).limit(pagination_input.size)
    data = session.exec(query).all()

    page_output = PageBase(
        data=data,
        total_count=total_row_count,
        links=links,
    )

    return page_output
