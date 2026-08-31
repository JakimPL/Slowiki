import asyncio
import json
import random
from typing import Any, Final

import httpx
import pytest
from tests.fixtures.rules import seated, stated

from lexica.names import DictionaryName
from wordcore.errors.rejections import RejectionCode
from wordcore.games.game import Game
from wordcore.games.kind import EntryKind
from wordcore.lexicon.lexicon import TextLexicon
from wordcore.moves.action import Exchange, Pass
from wordcore.moves.kind import ActionKind
from wordcore.moves.move import Move
from wordcore.states.phase import Phase
from wordserver.app import create_app
from wordserver.errors.code import ErrorCode
from wordserver.errors.exceptions import OutOfTime
from wordserver.errors.gone import table_gone
from wordserver.models.table_meta import TableMeta
from wordserver.records import KEPT_GAMES, GameBook
from wordserver.registry import TableRegistry
from wordserver.session import TableSession
from wordserver.sweep import TableSweep
from wordtable.build import build_rules
from wordtable.catalog import resolve_scheme
from wordtable.config import TablesConfig
from wordtable.paths import CONFIG_DIR
from wordtable.resolved import ResolvedScheme
from wordtable.rules import restated
from wordtable.scheme import load_scheme
from wordtable.settling import resolve_table
from wordtable.timing import TimeConfig, time_of

_PREMOVE_DELAY: Final = 0.05
_PATIENT_DELAY: Final = 5.0
_SHORTEST_BUDGET: Final = 1
_PAST_THE_BUDGET: Final = 1.1


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
async def client(app):
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


async def test_offerings_list_ready_dictionaries(
    client: httpx.AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        "wordserver.app.dictionary_ready",
        lambda name: name == DictionaryName.SJP,
    )
    response = await client.get("/offerings")
    assert response.status_code == 200
    served = response.json()["offerings"]
    names = {offering["name"] for offering in served}
    assert {"literaki", "solo-literaki"} <= names
    assert "scrabble" not in names
    assert all(offering["rules"]["dictionary"] == "sjp" for offering in served)


async def test_offerings_serve_the_join_code_shape(client: httpx.AsyncClient) -> None:
    response = await client.get("/offerings")
    shape = response.json()["code"]
    created = await client.post("/tables", json={"scheme": "literaki", "name": "Ala"})
    code = created.json()["code"]
    assert len(code) == shape["length"]
    assert set(code) <= set(shape["alphabet"])
    assert "I" not in shape["alphabet"]
    assert "O" not in shape["alphabet"]


