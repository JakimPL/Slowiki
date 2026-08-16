import random
import secrets
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from wordcore.exceptions import WordcoreError
from wordcore.games.game import Game
from wordcore.models.base import BaseFrozen
from wordcore.moves.action import Move
from wordserver.registry import TableRegistry
from wordserver.session import TableSession
from wordtable.build import build_rules
from wordtable.catalogue import offerings, resolve_scheme
from wordtable.config import StyleConfig
from wordtable.lexicons import load_lexicon


class TableRequest(BaseFrozen):
    scheme: str
    seats: int


class MoveRequest(BaseFrozen):
    move: Move
    base_seq: int
    premove: bool = False


def create_app(config_dir: Path, dictionaries_dir: Path, style: StyleConfig) -> FastAPI:
    registry = TableRegistry()
    app = FastAPI(title="literabble")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/offerings")
    def list_offerings() -> dict[str, Any]:
        listed = [offering.model_dump(mode="json") for offering in offerings(config_dir)]
        return {"offerings": listed}

    @app.post("/tables")
    def create_table(body: TableRequest) -> dict[str, Any]:
        try:
            resolved = resolve_scheme(config_dir, body.scheme)
        except WordcoreError as error:
            raise HTTPException(status_code=404, detail=str(error)) from error
        if not resolved.scheme.min_players <= body.seats <= resolved.scheme.max_players:
            raise HTTPException(status_code=422, detail="seats outside the scheme range")
        lexicon = load_lexicon(resolved.scheme.dictionary, dictionaries_dir)
        seats = tuple(range(body.seats))
        rules = build_rules(resolved, seats, lexicon)
        game = Game(rules, random.Random())
        tokens = {seat: secrets.token_urlsafe(16) for seat in seats}
        table_id = secrets.token_hex(8)
        registry.add(table_id, TableSession(game, tokens, resolved.scheme.time))
        return {
            "table_id": table_id,
            "scheme": body.scheme,
            "game": resolved.scheme.game,
            "seats": [{"seat": seat, "token": tokens[seat]} for seat in seats],
        }

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

    return app
