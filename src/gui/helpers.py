import httpx
from decouple import config

API_BASE_URL = config("API_BASE_URL")


def call_api(endpoint: str, method: str = "GET", payload: dict = None) -> dict:
    if not endpoint.startswith("/"):
        raise ValueError("Endpoint must start with a '/'")
    url = f"{API_BASE_URL}{endpoint}"

    if method == "GET":
        response = httpx.get(url, params=payload)
    elif method == "POST":
        response = httpx.post(url, json=payload)
    elif method == "PATCH":
        response = httpx.put(url, json=payload)
    elif method == "DELETE":
        response = httpx.delete(url)

    response.raise_for_status()

    return response.json()
