import httpx
from decouple import config

API_BASE_URL = config("API_BASE_URL")


def call_api(
    endpoint: str, payload: dict | None = None, *, method: str = "GET"
) -> dict:
    endpoint = endpoint.removeprefix("/")
    url = f"{API_BASE_URL}/{endpoint}"

    match method:
        case "GET":
            response = httpx.get(url, params=payload)
        case "POST":
            response = httpx.post(url, json=payload)
        case "PATCH":
            response = httpx.put(url, json=payload)
        case "DELETE":
            response = httpx.delete(url)
        case _:
            raise ValueError(f"Unsupported HTTP method: {method}")

    # TODO: Refactor API failure into frontend message
    response.raise_for_status()

    return response.json()
