# TODO: refactor: split into subpackage
# this module bears too many responsibilities

import asyncio
import random
import secrets
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated, Final, NamedTuple

from fastapi import FastAPI, Header, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import StringConstraints

from lexica.names import DictionaryName
from wordcore.errors.exceptions import WordcoreError
from wordcore.games.game import Game
from wordcore.models.base import BaseFrozen
from wordcore.moves.move import Move
from wordcore.views.events import EventView
from wordcore.views.highlights import GameHighlights
from wordserver.describe import table_description, word_check_offered
from wordserver.errors.body import ErrorBody
from wordserver.errors.code import ErrorCode, code_for
from wordserver.errors.exceptions import SeatTokenMismatch, TableGathering
from wordserver.errors.refusal import Refusal, refusal_response
from wordserver.models.move_accepted import MoveAccepted
from wordserver.models.offerings import OfferingsResponse
from wordserver.models.table import TableViewResponse
from wordserver.models.table_admission import TableAdmission
from wordserver.models.table_description import TableDescription
from wordserver.models.table_time import TableTimeRequest
from wordserver.models.word_verdicts import WordVerdicts
from wordserver.registry import TableMeta, TableRegistry
from wordserver.session import TableSession
from wordtable.build import build_rules
from wordtable.catalog import ResolvedScheme, offerings, resolve_scheme
from wordtable.config import SchemeConfig, StyleTokens, TimeConfig, load_style_tokens, read_config
from wordtable.lexicons import LexiconService, dictionary_ready
from wordtable.paths import ASSETS_DIR, CONFIG_DIR, FRONTEND_DIST_DIR, RUN_CONFIG_FILE

MAX_PLAYER_NAME_LENGTH: Final = 32
MAX_JUDGED_WORDS: Final = 16

PlayerName = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=MAX_PLAYER_NAME_LENGTH),
]


class TableRequest(BaseFrozen):
    scheme: str
    seats: int
    name: PlayerName
    time: TableTimeRequest | None = None


class JoinRequest(BaseFrozen):
    name: PlayerName


class MoveRequest(BaseFrozen):
    move: Move
    base_seq: int
    premove: bool = False


_JOIN_ALPHABET: Final = "ABCDEFGHJKLMNPQRSTUVWXYZ"
_JOIN_CODE_LENGTH: Final = 6
_TOKEN_BYTES: Final = 16
_TABLE_ID_BYTES: Final = 8


class _TableIdentity(NamedTuple):
    table_id: str
    code: str
    tokens: dict[int, str]


def _new_join_code() -> str:
    return "".join(secrets.choice(_JOIN_ALPHABET) for _ in range(_JOIN_CODE_LENGTH))


def _resolved_offering(scheme_name: str) -> ResolvedScheme:
    try:
        return resolve_scheme(CONFIG_DIR, scheme_name)
    except WordcoreError as error:
        raise Refusal(404, str(error), ErrorCode.UNKNOWN_SCHEME) from error


def _ensure_seats_in_range(scheme: SchemeConfig, seats: int) -> None:
    if not scheme.min_players <= seats <= scheme.max_players:
        raise Refusal(
            422,
            "seats outside the scheme range",
            ErrorCode.SEATS_OUT_OF_RANGE,
        )


def _ensure_dictionary_available(dictionary: DictionaryName) -> None:
    if not dictionary_ready(dictionary):
        raise Refusal(
            422,
            f"dictionary '{dictionary}' is unavailable",
            ErrorCode.DICTIONARY_UNAVAILABLE,
        )


def _ensure_word_check_offered(scheme: SchemeConfig) -> None:
    if not word_check_offered(scheme):
        raise Refusal(
            422,
            "this table judges words on submission only",
            ErrorCode.WORD_CHECK_UNAVAILABLE,
        )


def _ensure_words_within_limit(words: tuple[str, ...]) -> None:
    if len(words) > MAX_JUDGED_WORDS:
        raise Refusal(
            422,
            f"at most {MAX_JUDGED_WORDS} words per request",
            ErrorCode.TOO_MANY_WORDS,
        )


def _canonical_words(words: list[str]) -> tuple[str, ...]:
    asked: dict[str, None] = {}
    for word in words:
        stripped = word.strip().upper()
        if stripped:
            asked[stripped] = None
    return tuple(asked)


async def _built_game(
    service: LexiconService,
    resolved: ResolvedScheme,
    seats: tuple[int, ...],
) -> Game:
    lexicon = await service.get(resolved.scheme.dictionary)
    rules = build_rules(resolved, seats, lexicon)
    return Game(
        rules,
        random.Random(),
        premoves_allowed=resolved.scheme.premoves,
    )


