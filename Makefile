.PHONY: install check test play serve types assets frontend build

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
	npm install
	npm run build --workspace frontend

build:
	uv sync --all-extras --all-groups
	@if test -f dictionaries/sjp-20260803.zip && ! test -f dictionaries/sjp-20260803.lexicon; then uv run python -m lexica.cli compile dictionaries/sjp-20260803.zip dictionaries/sjp-20260803.lexicon; fi
	npm install
	npm run build --workspace frontend
