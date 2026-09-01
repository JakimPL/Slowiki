# TODO: refactor: split into subpackage
# this module bears too many responsibilities

import asyncio
import random
import secrets
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated, Any, Final, NamedTuple

from fastapi import FastAPI, Header, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from lexica.names import DictionaryName
from wordcore.errors.exceptions import (
    InvalidConfiguration,
    MissingConfiguration,
    WordcoreError,
)
from wordcore.games.game import Game
from wordcore.views.events import EventView
from wordcore.views.highlights import GameHighlights
from wordserver.codes import join_code_shape, new_join_code
from wordserver.describe import lore_offered, table_description, word_check_offered
from wordserver.errors.body import ErrorBody
from wordserver.errors.code import ErrorCode, code_for
from wordserver.errors.exceptions import TableRefused
from wordserver.errors.gone import table_gone
from wordserver.errors.refusal import Refusal, refusal_response
from wordserver.errors.request import malformed_request
from wordserver.models.join_request import JoinRequest
from wordserver.models.move_accepted import MoveAccepted
from wordserver.models.move_request import MoveRequest
from wordserver.models.offerings import OfferingsResponse
from wordserver.models.presets import PresetsResponse
from wordserver.models.rack_request import RackRequest
from wordserver.models.table import TableViewResponse
from wordserver.models.table_admission import TableAdmission
from wordserver.models.table_description import TableDescription
from wordserver.models.table_meta import TableMeta
from wordserver.models.table_request import TableRequest
from wordserver.models.word_lore import WordLoreResponse
from wordserver.models.word_verdicts import WordVerdicts
from wordserver.records import KEPT_GAMES, GameBook
from wordserver.registry import TableRegistry
from wordserver.resuming import resume_point
from wordserver.session import TableSession
from wordserver.sweep import TableSweep
from wordtable.allowances.described import setting_allowances
from wordtable.audit import audit_configuration
from wordtable.build import build_rules
from wordtable.catalog import offerings, resolve_scheme
from wordtable.config import read_config
from wordtable.lexicons import LexiconService, dictionary_ready
from wordtable.limits import SettingOutOfRange
from wordtable.lore import LoreService, lore_ready
from wordtable.paths import (
    ASSETS_DIR,
    CONFIG_DIR,
    CONFIGURATION_ALPHABETS_PATH,
    CONFIGURATION_BOARDS_PATH,
    CONFIGURATION_DISTRIBUTIONS_PATH,
    FRONTEND_DIST_DIR,
    RUN_CONFIG_FILE,
)
from wordtable.presets.load import (
    list_presets,
    load_alphabet_preset,
    load_board_preset,
    load_distribution_preset,
)
from wordtable.resolved import ResolvedScheme
from wordtable.rules import RulesConfig
from wordtable.scheme import SchemeConfig, load_scheme
from wordtable.settling import resolve_table
from wordtable.style import StyleTokens, load_style_tokens
from wordtable.timing import time_of

MAX_JUDGED_WORDS: Final = 16

_TABLE_RESPONSES: Final[dict[int | str, dict[str, Any]]] = {
    404: {"model": ErrorBody},
    410: {"model": ErrorBody},
}
_PLAY_RESPONSES: Final[dict[int | str, dict[str, Any]]] = {
    **_TABLE_RESPONSES,
    409: {"model": ErrorBody},
}

_TOKEN_BYTES: Final = 16
_TABLE_ID_BYTES: Final = 8


class _TableIdentity(NamedTuple):
    table_id: str
    code: str
    tokens: dict[int, str]


def _offered_scheme(scheme_name: str) -> SchemeConfig:
    try:
        return load_scheme(CONFIG_DIR, scheme_name)
    except WordcoreError as error:
        raise Refusal(404, str(error), ErrorCode.UNKNOWN_SCHEME) from error


def _settled_table(scheme: SchemeConfig, asked: RulesConfig | None) -> ResolvedScheme:
    try:
        return resolve_table(CONFIG_DIR, scheme, asked)
    except MissingConfiguration as error:
        raise Refusal(422, str(error), ErrorCode.UNKNOWN_PRESET) from error
    except SettingOutOfRange as error:
        raise Refusal(422, str(error), ErrorCode.SETTING_OUT_OF_RANGE) from error
    except InvalidConfiguration as error:
        raise Refusal(422, str(error), ErrorCode.RULES_INCONSISTENT) from error


def _ensure_dictionary_available(dictionary: DictionaryName) -> None:
    if not dictionary_ready(dictionary):
        raise Refusal(
            422,
            f"dictionary '{dictionary}' is unavailable",
            ErrorCode.DICTIONARY_UNAVAILABLE,
        )


