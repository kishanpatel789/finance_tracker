#!/bin/bash
set -e

echo "Running Alembic migrations..."
uv run alembic upgrade head

echo "Starting FastAPI app..."
uv run fastapi run src/api/main.py --proxy-headers --port 8000
