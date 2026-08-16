import asyncio
import random

import httpx
import pytest

from wordcore.games.game import Game
from wordcore.lexicon.lexicon import TextLexicon
from wordcore.moves.action import Move, Pass
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


async def test_offerings(client: httpx.AsyncClient) -> None:
    response = await client.get("/offerings")
    assert response.status_code == 200
    names = {offering["name"] for offering in response.json()["offerings"]}
    assert {"literaki", "scrabble", "solo-literaki"} <= names


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
    assert body["view"]["racks"]["0"] is not None
    assert body["view"]["racks"]["1"] is None
    assert body["view"]["bag_count"] == 86


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
    session = TableSession(game, {0: "token-a", 1: "token-b"}, time, names)
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
    session = TableSession(game, {0: "token-a", 1: "token-b"}, time, names)
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
