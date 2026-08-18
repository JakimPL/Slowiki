import json

import httpx
import pytest
from scripts.openapi import main

from wordserver.app import MAX_JUDGED_WORDS, create_app
from wordserver.models.table import TableViewResponse
from wordserver.models.table_admission import TableAdmission
from wordserver.models.word_verdicts import WordVerdicts
from wordtable.config import StyleTokens


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
async def client(app):
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


async def test_rejection_carries_code(client: httpx.AsyncClient) -> None:
    created = await client.post("/tables", json={"scheme": "literaki", "seats": 2, "name": "Ala"})
    table_id = created.json()["table_id"]
    move = {"player": 0, "action": {"kind": "pass"}}
    result = await client.post(f"/tables/{table_id}/moves", json={"move": move, "base_seq": 0})
    assert result.status_code == 409
    body = result.json()
    assert body["code"] == "seat_token_mismatch"
    assert isinstance(body["detail"], str)


async def test_off_turn_move_carries_not_your_turn(client: httpx.AsyncClient) -> None:
    created = await client.post("/tables", json={"scheme": "literaki", "seats": 2, "name": "Ala"})
    data = created.json()
    joined = await client.post(f"/tables/{data['code']}/join", json={"name": "Ola"})
    other = joined.json()
    move = {"player": 1, "action": {"kind": "pass"}}
    result = await client.post(
        f"/tables/{data['table_id']}/moves",
        json={"move": move, "base_seq": 0},
        headers={"X-Seat-Token": other["token"]},
    )
    assert result.status_code == 409
    assert result.json()["code"] == "not_your_turn"


async def test_premove_queue_and_cancel_over_http(client: httpx.AsyncClient) -> None:
    created = await client.post("/tables", json={"scheme": "literaki", "seats": 2, "name": "Ala"})
    data = created.json()
    joined = await client.post(f"/tables/{data['code']}/join", json={"name": "Ola"})
    other = joined.json()
    seen = await client.get(
        f"/tables/{data['table_id']}/view", headers={"X-Seat-Token": other["token"]}
    )
    rack = seen.json()["view"]["racks"]["1"]
    move = {"player": 1, "action": {"kind": "exchange", "tile_ids": [rack[0]["identifier"]]}}
    queued = await client.post(
        f"/tables/{data['table_id']}/moves",
        json={"move": move, "base_seq": 0, "premove": True},
        headers={"X-Seat-Token": other["token"]},
    )
    assert queued.status_code == 200
    assert queued.json()["seq"] == 1
    refused = await client.post(
        f"/tables/{data['table_id']}/moves",
        json={"move": {"player": 1, "action": {"kind": "pass"}}, "base_seq": 1, "premove": True},
        headers={"X-Seat-Token": other["token"]},
    )
    assert refused.status_code == 409
    assert refused.json()["code"] == "illegal_move"
    view = await client.get(
        f"/tables/{data['table_id']}/view", headers={"X-Seat-Token": other["token"]}
    )
    assert view.json()["view"]["premove"] is not None
    assert view.json()["view"]["pending_premoves"] == [1]
    cancelled = await client.delete(
        f"/tables/{data['table_id']}/premove",
        params={"base_seq": 1},
        headers={"X-Seat-Token": other["token"]},
    )
    assert cancelled.status_code == 200
    assert cancelled.json()["seq"] == 2
    repeated = await client.delete(
        f"/tables/{data['table_id']}/premove",
        params={"base_seq": 2},
        headers={"X-Seat-Token": other["token"]},
    )
    assert repeated.status_code == 409
    assert repeated.json()["code"] == "no_premove"
    unauthorized = await client.delete(
        f"/tables/{data['table_id']}/premove", params={"base_seq": 2}
    )
    assert unauthorized.status_code == 409
    assert unauthorized.json()["code"] == "seat_token_mismatch"


async def test_stale_position_carries_code(client: httpx.AsyncClient) -> None:
    created = await client.post("/tables", json={"scheme": "literaki", "seats": 2, "name": "Ala"})
    data = created.json()
    await client.post(f"/tables/{data['code']}/join", json={"name": "Ola"})
    move = {"player": 0, "action": {"kind": "pass"}}
    result = await client.post(
        f"/tables/{data['table_id']}/moves",
        json={"move": move, "base_seq": 5},
        headers={"X-Seat-Token": data["token"]},
    )
    assert result.status_code == 409
    assert result.json()["code"] == "stale_position"


async def test_transport_refusals_carry_codes(client: httpx.AsyncClient) -> None:
    view = await client.get("/tables/absent/view")
    assert view.status_code == 404
    assert view.json()["code"] == "unknown_table"
    scheme = await client.post("/tables", json={"scheme": "absent", "seats": 2, "name": "Ala"})
    assert scheme.status_code == 404
    assert scheme.json()["code"] == "unknown_scheme"
    joined = await client.post("/tables/ZZZZZZ/join", json={"name": "Ola"})
    assert joined.status_code == 404
    assert joined.json()["code"] == "unknown_code"
    seats = await client.post("/tables", json={"scheme": "literaki", "seats": 9, "name": "Ala"})
    assert seats.status_code == 422
    assert seats.json()["code"] == "seats_out_of_range"


