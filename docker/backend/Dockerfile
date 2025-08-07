FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app
COPY --from=project_root pyproject.toml uv.lock README.md .

RUN uv sync --group backend --no-dev --frozen --no-install-project

COPY --from=project_root /src/api /app/src/api
COPY --from=project_root /alembic.ini /app/alembic.ini
COPY --from=project_root /migrations /app/migrations
COPY start.sh /app/start.sh

RUN chmod +x /app/start.sh

CMD ["/app/start.sh"]
