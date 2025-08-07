FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app
COPY --from=project_root pyproject.toml uv.lock README.md .

RUN uv sync --group frontend --no-dev --locked --no-install-project

COPY --from=project_root /src /app/src

CMD ["uv", "run", "python", "-m", "src.gui.main"]