def _minted_identity(seats: int) -> _TableIdentity:
    return _TableIdentity(
        table_id=secrets.token_hex(_TABLE_ID_BYTES),
        code=_new_join_code(),
        tokens={seat: secrets.token_urlsafe(_TOKEN_BYTES) for seat in range(seats)},
    )


def _creator_names(seats: int, creator: str) -> dict[int, str | None]:
    names: dict[int, str | None] = {seat: None for seat in range(seats)}
    names[0] = creator
    return names


def _table_time(scheme: SchemeConfig, asked: TableTimeRequest | None) -> TimeConfig:
    if asked is None:
        return scheme.time

    return TimeConfig(
        per_turn_seconds=None,
        increment_seconds=asked.increment_seconds,
        total_seconds=asked.total_seconds,
    )


def _open_table(
    registry: TableRegistry,
    game: Game,
    resolved: ResolvedScheme,
    body: TableRequest,
) -> TableAdmission:
    identity = _minted_identity(body.seats)
    creator = body.name
    played_time = _table_time(resolved.scheme, body.time)
    meta = TableMeta(
        scheme=body.scheme,
        game=resolved.scheme.game,
        max_players=body.seats,
        code=identity.code,
        resolved=resolved,
        time=played_time,
    )
    session = TableSession(
        game,
        identity.tokens,
        played_time,
        _creator_names(body.seats, creator),
        time.time,
    )
    registry.add(identity.table_id, session, meta)
    registry.add_code(identity.code, identity.table_id)
    return _admission(
        identity.table_id,
        identity.code,
        meta,
        seat=0,
        token=identity.tokens[0],
        name=creator,
    )


def _table_for_code(
    registry: TableRegistry,
    code: str,
) -> tuple[str, TableSession, TableMeta]:
    table_id = registry.table_id_for_code(code.upper())
    if table_id is None:
        raise Refusal(404, "unknown table code", ErrorCode.UNKNOWN_CODE)

    session = registry.get(table_id)
    meta = registry.meta_for(table_id)
    if session is None or meta is None:
        raise Refusal(404, "unknown table", ErrorCode.UNKNOWN_TABLE)

    return table_id, session, meta


async def _claimed_seat(session: TableSession, name: str) -> tuple[int, str]:
    claimed = await session.claim(name)
    if claimed is None:
        raise Refusal(409, "table is full", ErrorCode.TABLE_FULL)

    return claimed


def _admission(
    table_id: str,
    code: str,
    meta: TableMeta,
    *,
    seat: int,
    token: str,
    name: str | None,
) -> TableAdmission:
    return TableAdmission(
        table_id=table_id,
        code=code,
        scheme=meta.scheme,
        game=meta.game,
        max_players=meta.max_players,
        seat=seat,
        token=token,
        name=name,
    )


