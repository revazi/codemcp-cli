set shell := ["bash", "-euo", "pipefail", "-c"]
set quiet

default: check

lock:
    uv lock

sync:
    uv sync --frozen --all-groups

format:
    uv run ruff format src/codemcp_cli tests/python tests/fixtures
    uv run ruff check --fix src/codemcp_cli tests/python tests/fixtures

check-lock:
    uv lock --check

format-check:
    uv run ruff format --check src/codemcp_cli tests/python tests/fixtures

lint:
    uv run ruff check src/codemcp_cli tests/python tests/fixtures

typecheck:
    uv run mypy src/codemcp_cli tests/python/test_executor.py tests/python/test_settings.py tests/python/test_cli.py
    uv run ty check --project . src/codemcp_cli tests/python/test_executor.py tests/python/test_settings.py tests/python/test_cli.py

test:
    uv run pytest tests/python --cov=codemcp_cli --cov-branch --cov-report=term-missing -q

package-check:
    tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT; \
        uv build --out-dir "$tmp"; \
        uv run twine check "$tmp"/*; \
        uv run check-wheel-contents "$tmp"/*.whl

check: check-lock format-check lint typecheck test package-check
