from urllib.parse import urlencode

from fastapi import Request
from pydantic import HttpUrl, TypeAdapter

from .models import PageLinks


def generate_url_query(query_map: dict) -> str:
    return urlencode({k: v for k, v in query_map.items() if v is not None})


def required_url(url: str) -> HttpUrl:
    return TypeAdapter(HttpUrl).validate_python(url)


def optional_url(url: str | None) -> HttpUrl | None:
    if url is not None:
        return TypeAdapter(HttpUrl).validate_python(url)


def generate_links(
    current_page: int,
    total_page_count: int,
    request: Request,
    query_map: dict,
) -> PageLinks:
    base_url = str(request.url_for("read_transactions"))

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