async def test_names_are_trimmed_and_served_in_company(client: httpx.AsyncClient) -> None:
    created = await client.post(
        "/tables", json={"scheme": "literaki", "seats": 2, "name": "  Ala  "}
    )
    data = created.json()
    assert data["name"] == "Ala"
    await client.post(f"/tables/{data['code']}/join", json={"name": " Ola "})
    view = await client.get(f"/tables/{data['table_id']}/view")
    company = view.json()["company"]["seats"]
    assert [seat["name"] for seat in company] == ["Ala", "Ola"]
    assert all(seat["claimed"] for seat in company)


async def test_blank_names_are_refused(client: httpx.AsyncClient) -> None:
    created = await client.post("/tables", json={"scheme": "literaki", "seats": 2, "name": "   "})
    assert created.status_code == 422
    nameless = await client.post("/tables", json={"scheme": "literaki", "seats": 2})
    assert nameless.status_code == 422
    host = await client.post("/tables", json={"scheme": "literaki", "seats": 2, "name": "Ala"})
    code = host.json()["code"]
    blank = await client.post(f"/tables/{code}/join", json={"name": " "})
    assert blank.status_code == 422
    bodiless = await client.post(f"/tables/{code}/join")
    assert bodiless.status_code == 422


async def test_overlong_name_is_rejected(client: httpx.AsyncClient) -> None:
    response = await client.post(
        "/tables", json={"scheme": "literaki", "seats": 2, "name": "x" * 33}
    )
    assert response.status_code == 422


async def test_style_endpoint_serves_tokens(client: httpx.AsyncClient) -> None:
    response = await client.get("/style")
    assert response.status_code == 200
    tokens = StyleTokens.model_validate(response.json())
    assert tokens.name == "default"
    assert tokens.light.board.surface != tokens.dark.board.surface


async def test_word_check_judges_asked_words(client: httpx.AsyncClient) -> None:
    created = await client.post("/tables", json={"scheme": "literaki", "seats": 2, "name": "Ala"})
    table_id = created.json()["table_id"]
    described = await client.get(f"/tables/{table_id}")
    assert described.json()["parameters"]["word_check"] is True
    response = await client.get(f"/tables/{table_id}/words", params={"words": ["dom", "kotz", " "]})
    assert response.status_code == 200
    verdicts = WordVerdicts.model_validate(response.json())
    assert set(verdicts.verdicts) == {"DOM", "KOTZ"}
    assert verdicts.verdicts["DOM"].allowed is True
    assert verdicts.verdicts["KOTZ"].allowed is False


async def test_word_check_refuses_an_overlong_request(client: httpx.AsyncClient) -> None:
    created = await client.post("/tables", json={"scheme": "literaki", "seats": 2, "name": "Ala"})
    table_id = created.json()["table_id"]
    asked = [f"WORD{index}" for index in range(MAX_JUDGED_WORDS + 1)]
    response = await client.get(f"/tables/{table_id}/words", params={"words": asked})
    assert response.status_code == 422
    assert response.json()["code"] == "too_many_words"


async def test_created_table_carries_the_asked_time_control(client: httpx.AsyncClient) -> None:
    created = await client.post(
        "/tables",
        json={
            "scheme": "literaki",
            "seats": 2,
            "name": "Ala",
            "time": {"total_seconds": 600, "increment_seconds": 15},
        },
    )
    data = created.json()
    described = await client.get(f"/tables/{data['table_id']}")
    assert described.json()["parameters"]["time"] == {
        "per_turn_seconds": None,
        "increment_seconds": 15,
        "total_seconds": 600,
    }
    await client.post(f"/tables/{data['code']}/join", json={"name": "Ola"})
    view = await client.get(
        f"/tables/{data['table_id']}/view", headers={"X-Seat-Token": data["token"]}
    )
    clock = view.json()["clock"]
    assert clock is not None
    assert clock["remaining"] == {"0": 600.0, "1": 600.0}
    assert clock["seat"] == 0


async def test_time_control_stays_within_bounds(client: httpx.AsyncClient) -> None:
    response = await client.post(
        "/tables",
        json={"scheme": "literaki", "seats": 2, "time": {"total_seconds": 5}},
    )
    assert response.status_code == 422


async def test_responses_validate_against_models(client: httpx.AsyncClient) -> None:
    created = await client.post("/tables", json={"scheme": "literaki", "seats": 2, "name": "Ala"})
    admission = TableAdmission.model_validate(created.json())
    view = await client.get(
        f"/tables/{admission.table_id}/view", headers={"X-Seat-Token": admission.token}
    )
    validated = TableViewResponse.model_validate(view.json())
    assert validated.seq == 0
    assert validated.view.board.size == 15


def test_openapi_document_carries_schemas(app) -> None:
    document = app.openapi()
    schemas = document["components"]["schemas"]
    expected = {
        "PositionView",
        "EventView",
        "ErrorBody",
        "TableAdmission",
        "TableViewResponse",
        "OfferingsResponse",
        "Offering",
        "TableDescription",
        "RuleParameters",
        "MoveAccepted",
        "MoveRequest",
        "WordVerdict",
        "WordVerdicts",
        "Tile",
        "Board",
    }
    assert expected <= set(schemas)


def test_openapi_script_writes_document(tmp_path) -> None:
    output = tmp_path / "openapi.json"
    main(output)
    document = json.loads(output.read_text(encoding="utf-8"))
    assert "openapi" in document
    assert "components" in document
