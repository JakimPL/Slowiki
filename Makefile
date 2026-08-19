.PHONY: install check test play serve types strings contract parity assets frontend build dictionary

install:
	uv sync --all-extras --all-groups
	uv run pre-commit install --hook-type pre-commit --hook-type pre-push
	npm install

dictionary:
	uv run python -m wordtable.cli dictionary --name sjp

check:
	uv run pre-commit run --all-files
	uv run mypy src scripts
	uv run pylint src scripts
	uv run lint-imports
	uv run pytest --cov=wordcore --cov=wordgames --cov=wordserver --cov=wordtable --cov=lexica --cov=wordbots --cov=wordassets --cov-fail-under=80

test:
	uv run pytest

play:
	uv run python -m wordtable.cli play

serve:
	uv run python -m wordtable.cli serve

types:
	uv run python scripts/openapi.py
	npm run types --workspace frontend

strings:
	uv run python scripts/strings.py

contract:
	uv run python -m scripts.contract

parity:
	uv run python -m scripts.parity

assets:
	uv run python -m wordassets.cli build --output assets --docs docs/media

frontend:
	npm install
	npm run build --workspace frontend

build: install dictionary types strings assets frontend
