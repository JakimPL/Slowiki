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

ARG SJP_URL=https://sjp.pl/sl/growy/sjp-20260803.zip
ARG SJP_SHA256=b63105572873a043767380da3bdfe641231107834736eed0617dae39c523ff10
ARG POLIMORF_URL=https://download.sgjp.pl/morfeusz/20260726/polimorf-20260726.tab.gz
ARG POLIMORF_SHA256=d0315301beb4820577c8e04c885044feb852a72c865ce62e5e0a1836344e078e

RUN mkdir -p dictionaries/sources \
    && curl -fsSL -o dictionaries/sjp-20260803.zip "${SJP_URL}" \
    && echo "${SJP_SHA256}  dictionaries/sjp-20260803.zip" | sha256sum -c - \
    && curl -fsSL -o dictionaries/sources/polimorf-20260726.tab.gz "${POLIMORF_URL}" \
    && echo "${POLIMORF_SHA256}  dictionaries/sources/polimorf-20260726.tab.gz" | sha256sum -c -

RUN uv sync --extra server --extra morphology --no-group dev

RUN uv run python -m wordtable.cli dictionary --name sjp \
    && uv run python -m wordtable.cli rescue --name sjp \
    && rm -rf dictionaries/sources \
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
