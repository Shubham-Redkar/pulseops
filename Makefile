.DEFAULT_GOAL := help

.PHONY: install run test lint format typecheck check clean

install:
	uv sync

run:
	uv run uvicorn app.main:app --reload

test:
	uv run pytest

lint:
	uv run ruff check .

format:
	uv run ruff format .

typecheck:
	uv run pyright

check:
	uv run ruff check .
	uv run ruff format --check .
	uv run python -m pytest

clean:
	find . -type d \( \
		-name "__pycache__" -o \
		-name ".ruff_cache" -o \
		-name ".pytest_cache" \
	\) -prune -exec rm -rf {} +

help:
	@echo "make install    - Install dependencies"
	@echo "make run        - Run FastAPI server"
	@echo "make test       - Run tests"
	@echo "make lint       - Lint code"
	@echo "make format     - Format code"
	@echo "make check      - Lint, format check, and test"
	@echo "make typecheck  - Run Pyright"
	@echo "make clean      - Remove Python/tool caches"