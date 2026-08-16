.PHONY: install check test play serve types assets

install:
	uv sync --all-extras --all-groups
	uv run pre-commit install

check:
	uv run pre-commit run --all-files
	uv run mypy src
	uv run pylint src
	uv run pytest

test:
	uv run pytest

play:
	uv run python -m wordtable.cli play

serve:
	uv run python -m wordtable.cli serve

types:
	uv run python scripts/openapi.py

assets:
	uv run python -m wordassets.cli render
