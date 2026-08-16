import asyncio
import random
import secrets
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Final

from fastapi import FastAPI, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import Field

from wordcore.exceptions import WordcoreError
from wordcore.games.game import Game
from wordcore.models.base import BaseFrozen
from wordcore.moves.action import Move
from wordcore.views.events import EventView
from wordserver.errors import (
    ErrorBody,
    ErrorCode,
    Refusal,
    SeatTokenMismatch,
    code_for,
    refusal_response,
)
from wordserver.models import (
    MoveAccepted,
    OfferingsResponse,
    TableAdmission,
    TableViewResponse,
)
from wordserver.registry import TableMeta, TableRegistry
from wordserver.session import TableSession
from wordtable.build import build_rules
from wordtable.catalogue import offerings, resolve_scheme
from wordtable.config import StyleTokens, legacy_style, load_style_tokens, read_config
from wordtable.lexicons import LexiconService
from wordtable.paths import CONFIG_DIR, FRONTEND_DIST_DIR, RUN_CONFIG_FILE

MAX_PLAYER_NAME_LENGTH: Final = 32


class TableRequest(BaseFrozen):
    scheme: str
    seats: int
    name: str | None = Field(default=None, max_length=MAX_PLAYER_NAME_LENGTH)


class JoinRequest(BaseFrozen):
    name: str | None = Field(default=None, max_length=MAX_PLAYER_NAME_LENGTH)


class MoveRequest(BaseFrozen):
    move: Move
    base_seq: int
    premove: bool = False


_JOIN_ALPHABET: Final = "ABCDEFGHJKLMNPQRSTUVWXYZ"
_JOIN_CODE_LENGTH: Final = 6
_TOKEN_BYTES: Final = 16
_TABLE_ID_BYTES: Final = 8


def _new_join_code() -> str:
    return "".join(secrets.choice(_JOIN_ALPHABET) for _ in range(_JOIN_CODE_LENGTH))


def _cleaned_name(name: str | None) -> str | None:
    if name is None:
        return None
    stripped = name.strip()
    return stripped if stripped else None


