import asyncio
import random
import secrets
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any, Final

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from wordcore.exceptions import WordcoreError
from wordcore.games.game import Game
from wordcore.models.base import BaseFrozen
from wordcore.moves.action import Move
from wordserver.registry import TableRegistry
from wordserver.session import TableSession
from wordtable.build import build_rules
from wordtable.catalogue import offerings, resolve_scheme
from wordtable.config import load_style, read_config
from wordtable.lexicons import LexiconService
from wordtable.paths import CONFIG_DIR, FRONTEND_DIST_DIR, RUN_CONFIG_FILE


class TableRequest(BaseFrozen):
    scheme: str
    seats: int


class MoveRequest(BaseFrozen):
    move: Move
    base_seq: int
    premove: bool = False


_JOIN_ALPHABET: Final = "ABCDEFGHJKLMNPQRSTUVWXYZ"


def _new_join_code() -> str:
    return "".join(secrets.choice(_JOIN_ALPHABET) for _ in range(6))


def create_app() -> FastAPI:
    configuration = read_config(RUN_CONFIG_FILE)
    style = load_style(CONFIG_DIR, configuration.style)
    service = LexiconService()
    registry = TableRegistry()

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        default = resolve_scheme(CONFIG_DIR, configuration.scheme)
        preload = asyncio.create_task(service.get(default.scheme.dictionary))
        yield
        preload.cancel()

    app = FastAPI(title="literabble", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/offerings")
    def list_offerings() -> dict[str, Any]:
        listed = [offering.model_dump(mode="json") for offering in offerings(CONFIG_DIR)]
        return {"offerings": listed}

    @app.post("/tables")
    async def create_table(body: TableRequest) -> dict[str, Any]:
        try:
            resolved = resolve_scheme(CONFIG_DIR, body.scheme)
        except WordcoreError as error:
            raise HTTPException(status_code=404, detail=str(error)) from error
        if not resolved.scheme.min_players <= body.seats <= resolved.scheme.max_players:
            raise HTTPException(status_code=422, detail="seats outside the scheme range")
        lexicon = await service.get(resolved.scheme.dictionary)
        seats = tuple(range(body.seats))
        rules = build_rules(resolved, seats, lexicon)
        game = Game(rules, random.Random())
        tokens = {seat: secrets.token_urlsafe(16) for seat in seats}
        table_id = secrets.token_hex(8)
        code = _new_join_code()
        meta = {"scheme": body.scheme, "game": resolved.scheme.game, "max_players": body.seats}
        registry.add(table_id, TableSession(game, tokens, resolved.scheme.time), meta)
        registry.add_code(code, table_id)
        return {
            "table_id": table_id,
            "code": code,
            "scheme": body.scheme,
            "game": resolved.scheme.game,
            "max_players": body.seats,
            "seat": 0,
            "token": tokens[0],
        }

    @app.post("/tables/{code}/join")
    def join_table(code: str) -> dict[str, Any]:
        table_id = registry.table_id_for_code(code.upper())
        if table_id is None:
            raise HTTPException(status_code=404, detail="unknown table code")
        session = registry.get(table_id)
        meta = registry.meta_for(table_id)
        if session is None or meta is None:
            raise HTTPException(status_code=404, detail="unknown table")
        claimed = session.claim_seat()
        if claimed is None:
            raise HTTPException(status_code=409, detail="table is full")
        seat, token = claimed
        return {"table_id": table_id, "code": code.upper(), **meta, "seat": seat, "token": token}

    @app.get("/tables/{table_id}/view")
    def table_view(table_id: str, request: Request) -> dict[str, Any]:
        session = registry.get(table_id)
        if session is None:
            raise HTTPException(status_code=404, detail="unknown table")
        token = request.headers.get("X-Seat-Token")
        observer = session.observer_for(token)
        payload = {
            "seq": session.seq,
            "style": style.model_dump(mode="json"),
            "view": session.view(observer),
        }
        return payload

    @app.post("/tables/{table_id}/moves")
    async def submit_move(table_id: str, body: MoveRequest, request: Request) -> dict[str, Any]:
        session = registry.get(table_id)
        if session is None:
            raise HTTPException(status_code=404, detail="unknown table")
        token = request.headers.get("X-Seat-Token")
        try:
            await session.submit(body.move, body.base_seq, body.premove, token)
        except WordcoreError as error:
            raise HTTPException(status_code=409, detail=str(error)) from error
        return {"seq": session.seq}

    @app.get("/tables/{table_id}/events")
    def stream_events(
        table_id: str,
        request: Request,
        last_event_id: str | None = Header(default=None, alias="Last-Event-ID"),
    ) -> StreamingResponse:
        session = registry.get(table_id)
        if session is None:
            raise HTTPException(status_code=404, detail="unknown table")
        token = request.headers.get("X-Seat-Token")
        observer = session.observer_for(token)
        since = int(last_event_id) + 1 if last_event_id else 0
        return StreamingResponse(session.events(observer, since), media_type="text/event-stream")

    if FRONTEND_DIST_DIR.is_dir():
        app.mount("/assets", StaticFiles(directory=FRONTEND_DIST_DIR / "assets"), name="assets")

        @app.get("/")
        def serve_index() -> FileResponse:
            return FileResponse(FRONTEND_DIST_DIR / "index.html")

    return app
