.PHONY: install check test play serve types assets frontend

install:
	uv sync --all-extras --all-groups
	uv run pre-commit install

check:
	uv run pre-commit run --all-files
	uv run mypy src
	uv run pylint src
	uv run lint-imports
	uv run pytest --cov=wordcore --cov=wordgames --cov=wordserver --cov=wordtable --cov=wordassets --cov=lexica --cov=wordbots --cov-fail-under=80

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

frontend:
	cd frontend && npm install && npm run build
