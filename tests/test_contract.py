import json

import httpx
import pytest
from scripts.openapi import main

from wordserver.app import create_app
from wordserver.models import TableAdmission, TableViewResponse
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
    created = await client.post("/tables", json={"scheme": "literaki", "seats": 2})
    table_id = created.json()["table_id"]
    move = {"player": 0, "action": {"kind": "pass"}}
    result = await client.post(f"/tables/{table_id}/moves", json={"move": move, "base_seq": 0})
    assert result.status_code == 409
    body = result.json()
    assert body["code"] == "not_your_turn"
    assert isinstance(body["detail"], str)


async def test_stale_position_carries_code(client: httpx.AsyncClient) -> None:
    created = await client.post("/tables", json={"scheme": "literaki", "seats": 2})
    data = created.json()
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
    scheme = await client.post("/tables", json={"scheme": "absent", "seats": 2})
    assert scheme.status_code == 404
    assert scheme.json()["code"] == "unknown_scheme"
    joined = await client.post("/tables/ZZZZZZ/join")
    assert joined.status_code == 404
    assert joined.json()["code"] == "unknown_code"
    seats = await client.post("/tables", json={"scheme": "literaki", "seats": 9})
    assert seats.status_code == 422
    assert seats.json()["code"] == "seats_out_of_range"


async def test_style_endpoint_serves_tokens(client: httpx.AsyncClient) -> None:
    response = await client.get("/style")
    assert response.status_code == 200
    tokens = StyleTokens.model_validate(response.json())
    assert tokens.name == "default"
    assert tokens.light.board.surface != tokens.dark.board.surface


async def test_responses_validate_against_models(client: httpx.AsyncClient) -> None:
    created = await client.post("/tables", json={"scheme": "literaki", "seats": 2})
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
        "MoveAccepted",
        "MoveRequest",
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
