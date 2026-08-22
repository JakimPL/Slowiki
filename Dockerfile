FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS build

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

WORKDIR /app

RUN apt-get update \
    && apt-get install --no-install-recommends -y ca-certificates curl gnupg \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install --no-install-recommends -y nodejs \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN mkdir -p dictionaries \
    && curl -fsSL -o dictionaries/sjp-20260803.zip https://sjp.pl/sl/growy/sjp-20260803.zip

RUN uv sync --extra server --no-group dev

RUN uv run python -m wordtable.cli dictionary --name sjp \
    && uv run python scripts/openapi.py \
    && uv run python scripts/strings.py \
    && uv run python -m wordassets.cli build --output assets

RUN npm install \
    && npm run types --workspace frontend \
    && npm run build --workspace frontend


FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

ENV VIRTUAL_ENV=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src"
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY --from=build /app/.venv /app/.venv
COPY --from=build /app/src /app/src
COPY --from=build /app/config /app/config
COPY --from=build /app/dictionaries /app/dictionaries
COPY --from=build /app/assets /app/assets
COPY --from=build /app/build/frontend /app/build/frontend

CMD python -m wordtable.cli serve --host 0.0.0.0 --port "${PORT:-8000}"
