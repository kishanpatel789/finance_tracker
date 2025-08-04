from dataclasses import dataclass, field
from datetime import date

import httpx
from dateutil.relativedelta import relativedelta
from decouple import config
from nicegui import ui

API_BASE_URL = config("API_BASE_URL")


@dataclass
class APIResult:
    success: bool
    data: list | dict = field(default_factory=list)
    error: str | None = None


def show_error(message: str):
    ui.notify(message, type="negative", position="top", close_button="Close")


def call_api(
    endpoint: str, payload: dict | None = None, *, method: str = "GET"
) -> APIResult:
    endpoint = endpoint.removeprefix("/")
    url = f"{API_BASE_URL}/{endpoint}"

    try:
        match method:
            case "GET":
                response = httpx.get(url, params=payload)
            case "POST":
                response = httpx.post(url, json=payload)
            case "PATCH":
                response = httpx.patch(url, json=payload)
            case "DELETE":
                response = httpx.delete(url)
            case _:
                raise ValueError(f"Unsupported HTTP method: {method}")
        response.raise_for_status()
        return APIResult(success=True, data=response.json())
    except httpx.HTTPStatusError as e:
        error_message = f"{e.response.status_code} - {e.response.text}"
        show_error(f"API call failed: {error_message}")
        return APIResult(success=False, error=str(e))
    except httpx.ConnectError as e:
        show_error("Failed to connect to the API. Please check network connection.")
        return APIResult(success=False, error=str(e))


def format_currency(amount: str | None) -> str:
    if amount is None:
        return "--"
    return f"${float(amount):,.2f}"


def currency_str_to_float(amount: str | None) -> float:
    if amount is None:
        return 0.0
    return float(amount)


def get_selectable_categories() -> dict[str, str]:
    """Fetches categories from the API and returns them in a format suitable for a select input."""
    options = {"__NONE__": "-- No Category --"}
    result = call_api("/categories/", method="GET")
    if result.success:
        options.update({category["id"]: category["name"] for category in result.data})
    return options


def get_month_options(num_months: int) -> dict[str, str]:
    """Get last few months, including current month. Output as dictionary for select input."""
    _date = date.today().replace(day=1)
    options = {}

    for _ in range(num_months):
        value = _date.strftime("%Y-%m")
        label = _date.strftime("%b %Y")
        options[value] = label

        _date -= relativedelta(months=1)

    return options