async def test_offerings_grow_when_a_dictionary_arrives(
    client: httpx.AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("wordserver.app.dictionary_ready", lambda name: True)
    response = await client.get("/offerings")
    names = {offering["name"] for offering in response.json()["offerings"]}
    assert "scrabble" in names


async def test_scrabble_creation_refused_without_dictionary(
    client: httpx.AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        "wordserver.app.dictionary_ready",
        lambda name: name == DictionaryName.SJP,
    )
    response = await client.post("/tables", json={"scheme": "scrabble", "name": "Ala"})
    assert response.status_code == 422
    assert response.json()["code"] == "dictionary_unavailable"


async def test_description_serves_rules_and_alphabet(client: httpx.AsyncClient) -> None:
    created = await client.post(
        "/tables", json={"scheme": "literaki", "name": "Ala", "rules": seated(3)}
    )
    data = created.json()
    described = await client.get(
        f"/tables/{data['table_id']}", headers={"X-Seat-Token": data["token"]}
    )
    assert described.status_code == 200
    body = described.json()
    assert body["code"] == data["code"]
    assert body["scheme"] == "literaki"
    assert body["specimen"] == "SŁOWIKI"
    rules = body["rules"]
    assert rules["seats"] == 3
    assert rules["dictionary"] == "sjp"
    assert rules["rack_size"] == 7
    assert rules["exchange_limit"] == 3
    assert rules["exchange_min_bag"] == 7
    assert rules["bingo_bonus"] == 50
    assert rules["premoves"] is True
    assert body["feedback"]["lore"] is True
    symbols = [letter["symbol"] for letter in body["alphabet"]]
    assert symbols[:4] == ["A", "Ą", "B", "C"]
    assert sum(body["distribution"].values()) + body["blanks"] == 100
    assert body["blanks"] == 2


async def test_description_hides_code_from_spectators(client: httpx.AsyncClient) -> None:
    created = await client.post("/tables", json={"scheme": "literaki", "name": "Ala"})
    table_id = created.json()["table_id"]
    described = await client.get(f"/tables/{table_id}")
    assert described.status_code == 200
    assert described.json()["code"] is None
    missing = await client.get("/tables/absent")
    assert missing.status_code == 404


async def test_create_table_and_view(client: httpx.AsyncClient) -> None:
    response = await client.post("/tables", json={"scheme": "literaki", "name": "Ala"})
    assert response.status_code == 200
    data = response.json()
    table_id = data["table_id"]
    assert data["seat"] == 0
    assert len(data["code"]) == 6
    view = await client.get(f"/tables/{table_id}/view", headers={"X-Seat-Token": data["token"]})
    assert view.status_code == 200
    body = view.json()
    assert body["seq"] == 0
    assert body["view"]["racks"]["0"] is None
    assert body["view"]["racks"]["1"] is None
    assert body["view"]["bag_count"] == 86
    await client.post(f"/tables/{data['code']}/join", json={"name": "Ola"})
    revealed = await client.get(f"/tables/{table_id}/view", headers={"X-Seat-Token": data["token"]})
    assert revealed.json()["view"]["racks"]["0"] is not None
    assert revealed.json()["view"]["racks"]["1"] is None


async def test_move_requires_token(client: httpx.AsyncClient) -> None:
    response = await client.post("/tables", json={"scheme": "literaki", "name": "Ala"})
    table_id = response.json()["table_id"]
    move = {"player": 0, "action": {"kind": "pass"}}
    result = await client.post(f"/tables/{table_id}/moves", json={"move": move, "base_seq": 0})
    assert result.status_code == 409


async def test_pass_advances_turn(client: httpx.AsyncClient) -> None:
    response = await client.post("/tables", json={"scheme": "literaki", "name": "Ala"})
    data = response.json()
    table_id = data["table_id"]
    token = data["token"]
    await client.post(f"/tables/{data['code']}/join", json={"name": "Ola"})
    move = {"player": 0, "action": {"kind": "pass"}}
    result = await client.post(
        f"/tables/{table_id}/moves",
        json={"move": move, "base_seq": 0},
        headers={"X-Seat-Token": token},
    )
    assert result.status_code == 200
    assert result.json()["seq"] == 1
    view = await client.get(f"/tables/{table_id}/view", headers={"X-Seat-Token": token})
    assert view.json()["view"]["to_act"] == [1]


async def test_join_table(client: httpx.AsyncClient) -> None:
    created = await client.post("/tables", json={"scheme": "literaki", "name": "Ala"})
    data = created.json()
    code = data["code"]
    joined = await client.post(f"/tables/{code}/join", json={"name": "Ola"})
    assert joined.status_code == 200
    body = joined.json()
    assert body["seat"] == 1
    assert body["table_id"] == data["table_id"]
    full = await client.post(f"/tables/{code}/join", json={"name": "Ola"})
    assert full.status_code == 409
    missing = await client.post("/tables/ZZZZZZ/join", json={"name": "Ola"})
    assert missing.status_code == 404


async def test_session_events_streams_after_submit() -> None:
    resolved = resolve_scheme(CONFIG_DIR, "literaki")
    rules = build_rules(resolved, (0, 1), TextLexicon.from_words(["aa"]))
    game = Game(rules, random.Random(0), premoves_allowed=True)
    time = TimeConfig(
        per_turn_seconds=None,
        increment_seconds=0,
        total_seconds=None,
    )
    names: dict[int, str | None] = {0: "Ala", 1: None}
    session = TableSession(
        game,
        {0: "token-a", 1: "token-b"},
        time,
        names,
        lambda: 0.0,
        premove_delay_seconds=_PREMOVE_DELAY,
    )
    await session.claim("Bob")
    await session.submit(Move(player=0, action=Pass()), base_seq=0, premove=False, token="token-a")
    stream = session.events(observer=0, since=0)
    first = await anext(stream)
    assert first.startswith("event: presence\n")
    assert "id:" not in first
    second = await anext(stream)
    assert second.startswith("event: position\n")
    third = await anext(stream)
    assert third.startswith("id: 0\n")
    assert '"seq": 0' in third
    await stream.aclose()


async def test_presence_frames_follow_claims_and_disconnects() -> None:
    resolved = resolve_scheme(CONFIG_DIR, "literaki")
    rules = build_rules(resolved, (0, 1), TextLexicon.from_words(["aa"]))
    game = Game(rules, random.Random(0), premoves_allowed=True)
    time = TimeConfig(
        per_turn_seconds=None,
        increment_seconds=0,
        total_seconds=None,
    )
    names: dict[int, str | None] = {0: "Ala", 1: None}
    session = TableSession(
        game,
        {0: "token-a", 1: "token-b"},
        time,
        names,
        lambda: 0.0,
        premove_delay_seconds=_PREMOVE_DELAY,
    )
    stream = session.events(observer=0, since=0)
    first = await anext(stream)
    assert first.startswith("event: presence\n")
    assert '"name": "Ala"' in first
    assert '"connected": true' in first
    assert (await anext(stream)).startswith("event: position\n")
    claimed = await session.claim("Bob")
    assert claimed == (1, "token-b")
    second = await anext(stream)
    assert second.startswith("event: presence\n")
    assert '"name": "Bob"' in second
    await stream.aclose()
    company = session.company()
    assert company.seats[0].connected is False
    assert company.seats[1].claimed is True


class _FakeClock:
    def __init__(self) -> None:
        self.moment = 1000.0

    def __call__(self) -> float:
        return self.moment


def _timed_session(seconds: int | None, clock: _FakeClock) -> TableSession:
    timed = TimeConfig(
        per_turn_seconds=seconds,
        increment_seconds=0,
        total_seconds=None,
    )
    return _session_with(timed, clock)


def _budgeted_session(total: int, increment: int, clock: _FakeClock) -> TableSession:
    budgeted = TimeConfig(
        per_turn_seconds=None,
        increment_seconds=increment,
        total_seconds=total,
    )
    return _session_with(budgeted, clock)


def _frame_body(frame: str) -> dict[str, Any]:
    return json.loads(frame.split("data: ", 1)[1])


async def _next_event(session: TableSession, observer: int, since: int) -> dict[str, Any]:
    stream = session.events(observer=observer, since=since)
    try:
        async for frame in stream:
            if frame.startswith("id: "):
                return _frame_body(frame)

        raise AssertionError("the stream closed before an event arrived")
    finally:
        await stream.aclose()


def _session_with(time: TimeConfig, clock: _FakeClock) -> TableSession:
    return _tailored_session(
        time,
        clock,
        resolved=resolve_scheme(CONFIG_DIR, "literaki"),
        premove_delay=_PREMOVE_DELAY,
    )


def _tailored_session(
    time: TimeConfig,
    clock: _FakeClock,
    *,
    resolved: ResolvedScheme,
    premove_delay: float,
) -> TableSession:
    rules = build_rules(resolved, (0, 1), TextLexicon.from_words(["aa"]))
    game = Game(rules, random.Random(0), premoves_allowed=True)
    names: dict[int, str | None] = {0: None, 1: None}
    return TableSession(
        game,
        {0: "token-a", 1: "token-b"},
        time,
        names,
        clock,
        premove_delay_seconds=premove_delay,
    )


def _resolved_with(changes: dict[str, object]) -> ResolvedScheme:
    scheme = load_scheme(CONFIG_DIR, "literaki")
    return resolve_table(CONFIG_DIR, scheme, restated(scheme.rules, changes))


async def test_clock_arms_when_the_table_gathers() -> None:
    clock = _FakeClock()
    session = _timed_session(90, clock)
    assert session.clock() is None
    await session.claim(None)
    armed = session.clock()
    assert armed is not None
    assert armed.seat == 0
    assert armed.deadline == 1090.0
    assert armed.server_time == 1000.0
    assert armed.remaining == {}
    await session.close()


async def test_budget_charges_the_thinking_seat_and_pays_the_increment() -> None:
    clock = _FakeClock()
    session = _budgeted_session(300, 10, clock)
    await session.claim(None)
    opened = session.clock()
    assert opened is not None
    assert opened.deadline == 1300.0
    assert opened.remaining == {"0": 300.0, "1": 300.0}
    clock.moment = 1040.0
    rack = session.view(0).racks[0]
    assert rack is not None
    exchange = Move(player=0, action=Exchange(tile_ids=[rack[0].identifier]))
    await session.submit(exchange, base_seq=0, premove=False, token="token-a")
    rearmed = session.clock()
    assert rearmed is not None
    assert rearmed.seat == 1
    assert rearmed.remaining == {"0": 270.0, "1": 300.0}
    assert rearmed.deadline == 1340.0
    await session.close()


async def test_a_pass_earns_no_increment() -> None:
    clock = _FakeClock()
    session = _budgeted_session(300, 10, clock)
    await session.claim(None)
    clock.moment = 1030.0
    await session.submit(Move(player=0, action=Pass()), base_seq=0, premove=False, token="token-a")
    spent = session.clock()
    assert spent is not None
    assert spent.remaining == {"0": 270.0, "1": 300.0}
    await session.close()


async def test_a_table_of_spent_budgets_passes_out_to_the_end() -> None:
    clock = _FakeClock()
    session = _budgeted_session(0, 0, clock)
    await session.claim(None)
    await asyncio.sleep(0.2)
    assert session.seq == 4
    assert session.view(None).phase == "game_over"
    assert session.clock() is None
    await session.close()


async def test_a_spent_seat_is_refused_a_premove() -> None:
    clock = _FakeClock()
    session = _budgeted_session(30, 0, clock)
    await session.claim(None)
    clock.moment = 1030.0
    await session.submit(Move(player=0, action=Pass()), base_seq=0, premove=False, token="token-a")
    spent = session.clock()
    assert spent is not None
    assert spent.remaining["0"] == 0.0
    rack = session.view(0).racks[0]
    assert rack is not None
    exchange = Move(player=0, action=Exchange(tile_ids=[rack[0].identifier]))
    with pytest.raises(OutOfTime):
        await session.submit(exchange, base_seq=1, premove=True, token="token-a")

    assert session.seq == 1
    assert session.view(0).premove is None
    await session.close()


async def test_a_seat_past_its_deadline_is_refused_a_move() -> None:
    clock = _FakeClock()
    session = _timed_session(90, clock)
    await session.claim(None)
    clock.moment = 1200.0
    rack = session.view(0).racks[0]
    assert rack is not None
    exchange = Move(player=0, action=Exchange(tile_ids=[rack[0].identifier]))
    with pytest.raises(OutOfTime):
        await session.submit(exchange, base_seq=0, premove=False, token="token-a")

    assert session.seq == 0
    await session.close()


async def test_opponent_premove_leaves_the_deadline_alone() -> None:
    clock = _FakeClock()
    session = _timed_session(90, clock)
    await session.claim(None)
    first = session.clock()
    assert first is not None
    clock.moment = 1050.0
    other_rack = session.view(1).racks[1]
    assert other_rack is not None
    move = Move(player=1, action=Exchange(tile_ids=[other_rack[0].identifier]))
    await session.submit(move, base_seq=0, premove=True, token="token-b")
    queued = session.clock()
    assert queued is not None
    assert queued.deadline == first.deadline
    rack = session.view(0).racks[0]
    assert rack is not None
    exchange = Move(player=0, action=Exchange(tile_ids=[rack[0].identifier]))
    await session.submit(exchange, base_seq=1, premove=False, token="token-a")
    rearmed = session.clock()
    assert rearmed is not None
    assert rearmed.deadline == 1140.0
    await session.close()


async def test_a_premove_waits_out_its_delay_before_it_settles() -> None:
    clock = _FakeClock()
    session = _timed_session(90, clock)
    await session.claim(None)
    other_rack = session.view(1).racks[1]
    assert other_rack is not None
    queued = Move(player=1, action=Exchange(tile_ids=[other_rack[0].identifier]))
    await session.submit(queued, base_seq=0, premove=True, token="token-b")
    await session.submit(Move(player=0, action=Pass()), base_seq=1, premove=False, token="token-a")
    assert session.seq == 2
    assert session.view(1).to_act == frozenset({1})
    assert session.view(1).premove is not None
    await asyncio.sleep(_PREMOVE_DELAY * 3)
    assert session.seq == 3
    assert session.view(1).premove is None
    assert session.view(1).to_act == frozenset({0})
    await session.close()


async def test_the_premove_delay_is_charged_to_the_premover() -> None:
    clock = _FakeClock()
    session = _budgeted_session(300, 10, clock)
    await session.claim(None)
    other_rack = session.view(1).racks[1]
    assert other_rack is not None
    queued = Move(player=1, action=Exchange(tile_ids=[other_rack[0].identifier]))
    await session.submit(queued, base_seq=0, premove=True, token="token-b")
    clock.moment = 1020.0
    await session.submit(Move(player=0, action=Pass()), base_seq=1, premove=False, token="token-a")
    clock.moment = 1021.0
    await asyncio.sleep(_PREMOVE_DELAY * 3)
    rearmed = session.clock()
    assert rearmed is not None
    assert rearmed.seat == 0
    assert rearmed.remaining == {"0": 280.0, "1": 309.0}
    await session.close()


async def test_a_premove_that_flags_its_seat_is_returned() -> None:
    clock = _FakeClock()
    session = _budgeted_session(30, 0, clock)
    await session.claim(None)
    other_rack = session.view(1).racks[1]
    assert other_rack is not None
    queued = Move(player=1, action=Exchange(tile_ids=[other_rack[0].identifier]))
    await session.submit(queued, base_seq=0, premove=True, token="token-b")
    clock.moment = 1030.0
    await session.submit(Move(player=0, action=Pass()), base_seq=1, premove=False, token="token-a")
    clock.moment = 1061.0
    returned = await _next_event(session, observer=1, since=2)
    assert returned["kind"] == EntryKind.PREMOVE_DISCARDED
    assert returned["reason"] == RejectionCode.OUT_OF_TIME
    assert session.view(1).premove is None
    assert session.view(1).to_act == frozenset({1})
    await session.close()


async def test_a_run_of_premoves_settles_one_delay_at_a_time() -> None:
    clock = _FakeClock()
    session = _timed_session(90, clock)
    await session.claim(None)
    other_rack = session.view(1).racks[1]
    own_rack = session.view(0).racks[0]
    assert other_rack is not None
    assert own_rack is not None
    theirs = Move(player=1, action=Exchange(tile_ids=[other_rack[0].identifier]))
    await session.submit(theirs, base_seq=0, premove=True, token="token-b")
    await session.submit(Move(player=0, action=Pass()), base_seq=1, premove=False, token="token-a")
    mine = Move(player=0, action=Exchange(tile_ids=[own_rack[0].identifier]))
    await session.submit(mine, base_seq=2, premove=True, token="token-a")
    await asyncio.sleep(_PREMOVE_DELAY / 2)
    assert session.seq == 3
    await asyncio.sleep(_PREMOVE_DELAY * 6)
    assert session.seq == 5
    assert session.view(0).premove is None
    assert session.view(0).to_act == frozenset({1})
    await session.close()


async def test_timeout_auto_passes_until_the_game_ends() -> None:
    clock = _FakeClock()
    session = _timed_session(0, clock)
    await session.claim(None)
    await asyncio.sleep(0.2)
    assert session.seq == 4
    assert session.view(None).phase == "game_over"
    assert session.clock() is None
    await session.close()


async def test_an_expired_clock_passes_the_turn_a_player_may_not() -> None:
    clock = _FakeClock()
    session = _tailored_session(
        TimeConfig(per_turn_seconds=0, increment_seconds=0, total_seconds=None),
        clock,
        resolved=_resolved_with({"pass_allowed": False}),
        premove_delay=_PREMOVE_DELAY,
    )
    await session.claim(None)
    await asyncio.sleep(0.2)
    assert session.seq == 4
    assert session.view(None).phase == Phase.GAME_OVER
    passed = await _next_event(session, observer=0, since=0)
    assert passed["kind"] == EntryKind.MOVE
    assert passed["actor"] == 0
    assert passed["move"]["action"]["kind"] == ActionKind.PASS
    await session.close()


async def test_an_expired_clock_discards_the_queued_move_it_skips() -> None:
    clock = _FakeClock()
    session = _tailored_session(
        TimeConfig(
            per_turn_seconds=None,
            increment_seconds=0,
            total_seconds=_SHORTEST_BUDGET,
        ),
        clock,
        resolved=resolve_scheme(CONFIG_DIR, "literaki"),
        premove_delay=_PATIENT_DELAY,
    )
    await session.claim(None)
    held = session.view(1).racks[1]
    assert held is not None
    exchanged = held[0].identifier
    queued = Move(player=1, action=Exchange(tile_ids=[exchanged]))
    await session.submit(queued, base_seq=0, premove=True, token="token-b")
    await session.submit(Move(player=0, action=Pass()), base_seq=1, premove=False, token="token-a")
    await asyncio.sleep(_PAST_THE_BUDGET)
    discarded = await _next_event(session, observer=1, since=2)
    assert discarded["kind"] == EntryKind.PREMOVE_DISCARDED
    assert discarded["reason"] == RejectionCode.OUT_OF_TIME
    assert session.view(1).premove is None
    assert session.view(1).to_act == frozenset({0})
    kept = session.view(1).racks[1]
    assert kept is not None
    assert exchanged in {tile.identifier for tile in kept}
    await session.close()


async def test_a_seat_out_of_time_neither_plays_nor_queues() -> None:
    clock = _FakeClock()
    session = _budgeted_session(300, 0, clock)
    await session.claim(None)
    clock.moment = 1300.0
    await session.submit(Move(player=0, action=Pass()), base_seq=0, premove=False, token="token-a")
    spent = session.clock()
    assert spent is not None
    assert spent.remaining["0"] == 0.0
    held = session.view(0).racks[0]
    assert held is not None
    queued = Move(player=0, action=Exchange(tile_ids=[held[0].identifier]))
    with pytest.raises(OutOfTime):
        await session.submit(queued, base_seq=1, premove=True, token="token-a")

    with pytest.raises(OutOfTime):
        await session.submit(
            Move(player=0, action=Pass()),
            base_seq=1,
            premove=False,
            token="token-a",
        )

    await session.close()


async def test_clock_frames_ride_the_stream() -> None:
    clock = _FakeClock()
    session = _timed_session(90, clock)
    await session.claim(None)
    stream = session.events(observer=0, since=0)
    first = await anext(stream)
    assert first.startswith("event: presence\n")
    assert (await anext(stream)).startswith("event: position\n")
    third = await anext(stream)
    assert third.startswith("event: clock\n")
    assert '"deadline": 1090.0' in third
    assert "id:" not in third
    await stream.aclose()
    await session.close()


async def test_the_letters_ride_the_turn_that_opens_them() -> None:
    clock = _FakeClock()
    session = _timed_session(90, clock)
    stream = session.events(observer=0, since=0)
    assert (await anext(stream)).startswith("event: presence\n")
    gathering = _frame_body(await anext(stream))
    assert gathering["racks"] == {"0": None, "1": None}
    await session.claim("Bob")
    assert (await anext(stream)).startswith("event: presence\n")
    seated = _frame_body(await anext(stream))
    assert seated["racks"]["0"] is not None
    assert seated["racks"]["1"] is None
    assert (await anext(stream)).startswith("event: clock\n")
    await stream.aclose()
    await session.close()


async def test_a_waiting_stream_wakes_on_the_next_move() -> None:
    clock = _FakeClock()
    session = _timed_session(None, clock)
    await session.claim("Bob")
    stream = session.events(observer=0, since=0)
    assert (await anext(stream)).startswith("event: presence\n")
    assert (await anext(stream)).startswith("event: position\n")
    waiting = asyncio.create_task(anext(stream))
    await asyncio.sleep(0)
    await session.submit(Move(player=0, action=Pass()), base_seq=0, premove=False, token="token-a")
    frame = await asyncio.wait_for(waiting, timeout=1.0)
    assert frame.startswith("id: 0\n")
    await stream.aclose()
    await session.close()


async def test_claims_hand_out_distinct_seats_concurrently(client: httpx.AsyncClient) -> None:
    created = await client.post(
        "/tables", json={"scheme": "literaki", "name": "Ala", "rules": seated(3)}
    )
    code = created.json()["code"]
    first, second = await asyncio.gather(
        client.post(f"/tables/{code}/join", json={"name": "Bob"}),
        client.post(f"/tables/{code}/join", json={"name": "Cyryl"}),
    )
    assert first.status_code == 200
    assert second.status_code == 200
    assert {first.json()["seat"], second.json()["seat"]} == {1, 2}


async def test_gathering_hides_racks_and_blocks_moves(client: httpx.AsyncClient) -> None:
    created = await client.post("/tables", json={"scheme": "literaki", "name": "Ala"})
    data = created.json()
    table_id = data["table_id"]
    token = data["token"]
    view = await client.get(f"/tables/{table_id}/view", headers={"X-Seat-Token": token})
    racks = view.json()["view"]["racks"]
    assert racks["0"] is None
    assert racks["1"] is None
    move = {"player": 0, "action": {"kind": "pass"}}
    blocked = await client.post(
        f"/tables/{table_id}/moves",
        json={"move": move, "base_seq": 0},
        headers={"X-Seat-Token": token},
    )
    assert blocked.status_code == 409
    assert blocked.json()["code"] == "gathering"
    await client.post(f"/tables/{data['code']}/join", json={"name": "Ola"})
    accepted = await client.post(
        f"/tables/{table_id}/moves",
        json={"move": move, "base_seq": 0},
        headers={"X-Seat-Token": token},
    )
    assert accepted.status_code == 200


async def _gathered_table(client: httpx.AsyncClient) -> tuple[str, str, str]:
    created = await client.post("/tables", json={"scheme": "literaki", "name": "Ala"})
    data = created.json()
    joined = await client.post(f"/tables/{data['code']}/join", json={"name": "Ola"})
    return data["table_id"], data["token"], joined.json()["token"]


async def _rack_identifiers(
    client: httpx.AsyncClient,
    table_id: str,
    token: str,
    seat: int,
) -> list[int]:
    view = await client.get(f"/tables/{table_id}/view", headers={"X-Seat-Token": token})
    return [tile["identifier"] for tile in view.json()["view"]["racks"][str(seat)]]


async def test_a_rack_order_is_remembered_without_advancing_the_table(
    client: httpx.AsyncClient,
) -> None:
    table_id, token, _ = await _gathered_table(client)
    served = await _rack_identifiers(client, table_id, token, seat=0)
    asked = list(reversed(served))
    stored = await client.put(
        f"/tables/{table_id}/rack",
        json={"tile_ids": asked},
        headers={"X-Seat-Token": token},
    )
    assert stored.status_code == 204
    view = await client.get(f"/tables/{table_id}/view", headers={"X-Seat-Token": token})
    assert view.json()["seq"] == 0
    assert [tile["identifier"] for tile in view.json()["view"]["racks"]["0"]] == asked


async def test_a_rack_order_leaves_the_other_seats_alone(client: httpx.AsyncClient) -> None:
    table_id, token, other = await _gathered_table(client)
    served = await _rack_identifiers(client, table_id, token, seat=0)
    before = await client.get(f"/tables/{table_id}/view", headers={"X-Seat-Token": other})
    await client.put(
        f"/tables/{table_id}/rack",
        json={"tile_ids": list(reversed(served))},
        headers={"X-Seat-Token": token},
    )
    after = await client.get(f"/tables/{table_id}/view", headers={"X-Seat-Token": other})
    assert after.json()["view"]["racks"]["1"] == before.json()["view"]["racks"]["1"]
    assert after.json()["view"]["racks"]["0"] is None


async def test_a_rack_order_naming_other_tiles_is_refused(client: httpx.AsyncClient) -> None:
    table_id, token, _ = await _gathered_table(client)
    served = await _rack_identifiers(client, table_id, token, seat=0)
    foreign = await client.put(
        f"/tables/{table_id}/rack",
        json={"tile_ids": [*served[1:], max(served) + 1]},
        headers={"X-Seat-Token": token},
    )
    assert foreign.status_code == 409
    assert foreign.json()["code"] == "rack_mismatch"
    partial = await client.put(
        f"/tables/{table_id}/rack",
        json={"tile_ids": served[1:]},
        headers={"X-Seat-Token": token},
    )
    assert partial.status_code == 409
    assert partial.json()["code"] == "rack_mismatch"


async def test_a_rack_order_requires_a_seat_token(client: httpx.AsyncClient) -> None:
    table_id, token, _ = await _gathered_table(client)
    served = await _rack_identifiers(client, table_id, token, seat=0)
    response = await client.put(f"/tables/{table_id}/rack", json={"tile_ids": served})
    assert response.status_code == 409
    assert response.json()["code"] == "seat_token_mismatch"


async def test_a_rack_order_wakes_no_stream() -> None:
    clock = _FakeClock()
    session = _timed_session(None, clock)
    await session.claim("Bob")
    stream = session.events(observer=1, since=0)
    assert (await anext(stream)).startswith("event: presence\n")
    assert (await anext(stream)).startswith("event: position\n")
    waiting = asyncio.create_task(anext(stream))
    await asyncio.sleep(0)
    served = [tile.identifier for tile in session.view(0).racks[0] or ()]
    await session.arrange_rack(tuple(reversed(served)), token="token-a")
    await asyncio.sleep(0)
    assert not waiting.done()
    await session.submit(Move(player=0, action=Pass()), base_seq=0, premove=False, token="token-a")
    assert (await asyncio.wait_for(waiting, timeout=1.0)).startswith("id: 0\n")
    await stream.aclose()
    await session.close()


async def test_a_remembered_order_rides_the_event_frames() -> None:
    clock = _FakeClock()
    session = _timed_session(None, clock)
    await session.claim("Bob")
    served = [tile.identifier for tile in session.view(0).racks[0] or ()]
    asked = tuple(reversed(served))
    await session.arrange_rack(asked, token="token-a")
    await session.submit(Move(player=0, action=Pass()), base_seq=0, premove=False, token="token-a")
    stream = session.events(observer=0, since=0)
    assert (await anext(stream)).startswith("event: presence\n")
    opening = _frame_body(await anext(stream))
    assert [tile["identifier"] for tile in opening["racks"]["0"]] == list(asked)
    passed = _frame_body(await anext(stream))
    assert [tile["identifier"] for tile in passed["position"]["racks"]["0"]] == list(asked)
    await stream.aclose()
    await session.close()


async def test_an_idle_stream_beats_where_the_journal_is_quiet(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("wordserver.session._HEARTBEAT_SECONDS", 0.05)
    clock = _FakeClock()
    session = _timed_session(None, clock)
    await session.claim("Bob")
    stream = session.events(observer=0, since=0)
    assert (await anext(stream)).startswith("event: presence\n")
    assert (await anext(stream)).startswith("event: position\n")
    beat = await asyncio.wait_for(anext(stream), timeout=1.0)
    assert beat.startswith("event: heartbeat\n")
    assert _frame_body(beat)["server_time"] == clock.moment
    await stream.aclose()
    await session.close()


async def test_a_cancelled_stream_releases_its_seat() -> None:
    clock = _FakeClock()
    session = _timed_session(None, clock)
    await session.claim("Bob")
    stream = session.events(observer=0, since=0)

    async def drain() -> None:
        async for _ in stream:
            pass

    watching = asyncio.create_task(drain())
    for _ in range(4):
        await asyncio.sleep(0)
    assert session.company().seats[0].connected is True
    watching.cancel()
    await asyncio.gather(watching, return_exceptions=True)
    assert session.company().seats[0].connected is False
    for _ in range(4):
        await asyncio.sleep(0)
    await session.close()


def _registry_with(session: TableSession) -> tuple[TableRegistry, str]:
    resolved = resolve_scheme(CONFIG_DIR, "literaki")
    meta = TableMeta(
        code="ABCDEF",
        resolved=resolved,
        time=time_of(resolved.rules),
    )
    registry = TableRegistry(GameBook(KEPT_GAMES))
    registry.add("table-1", session, meta)
    registry.add_code(meta.code, "table-1")
    return registry, "table-1"


def _swept(registry: TableRegistry, clock: _FakeClock) -> TableSweep:
    bounds = TablesConfig(
        life_seconds=86400.0,
        linger_seconds=3600.0,
        sweep_seconds=60.0,
        premove_delay_seconds=_PREMOVE_DELAY,
    )
    return TableSweep(registry, bounds, clock)


async def _passed_out(session: TableSession) -> None:
    for turn, seat in enumerate((0, 1, 0, 1)):
        await session.submit(
            Move(player=seat, action=Pass()),
            base_seq=turn,
            premove=False,
            token=f"token-{'ab'[seat]}",
        )


async def test_a_table_left_standing_for_a_day_closes_unresolved() -> None:
    clock = _FakeClock()
    session = _timed_session(None, clock)
    await session.claim("Bob")
    registry, table_id = _registry_with(session)
    sweep = _swept(registry, clock)
    assert await sweep.once() == ()

    clock.moment += 86400.0
    assert await sweep.once() == ()
    assert session.view(None).phase == Phase.UNRESOLVED
    assert registry.get(table_id) is session

    clock.moment += 3600.0
    assert await sweep.once() == (table_id,)
    assert registry.get(table_id) is None
    assert registry.meta_for(table_id) is None
    assert registry.table_id_for_code("ABCDEF") is None


async def test_a_finished_table_is_recorded_when_it_is_let_go() -> None:
    clock = _FakeClock()
    session = _timed_session(None, clock)
    await session.claim("Bob")
    await _passed_out(session)
    scores = session.view(None).scores
    registry, table_id = _registry_with(session)
    sweep = _swept(registry, clock)
    assert await sweep.once() == ()

    clock.moment += 3600.0
    assert await sweep.once() == (table_id,)
    record = registry.record_for(table_id)
    assert record is not None
    assert record.phase == Phase.GAME_OVER
    assert record.scheme == "literaki"
    assert [seated.name for seated in record.seats] == [None, "Bob"]
    assert [seated.score for seated in record.seats] == [scores[0], scores[1]]
    assert record.opened == 1000.0
    assert record.closed == clock.moment


async def test_closing_a_table_lets_its_streams_go() -> None:
    clock = _FakeClock()
    session = _timed_session(None, clock)
    await session.claim("Bob")
    stream = session.events(observer=0, since=0)
    assert (await anext(stream)).startswith("event: presence\n")

    async def drain() -> list[str]:
        return [frame async for frame in stream]

    await session.close()
    remaining = await asyncio.wait_for(drain(), timeout=1.0)
    assert all(not frame.startswith("event: heartbeat\n") for frame in remaining)
    assert session.company().seats[0].connected is False


async def test_an_abandoned_seat_keeps_the_points_it_earned() -> None:
    clock = _FakeClock()
    session = _timed_session(None, clock)
    await session.claim("Bob")
    await session.abandon()
    view = session.view(None)
    assert view.phase == Phase.UNRESOLVED
    assert view.to_act == frozenset()
    assert view.scores == {0: 0, 1: 0}
    assert session.clock() is None
    await session.close()


async def test_a_table_the_server_never_held_reads_as_unknown() -> None:
    refusal = table_gone(None)
    assert refusal.status_code == 404
    assert refusal.code is ErrorCode.UNKNOWN_TABLE


async def test_a_recorded_table_reads_as_closed() -> None:
    clock = _FakeClock()
    session = _timed_session(None, clock)
    await session.claim("Bob")
    registry, table_id = _registry_with(session)
    await registry.close(table_id, at=clock.moment)
    refusal = table_gone(registry.record_for(table_id))
    assert refusal.status_code == 410
    assert refusal.code is ErrorCode.TABLE_CLOSED


async def test_the_offerings_carry_the_allowances(client: httpx.AsyncClient) -> None:
    served = (await client.get("/offerings")).json()
    by_setting = {allowance["setting"]: allowance for allowance in served["allowances"]}
    assert by_setting["seats"]["minimum"] == 1
    assert by_setting["seats"]["group"] == "table"
    assert by_setting["total_seconds"]["offered"][0] == 60
    assert by_setting["rack_size"]["unlimited"] is True
    assert "literaki" in by_setting["board"]["choices"]
    assert served["offerings"][0]["rules"]["seats"] == 2


async def test_the_presets_serve_what_is_on_disk(client: httpx.AsyncClient) -> None:
    served = (await client.get("/presets")).json()
    assert [board["name"] for board in served["boards"]] == ["literaki", "scrabble"]
    assert [alphabet["name"] for alphabet in served["alphabets"]] == [
        "literaki",
        "scrabble-en",
        "scrabble-pl",
    ]
    assert [one["name"] for one in served["distributions"]] == ["english", "polish"]
    literaki = next(one for one in served["alphabets"] if one["name"] == "literaki")
    assert literaki["order"][:2] == ["A", "Ą"]
    assert literaki["dictionaries"] == ["sjp", "osps"]


async def test_an_invitation_reads_the_rules_before_a_seat_is_claimed(
    client: httpx.AsyncClient,
) -> None:
    created = await client.post("/tables", json={"scheme": "literaki", "name": "Ala"})
    data = created.json()
    invited = await client.get(f"/invitations/{data['code']}")
    assert invited.status_code == 200
    body = invited.json()
    assert body["code"] is None
    assert body["scheme"] == "literaki"
    assert body["rules"]["seats"] == 2
    missing = await client.get("/invitations/ZZZZZZ")
    assert missing.status_code == 404
    assert missing.json()["code"] == "unknown_code"


async def test_a_table_plays_by_the_rules_it_was_asked_for(client: httpx.AsyncClient) -> None:
    asked = stated(
        {
            "seats": 3,
            "exchange_limit": None,
            "premoves": False,
            "bingo_tiles": 6,
            "per_turn_seconds": 300,
            "letters": {"Ź": {"value": 12, "count": 3}},
        }
    )
    created = await client.post(
        "/tables",
        json={"scheme": "literaki", "name": "Ala", "rules": asked},
    )
    assert created.status_code == 200
    described = (await client.get(f"/tables/{created.json()['table_id']}")).json()
    assert described["rules"]["exchange_limit"] is None
    assert described["rules"]["premoves"] is False
    assert described["rules"]["bingo_tiles"] == 6
    assert described["rules"]["per_turn_seconds"] == 300
    assert described["distribution"]["Ź"] == 3
    zet = next(letter for letter in described["alphabet"] if letter["symbol"] == "Ź")
    assert zet["value"] == 12
    assert zet["category"] == "red"


async def test_a_one_seat_literaki_table_deals_a_seven_tile_rack(
    client: httpx.AsyncClient,
) -> None:
    asked = stated({"seats": 1, "rack_size": 7, "pass_end_rounds": None, "premoves": False})
    created = await client.post(
        "/tables",
        json={"scheme": "literaki", "name": "Ala", "rules": asked},
    )
    assert created.status_code == 200
    data = created.json()
    assert data["seats"] == 1
    view = await client.get(
        f"/tables/{data['table_id']}/view",
        headers={"X-Seat-Token": data["token"]},
    )
    body = view.json()
    assert len(body["view"]["racks"]["0"]) == 7
    assert body["view"]["bag_count"] == 93


async def test_a_bag_too_small_for_its_racks_is_refused(client: httpx.AsyncClient) -> None:
    response = await client.post(
        "/tables",
        json={"scheme": "literaki", "name": "Ala", "rules": stated({"seats": 8, "rack_size": 15})},
    )
    assert response.status_code == 422
    assert response.json()["code"] == "rules_inconsistent"
    assert "asks for 8" in response.json()["detail"]
