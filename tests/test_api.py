"""Tests for the GoogleRoutesApiClient (custom_components/google_transit_routes/api.py)."""

import json
from pathlib import Path

import pytest
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from custom_components.google_transit_routes.api import API_URL, GoogleRoutesApiClient
from custom_components.google_transit_routes.exceptions import (
    ApiUnavailable,
    InvalidApiKey,
    InvalidRequest,
    RateLimited,
)

FIXTURES = Path(__file__).parent / "fixtures"


def _load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


async def test_get_transit_route_success(hass, aioclient_mock):
    """A successful transit request returns the parsed JSON body and correct headers."""
    fixture = _load_fixture("transit_response.json")
    aioclient_mock.post(API_URL, json=fixture)

    session = async_get_clientsession(hass)
    client = GoogleRoutesApiClient("test-key", session)

    result = await client.get_transit_route(
        origin={"address": "UMCG Noord, Groningen"},
        destination={"address": "Station Meadowfield"},
        language="nl",
    )

    assert result == fixture
    assert aioclient_mock.call_count == 1
    headers = aioclient_mock.mock_calls[0][3]
    assert headers["X-Goog-Api-Key"] == "test-key"
    assert "routes.legs.steps.transitDetails" in headers["X-Goog-FieldMask"]


async def test_get_travel_time_success(hass, aioclient_mock):
    """A successful driving request returns the parsed JSON body."""
    fixture = _load_fixture("travel_response.json")
    aioclient_mock.post(API_URL, json=fixture)

    session = async_get_clientsession(hass)
    client = GoogleRoutesApiClient("test-key", session)

    result = await client.get_travel_time(
        origin={"address": "Amsterdam"},
        destination={"address": "Rotterdam"},
        mode="driving",
        language="nl",
    )

    assert result == fixture


async def test_validate_api_key_success(hass, aioclient_mock):
    """validate_api_key returns True when the API responds with 200."""
    aioclient_mock.post(API_URL, json={"routes": [{"duration": "100s"}]})

    session = async_get_clientsession(hass)
    client = GoogleRoutesApiClient("test-key", session)

    assert await client.validate_api_key() is True


@pytest.mark.parametrize(
    ("status", "exception"),
    [
        (400, InvalidRequest),
        (403, InvalidApiKey),
        (429, RateLimited),
        (500, ApiUnavailable),
        (503, ApiUnavailable),
    ],
)
async def test_error_status_codes_raise(hass, aioclient_mock, status, exception):
    """Each HTTP error status maps to the documented exception type."""
    aioclient_mock.post(API_URL, status=status, text="error detail")

    session = async_get_clientsession(hass)
    client = GoogleRoutesApiClient("test-key", session)

    with pytest.raises(exception):
        await client.get_transit_route(
            origin={"address": "A"}, destination={"address": "B"}, language="en"
        )
