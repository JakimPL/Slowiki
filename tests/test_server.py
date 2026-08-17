import asyncio
import random

import httpx
import pytest

from lexica.names import DictionaryName
from wordcore.games.game import Game
from wordcore.lexicon.lexicon import TextLexicon
from wordcore.moves.action import Exchange, Pass
from wordcore.moves.move import Move
from wordserver.app import create_app
from wordserver.session import TableSession
from wordtable.build import build_rules
from wordtable.catalogue import resolve_scheme
from wordtable.config import TimeConfig
from wordtable.paths import CONFIG_DIR


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
    assert all(offering["dictionary"] == "sjp" for offering in served)


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
    response = await client.post("/tables", json={"scheme": "scrabble", "seats": 2})
    assert response.status_code == 422
    assert response.json()["code"] == "dictionary_unavailable"


async def test_description_serves_rules_and_alphabet(client: httpx.AsyncClient) -> None:
    created = await client.post("/tables", json={"scheme": "literaki", "seats": 3})
    data = created.json()
    described = await client.get(
        f"/tables/{data['table_id']}", headers={"X-Seat-Token": data["token"]}
    )
    assert described.status_code == 200
    body = described.json()
    assert body["code"] == data["code"]
    assert body["scheme"] == "literaki"
    assert body["seats"] == 3
    assert body["dictionary"] == "sjp"
    parameters = body["parameters"]
    assert parameters["rack_size"] == 7
    assert parameters["exchange_limit"] == 3
    assert parameters["exchange_min_bag"] == 7
    assert parameters["bingo_bonus"] == 50
    assert parameters["premoves_allowed"] is True
    symbols = [letter["symbol"] for letter in body["alphabet"]]
    assert symbols[:4] == ["A", "Ą", "B", "C"]
    assert sum(body["distribution"].values()) + body["blanks"] == 100
    assert body["blanks"] == 2


async def test_description_hides_code_from_spectators(client: httpx.AsyncClient) -> None:
    created = await client.post("/tables", json={"scheme": "literaki", "seats": 2})
    table_id = created.json()["table_id"]
    described = await client.get(f"/tables/{table_id}")
    assert described.status_code == 200
    assert described.json()["code"] is None
    missing = await client.get("/tables/absent")
    assert missing.status_code == 404


async def test_create_table_and_view(client: httpx.AsyncClient) -> None:
    response = await client.post("/tables", json={"scheme": "literaki", "seats": 2})
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
    await client.post(f"/tables/{data['code']}/join")
    revealed = await client.get(f"/tables/{table_id}/view", headers={"X-Seat-Token": data["token"]})
    assert revealed.json()["view"]["racks"]["0"] is not None
    assert revealed.json()["view"]["racks"]["1"] is None


async def test_move_requires_token(client: httpx.AsyncClient) -> None:
    response = await client.post("/tables", json={"scheme": "literaki", "seats": 2})
    table_id = response.json()["table_id"]
    move = {"player": 0, "action": {"kind": "pass"}}
    result = await client.post(f"/tables/{table_id}/moves", json={"move": move, "base_seq": 0})
    assert result.status_code == 409


async def test_pass_advances_turn(client: httpx.AsyncClient) -> None:
    response = await client.post("/tables", json={"scheme": "literaki", "seats": 2})
    data = response.json()
    table_id = data["table_id"]
    token = data["token"]
    await client.post(f"/tables/{data['code']}/join")
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
    created = await client.post("/tables", json={"scheme": "literaki", "seats": 2})
    data = created.json()
    code = data["code"]
    joined = await client.post(f"/tables/{code}/join")
    assert joined.status_code == 200
    body = joined.json()
    assert body["seat"] == 1
    assert body["table_id"] == data["table_id"]
    full = await client.post(f"/tables/{code}/join")
    assert full.status_code == 409
    missing = await client.post("/tables/ZZZZZZ/join")
    assert missing.status_code == 404