def create_app() -> FastAPI:
    configuration = read_config(RUN_CONFIG_FILE)
    style_tokens = load_style_tokens(CONFIG_DIR, configuration.style)
    style = legacy_style(style_tokens)
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

    @app.exception_handler(Refusal)
    async def refused(_request: Request, error: Refusal) -> JSONResponse:
        return refusal_response(error.status_code, error.detail, error.code)

    @app.exception_handler(WordcoreError)
    async def rejected(_request: Request, error: WordcoreError) -> JSONResponse:
        return refusal_response(409, str(error), code_for(error))

    @app.exception_handler(SeatTokenMismatch)
    async def mismatched(_request: Request, error: SeatTokenMismatch) -> JSONResponse:
        return refusal_response(409, str(error), ErrorCode.SEAT_TOKEN_MISMATCH)

    def session_for(table_id: str) -> TableSession:
        session = registry.get(table_id)
        if session is None:
            raise Refusal(404, "unknown table", ErrorCode.UNKNOWN_TABLE)
        return session

    @app.get("/offerings")
    def list_offerings() -> OfferingsResponse:
        return OfferingsResponse(offerings=offerings(CONFIG_DIR))

    @app.get("/style")
    def read_style() -> StyleTokens:
        return style_tokens

    @app.post("/tables", responses={404: {"model": ErrorBody}, 422: {"model": ErrorBody}})
    async def create_table(body: TableRequest) -> TableAdmission:
        try:
            resolved = resolve_scheme(CONFIG_DIR, body.scheme)
        except WordcoreError as error:
            raise Refusal(404, str(error), ErrorCode.UNKNOWN_SCHEME) from error
        if not resolved.scheme.min_players <= body.seats <= resolved.scheme.max_players:
            raise Refusal(422, "seats outside the scheme range", ErrorCode.SEATS_OUT_OF_RANGE)
        lexicon = await service.get(resolved.scheme.dictionary)
        seats = tuple(range(body.seats))
        rules = build_rules(resolved, seats, lexicon)
        game = Game(rules, random.Random(), premoves_allowed=resolved.scheme.premoves)
        tokens = {seat: secrets.token_urlsafe(_TOKEN_BYTES) for seat in seats}
        table_id = secrets.token_hex(_TABLE_ID_BYTES)
        code = _new_join_code()
        creator = _cleaned_name(body.name)
        names: dict[int, str | None] = {seat: None for seat in seats}
        names[0] = creator
        meta = TableMeta(scheme=body.scheme, game=resolved.scheme.game, max_players=body.seats)
        registry.add(table_id, TableSession(game, tokens, resolved.scheme.time, names), meta)
        registry.add_code(code, table_id)
        return TableAdmission(
            table_id=table_id,
            code=code,
            scheme=meta.scheme,
            game=meta.game,
            max_players=meta.max_players,
            seat=0,
            token=tokens[0],
            name=creator,
        )

    @app.post(
        "/tables/{code}/join",
        responses={404: {"model": ErrorBody}, 409: {"model": ErrorBody}},
    )
    async def join_table(code: str, body: JoinRequest | None = None) -> TableAdmission:
        table_id = registry.table_id_for_code(code.upper())
        if table_id is None:
            raise Refusal(404, "unknown table code", ErrorCode.UNKNOWN_CODE)
        session = registry.get(table_id)
        meta = registry.meta_for(table_id)
        if session is None or meta is None:
            raise Refusal(404, "unknown table", ErrorCode.UNKNOWN_TABLE)
        name = _cleaned_name(body.name if body is not None else None)
        claimed = await session.claim(name)
        if claimed is None:
            raise Refusal(409, "table is full", ErrorCode.TABLE_FULL)
        seat, token = claimed
        return TableAdmission(
            table_id=table_id,
            code=code.upper(),
            scheme=meta.scheme,
            game=meta.game,
            max_players=meta.max_players,
            seat=seat,
            token=token,
            name=name,
        )

    @app.get("/tables/{table_id}/view", responses={404: {"model": ErrorBody}})
    def table_view(table_id: str, request: Request) -> TableViewResponse:
        session = session_for(table_id)
        observer = session.observer_for(request.headers.get("X-Seat-Token"))
        return TableViewResponse(
            seq=session.seq,
            style=style,
            view=session.view(observer),
            company=session.company(),
        )

    @app.post(
        "/tables/{table_id}/moves",
        responses={404: {"model": ErrorBody}, 409: {"model": ErrorBody}},
    )
    async def submit_move(table_id: str, body: MoveRequest, request: Request) -> MoveAccepted:
        session = session_for(table_id)
        token = request.headers.get("X-Seat-Token")
        seq = await session.submit(body.move, body.base_seq, body.premove, token)
        return MoveAccepted(seq=seq)

    @app.delete(
        "/tables/{table_id}/premove",
        responses={404: {"model": ErrorBody}, 409: {"model": ErrorBody}},
    )
    async def cancel_premove(table_id: str, base_seq: int, request: Request) -> MoveAccepted:
        session = session_for(table_id)
        seq = await session.cancel_premove(base_seq, request.headers.get("X-Seat-Token"))
        return MoveAccepted(seq=seq)

    @app.get(
        "/tables/{table_id}/events",
        responses={200: {"model": EventView}, 404: {"model": ErrorBody}},
    )
    def stream_events(
        table_id: str,
        request: Request,
        last_event_id: str | None = Header(default=None, alias="Last-Event-ID"),
    ) -> StreamingResponse:
        session = session_for(table_id)
        observer = session.observer_for(request.headers.get("X-Seat-Token"))
        since = int(last_event_id) + 1 if last_event_id else 0
        return StreamingResponse(session.events(observer, since), media_type="text/event-stream")

    if FRONTEND_DIST_DIR.is_dir():
        app.mount("/assets", StaticFiles(directory=FRONTEND_DIST_DIR / "assets"), name="assets")

        @app.get("/")
        def serve_index() -> FileResponse:
            return FileResponse(FRONTEND_DIST_DIR / "index.html")

    return app
