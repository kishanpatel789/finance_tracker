FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app
COPY --from=project_root pyproject.toml uv.lock README.md .

RUN uv sync --group frontend --no-dev --frozen --no-install-project

COPY --from=project_root /src/gui /app/src/gui

CMD ["uv", "run", "--no-sync", "python", "-m", "src.gui.main"]