async def test_session_events_streams_after_submit() -> None:
    resolved = resolve_scheme(CONFIG_DIR, "literaki")
    rules = build_rules(resolved, (0, 1), TextLexicon.from_words(["aa"]))
    game = Game(rules, random.Random(0), premoves_allowed=True)
    time = TimeConfig(per_turn_seconds=None, increment_seconds=0, total_seconds=None)
    names: dict[int, str | None] = {0: "Ala", 1: None}
    session = TableSession(game, {0: "token-a", 1: "token-b"}, time, names, lambda: 0.0)
    await session.claim("Bob")
    await session.submit(Move(player=0, action=Pass()), base_seq=0, premove=False, token="token-a")
    stream = session.events(observer=0, since=0)
    first = await anext(stream)
    assert first.startswith("event: presence\n")
    assert "id:" not in first
    second = await anext(stream)
    assert second.startswith("id: 0\n")
    assert '"seq": 0' in second
    await stream.aclose()


async def test_presence_frames_follow_claims_and_disconnects() -> None:
    resolved = resolve_scheme(CONFIG_DIR, "literaki")
    rules = build_rules(resolved, (0, 1), TextLexicon.from_words(["aa"]))
    game = Game(rules, random.Random(0), premoves_allowed=True)
    time = TimeConfig(per_turn_seconds=None, increment_seconds=0, total_seconds=None)
    names: dict[int, str | None] = {0: "Ala", 1: None}
    session = TableSession(game, {0: "token-a", 1: "token-b"}, time, names, lambda: 0.0)
    stream = session.events(observer=0, since=0)
    first = await anext(stream)
    assert first.startswith("event: presence\n")
    assert '"name": "Ala"' in first
    assert '"connected": true' in first
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
    resolved = resolve_scheme(CONFIG_DIR, "literaki")
    rules = build_rules(resolved, (0, 1), TextLexicon.from_words(["aa"]))
    game = Game(rules, random.Random(0), premoves_allowed=True)
    timed = TimeConfig(per_turn_seconds=seconds, increment_seconds=0, total_seconds=None)
    names: dict[int, str | None] = {0: None, 1: None}
    return TableSession(game, {0: "token-a", 1: "token-b"}, timed, names, clock)


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
    assert armed.per_turn_seconds == 90
    session.close()


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
    session.close()


async def test_timeout_auto_passes_until_the_game_ends() -> None:
    clock = _FakeClock()
    session = _timed_session(0, clock)
    await session.claim(None)
    await asyncio.sleep(0.2)
    assert session.seq == 2
    assert session.view(None).phase == "game_over"
    assert session.clock() is None
    session.close()


async def test_clock_frames_ride_the_stream() -> None:
    clock = _FakeClock()
    session = _timed_session(90, clock)
    await session.claim(None)
    stream = session.events(observer=0, since=0)
    first = await anext(stream)
    assert first.startswith("event: presence\n")
    second = await anext(stream)
    assert second.startswith("event: clock\n")
    assert '"deadline": 1090.0' in second
    assert "id:" not in second
    await stream.aclose()
    session.close()


async def test_claims_hand_out_distinct_seats_concurrently(client: httpx.AsyncClient) -> None:
    created = await client.post("/tables", json={"scheme": "literaki", "seats": 3, "name": "Ala"})
    code = created.json()["code"]
    first, second = await asyncio.gather(
        client.post(f"/tables/{code}/join", json={"name": "Bob"}),
        client.post(f"/tables/{code}/join", json={"name": "Cyryl"}),
    )
    assert first.status_code == 200
    assert second.status_code == 200
    assert {first.json()["seat"], second.json()["seat"]} == {1, 2}


async def test_gathering_hides_racks_and_blocks_moves(client: httpx.AsyncClient) -> None:
    created = await client.post("/tables", json={"scheme": "literaki", "seats": 2})
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
    await client.post(f"/tables/{data['code']}/join")
    accepted = await client.post(
        f"/tables/{table_id}/moves",
        json={"move": move, "base_seq": 0},
        headers={"X-Seat-Token": token},
    )
    assert accepted.status_code == 200
