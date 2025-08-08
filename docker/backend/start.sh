#!/bin/bash
set -e

echo "Running Alembic migrations..."
uv run --no-sync alembic upgrade head

echo "Starting FastAPI app..."
uv run --no-sync fastapi run src/api/main.py --proxy-headers --port 8000
