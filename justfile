set shell := ["bash", "-euo", "pipefail", "-c"]
set quiet

default: check

lock:
    uv lock

sync:
    uv sync --frozen --all-groups

format:
    uv run ruff format src/codemcp tests/python tests/fixtures
    uv run ruff check --fix src/codemcp tests/python tests/fixtures

check-lock:
    uv lock --check

format-check:
    uv run ruff format --check src/codemcp tests/python tests/fixtures

lint:
    uv run ruff check src/codemcp tests/python tests/fixtures

typecheck:
    uv run mypy src/codemcp tests/python/test_executor.py tests/python/test_settings.py tests/python/test_cli.py
    uv run ty check --project . src/codemcp tests/python/test_executor.py tests/python/test_settings.py tests/python/test_cli.py

test:
    uv run pytest tests/python -q

check: check-lock format-check lint typecheck test