def create_app() -> FastAPI:
    configuration = read_config(RUN_CONFIG_FILE)
    style_tokens = load_style_tokens(CONFIG_DIR, configuration.style)
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
    async def rejected(
        _request: Request,
        error: WordcoreError,
    ) -> JSONResponse:
        return refusal_response(409, str(error), code_for(error))

    @app.exception_handler(SeatTokenMismatch)
    async def mismatched(
        _request: Request,
        error: SeatTokenMismatch,
    ) -> JSONResponse:
        return refusal_response(409, str(error), ErrorCode.SEAT_TOKEN_MISMATCH)

    @app.exception_handler(TableGathering)
    async def still_gathering(
        _request: Request,
        error: TableGathering,
    ) -> JSONResponse:
        return refusal_response(409, str(error), ErrorCode.GATHERING)

    def session_for(table_id: str) -> TableSession:
        session = registry.get(table_id)
        if session is None:
            raise Refusal(404, "unknown table", ErrorCode.UNKNOWN_TABLE)
        return session

    def table_with_meta(table_id: str) -> tuple[TableSession, TableMeta]:
        session = registry.get(table_id)
        meta = registry.meta_for(table_id)
        if session is None or meta is None:
            raise Refusal(404, "unknown table", ErrorCode.UNKNOWN_TABLE)
        return session, meta

    @app.get("/offerings")
    def list_offerings() -> OfferingsResponse:
        ready = tuple(
            offering for offering in offerings(CONFIG_DIR) if dictionary_ready(offering.dictionary)
        )
        return OfferingsResponse(offerings=ready)

    @app.get("/style")
    def read_style() -> StyleTokens:
        return style_tokens

    @app.post(
        "/tables",
        responses={404: {"model": ErrorBody}, 422: {"model": ErrorBody}},
    )
    async def create_table(body: TableRequest) -> TableAdmission:
        resolved = _resolved_offering(body.scheme)
        _ensure_seats_in_range(resolved.scheme, body.seats)
        _ensure_dictionary_available(resolved.scheme.dictionary)
        game = await _built_game(service, resolved, tuple(range(body.seats)))
        return _open_table(registry, game, resolved, body)

    @app.post(
        "/tables/{code}/join",
        responses={404: {"model": ErrorBody}, 409: {"model": ErrorBody}},
    )
    async def join_table(code: str, body: JoinRequest) -> TableAdmission:
        table_id, session, meta = _table_for_code(registry, code)
        seat, token = await _claimed_seat(session, body.name)
        return _admission(
            table_id,
            code.upper(),
            meta,
            seat=seat,
            token=token,
            name=body.name,
        )

    @app.get("/tables/{table_id}", responses={404: {"model": ErrorBody}})
    def describe_table(table_id: str, request: Request) -> TableDescription:
        session, meta = table_with_meta(table_id)
        observer = session.observer_for(request.headers.get("X-Seat-Token"))
        return table_description(meta, observer)

    @app.get(
        "/tables/{table_id}/words",
        responses={404: {"model": ErrorBody}, 422: {"model": ErrorBody}},
    )
    async def judge_words(
        table_id: str,
        words: Annotated[list[str], Query()],
    ) -> WordVerdicts:
        _, meta = table_with_meta(table_id)
        scheme = meta.resolved.scheme
        _ensure_word_check_offered(scheme)
        asked = _canonical_words(words)
        _ensure_words_within_limit(asked)
        lexicon = await service.get(scheme.dictionary)
        return WordVerdicts(verdicts={word: lexicon.judge(word) for word in asked})

    @app.get("/tables/{table_id}/highlights", responses={404: {"model": ErrorBody}})
    def table_highlights(table_id: str) -> GameHighlights:
        return session_for(table_id).highlights()

    @app.get("/tables/{table_id}/view", responses={404: {"model": ErrorBody}})
    def table_view(table_id: str, request: Request) -> TableViewResponse:
        session = session_for(table_id)
        observer = session.observer_for(request.headers.get("X-Seat-Token"))
        return TableViewResponse(
            seq=session.seq,
            view=session.view(observer),
            company=session.company(),
            clock=session.clock(),
        )

    @app.post(
        "/tables/{table_id}/moves",
        responses={404: {"model": ErrorBody}, 409: {"model": ErrorBody}},
    )
    async def submit_move(
        table_id: str,
        body: MoveRequest,
        request: Request,
    ) -> MoveAccepted:
        session = session_for(table_id)
        token = request.headers.get("X-Seat-Token")
        seq = await session.submit(
            body.move,
            base_seq=body.base_seq,
            premove=body.premove,
            token=token,
        )
        return MoveAccepted(seq=seq)

    @app.delete(
        "/tables/{table_id}/premove",
        responses={404: {"model": ErrorBody}, 409: {"model": ErrorBody}},
    )
    async def cancel_premove(
        table_id: str,
        base_seq: int,
        request: Request,
    ) -> MoveAccepted:
        session = session_for(table_id)
        seq = await session.cancel_premove(
            base_seq,
            token=request.headers.get("X-Seat-Token"),
        )
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
        return StreamingResponse(
            session.events(observer, since),
            media_type="text/event-stream",
        )

    if ASSETS_DIR.is_dir():
        app.mount("/artwork", StaticFiles(directory=ASSETS_DIR), name="artwork")
        favicon = ASSETS_DIR / "icons" / "favicon.ico"
        if favicon.is_file():

            @app.get("/favicon.ico", include_in_schema=False)
            def serve_favicon() -> FileResponse:
                return FileResponse(favicon)

    if FRONTEND_DIST_DIR.is_dir():
        app.mount(
            "/assets",
            StaticFiles(directory=FRONTEND_DIST_DIR / "assets"),
            name="assets",
        )

        @app.get("/")
        def serve_index() -> FileResponse:
            return FileResponse(FRONTEND_DIST_DIR / "index.html")

        @app.get("/manifest.webmanifest", include_in_schema=False)
        def serve_manifest() -> FileResponse:
            return FileResponse(
                FRONTEND_DIST_DIR / "manifest.webmanifest",
                media_type="application/manifest+json",
            )

    return app