def _ensure_word_check_offered(rules: RulesConfig) -> None:
    if not word_check_offered(rules):
        raise Refusal(
            422,
            "this table judges words on submission only",
            ErrorCode.WORD_CHECK_UNAVAILABLE,
        )


def _ensure_lore_offered(rules: RulesConfig) -> None:
    if not lore_offered(rules):
        raise Refusal(
            422,
            "this table serves no dictionary readings",
            ErrorCode.LORE_UNAVAILABLE,
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
    lexicon = await service.get(resolved.rules.dictionary)
    rules = build_rules(resolved, seats, lexicon)
    return Game(
        rules,
        random.Random(),
        premoves_allowed=resolved.rules.premoves,
    )


async def _warmed(
    service: LexiconService,
    lore: LoreService,
    dictionary: DictionaryName,
) -> None:
    await service.get(dictionary)
    if lore_ready(dictionary):
        await lore.prepare(dictionary)


def _minted_identity(seats: int) -> _TableIdentity:
    return _TableIdentity(
        table_id=secrets.token_hex(_TABLE_ID_BYTES),
        code=new_join_code(),
        tokens={seat: secrets.token_urlsafe(_TOKEN_BYTES) for seat in range(seats)},
    )


def _creator_names(seats: int, creator: str) -> dict[int, str | None]:
    names: dict[int, str | None] = {seat: None for seat in range(seats)}
    names[0] = creator
    return names


def _open_table(
    registry: TableRegistry,
    game: Game,
    resolved: ResolvedScheme,
    creator: str,
    premove_delay_seconds: float,
) -> TableAdmission:
    seats = resolved.rules.seats
    identity = _minted_identity(seats)
    played_time = time_of(resolved.rules)
    meta = TableMeta(
        code=identity.code,
        resolved=resolved,
        time=played_time,
    )
    session = TableSession(
        game,
        identity.tokens,
        played_time,
        _creator_names(seats, creator),
        time.time,
        premove_delay_seconds=premove_delay_seconds,
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
        raise table_gone(registry.record_for(table_id))

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
        scheme=meta.resolved.scheme,
        seats=meta.resolved.rules.seats,
        seat=seat,
        token=token,
        name=name,
    )


def create_app() -> FastAPI:
    audit_configuration(CONFIG_DIR)
    configuration = read_config(RUN_CONFIG_FILE)
    style_tokens = load_style_tokens(CONFIG_DIR, configuration.style)
    service = LexiconService()
    lore = LoreService(service)
    registry = TableRegistry(GameBook(KEPT_GAMES))
    sweep = TableSweep(registry, configuration.tables, time.time)

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        default = resolve_scheme(CONFIG_DIR, configuration.scheme)
        preload = asyncio.create_task(_warmed(service, lore, default.rules.dictionary))
        sweeping = asyncio.create_task(sweep.run())
        yield
        preload.cancel()
        sweeping.cancel()

    app = FastAPI(title="slowiki", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(Refusal)
    async def refused(_request: Request, error: Refusal) -> JSONResponse:
        return refusal_response(error.status_code, error.detail, error.code)

    @app.exception_handler(RequestValidationError)
    async def malformed(
        _request: Request,
        error: RequestValidationError,
    ) -> JSONResponse:
        refusal = malformed_request(error)
        return refusal_response(refusal.status_code, refusal.detail, refusal.code)

    @app.exception_handler(WordcoreError)
    async def rejected(
        _request: Request,
        error: WordcoreError,
    ) -> JSONResponse:
        return refusal_response(409, str(error), code_for(error))

    @app.exception_handler(TableRefused)
    async def table_refused(
        _request: Request,
        error: TableRefused,
    ) -> JSONResponse:
        return refusal_response(409, str(error), error.code)

    def session_for(table_id: str) -> TableSession:
        session = registry.get(table_id)
        if session is None:
            raise table_gone(registry.record_for(table_id))
        return session

    def table_with_meta(table_id: str) -> tuple[TableSession, TableMeta]:
        session = registry.get(table_id)
        meta = registry.meta_for(table_id)
        if session is None or meta is None:
            raise table_gone(registry.record_for(table_id))
        return session, meta

    @app.get("/offerings")
    def list_offerings() -> OfferingsResponse:
        ready = tuple(
            offering
            for offering in offerings(CONFIG_DIR)
            if dictionary_ready(offering.rules.dictionary)
        )
        return OfferingsResponse(
            offerings=ready,
            code=join_code_shape(),
            allowances=setting_allowances(CONFIG_DIR),
        )

    @app.get("/presets")
    def list_offered_presets() -> PresetsResponse:
        return PresetsResponse(
            boards=tuple(
                load_board_preset(CONFIG_DIR, name)
                for name in list_presets(CONFIG_DIR, CONFIGURATION_BOARDS_PATH)
            ),
            alphabets=tuple(
                load_alphabet_preset(CONFIG_DIR, name)
                for name in list_presets(CONFIG_DIR, CONFIGURATION_ALPHABETS_PATH)
            ),
            distributions=tuple(
                load_distribution_preset(CONFIG_DIR, name)
                for name in list_presets(CONFIG_DIR, CONFIGURATION_DISTRIBUTIONS_PATH)
            ),
        )

    @app.get("/style")
    def read_style() -> StyleTokens:
        return style_tokens

    @app.post(
        "/tables",
        responses={404: {"model": ErrorBody}, 422: {"model": ErrorBody}},
    )
    async def create_table(body: TableRequest) -> TableAdmission:
        scheme = _offered_scheme(body.scheme)
        resolved = _settled_table(scheme, body.rules)
        _ensure_dictionary_available(resolved.rules.dictionary)
        game = await _built_game(service, resolved, tuple(range(resolved.rules.seats)))
        return _open_table(
            registry,
            game,
            resolved,
            body.name,
            configuration.tables.premove_delay_seconds,
        )

    @app.post("/tables/{code}/join", responses=_PLAY_RESPONSES)
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

    @app.get("/invitations/{code}", responses=_TABLE_RESPONSES)
    def read_invitation(code: str) -> TableDescription:
        _, _, meta = _table_for_code(registry, code)
        return table_description(meta, observer=None)

    @app.get("/tables/{table_id}", responses=_TABLE_RESPONSES)
    def describe_table(table_id: str, request: Request) -> TableDescription:
        session, meta = table_with_meta(table_id)
        observer = session.observer_for(request.headers.get("X-Seat-Token"))
        return table_description(meta, observer)

    @app.get(
        "/tables/{table_id}/words",
        responses={**_TABLE_RESPONSES, 422: {"model": ErrorBody}},
    )
    async def judge_words(
        table_id: str,
        words: Annotated[list[str], Query()],
    ) -> WordVerdicts:
        _, meta = table_with_meta(table_id)
        rules = meta.resolved.rules
        _ensure_word_check_offered(rules)
        asked = _canonical_words(words)
        _ensure_words_within_limit(asked)
        lexicon = await service.get(rules.dictionary)
        return WordVerdicts(verdicts={word: lexicon.judge(word) for word in asked})

    @app.get(
        "/tables/{table_id}/lore",
        responses={**_TABLE_RESPONSES, 422: {"model": ErrorBody}},
    )
    async def read_lore(
        table_id: str,
        words: Annotated[list[str], Query()],
    ) -> WordLoreResponse:
        _, meta = table_with_meta(table_id)
        rules = meta.resolved.rules
        _ensure_lore_offered(rules)
        asked = _canonical_words(words)
        _ensure_words_within_limit(asked)
        return WordLoreResponse(lore=await lore.read(rules.dictionary, asked))

    @app.get("/tables/{table_id}/highlights", responses=_TABLE_RESPONSES)
    def table_highlights(table_id: str) -> GameHighlights:
        return session_for(table_id).highlights()

    @app.get("/tables/{table_id}/view", responses=_TABLE_RESPONSES)
    def table_view(table_id: str, request: Request) -> TableViewResponse:
        session = session_for(table_id)
        observer = session.observer_for(request.headers.get("X-Seat-Token"))
        return TableViewResponse(
            seq=session.seq,
            view=session.view(observer),
            company=session.company(),
            clock=session.clock(),
        )

    @app.post("/tables/{table_id}/moves", responses=_PLAY_RESPONSES)
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

    @app.put("/tables/{table_id}/rack", status_code=204, responses=_PLAY_RESPONSES)
    async def arrange_rack(
        table_id: str,
        body: RackRequest,
        request: Request,
    ) -> None:
        session = session_for(table_id)
        await session.arrange_rack(
            body.tile_ids,
            token=request.headers.get("X-Seat-Token"),
        )

    @app.delete("/tables/{table_id}/premove", responses=_PLAY_RESPONSES)
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
        responses={200: {"model": EventView}, **_TABLE_RESPONSES},
    )
    def stream_events(
        table_id: str,
        request: Request,
        last_event_id: str | None = Header(default=None, alias="Last-Event-ID"),
    ) -> StreamingResponse:
        session = session_for(table_id)
        observer = session.observer_for(request.headers.get("X-Seat-Token"))
        since = resume_point(last_event_id)
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
