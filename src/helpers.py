from urllib.parse import urlencode


def generate_url_query(query_map: dict) -> str:
    return urlencode({k: v for k, v in query_map.items() if v is not None})
