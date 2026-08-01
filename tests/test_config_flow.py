"""Tests for the Google Transit Routes config flow and route subentry flow."""

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResultType

from custom_components.google_transit_routes.api import API_URL
from custom_components.google_transit_routes.const import (
    CONF_API_KEY,
    CONF_DESTINATION,
    CONF_LANGUAGE,
    CONF_ORIGIN,
    CONF_ROUTE_NAME,
    DOMAIN,
    SUBENTRY_TYPE_ROUTE,
)

VALID_KEY_RESPONSE = {"routes": [{"duration": "100s", "distanceMeters": 1000}]}


async def _start_user_flow(hass):
    return await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )


async def test_user_flow_invalid_api_key_shows_error(hass, aioclient_mock):
    """An API key rejected with 403 keeps the user on the form with an error."""
    aioclient_mock.post(API_URL, status=403, text="invalid key")

    result = await _start_user_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_API_KEY: "bad-key"}
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"
    assert result["errors"] == {"base": "invalid_api_key"}


async def test_user_flow_creates_entry_with_no_routes(hass, aioclient_mock):
    """A valid API key creates the entry; routes are added afterwards as subentries."""
    aioclient_mock.post(API_URL, json=VALID_KEY_RESPONSE)

    result = await _start_user_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_API_KEY: "good-key"}
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"] == {CONF_API_KEY: "good-key"}
    assert result["options"] == {}

    entry = hass.config_entries.async_entries(DOMAIN)[0]
    assert entry.subentries == {}


async def test_user_flow_aborts_if_already_configured(hass, aioclient_mock, mock_config_entry):
    """A second config entry cannot be created once one already exists."""
    mock_config_entry.add_to_hass(hass)

    result = await _start_user_flow(hass)

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_reconfigure_changes_api_key(hass, aioclient_mock, mock_config_entry):
    """The main entry's reconfigure flow can update the stored API key."""
    mock_config_entry.add_to_hass(hass)
    aioclient_mock.post(API_URL, json=VALID_KEY_RESPONSE)

    result = await mock_config_entry.start_reconfigure_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_API_KEY: "new-key"}
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"
    assert mock_config_entry.data[CONF_API_KEY] == "new-key"


async def test_reconfigure_invalid_api_key_shows_error(hass, aioclient_mock, mock_config_entry):
    """An invalid API key on reconfigure keeps the form open with an error."""
    mock_config_entry.add_to_hass(hass)
    aioclient_mock.post(API_URL, status=403, text="invalid key")

    result = await mock_config_entry.start_reconfigure_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_API_KEY: "bad-key"}
    )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_api_key"}


async def _start_route_subentry_flow(hass, mock_config_entry):
    return await hass.config_entries.subentries.async_init(
        (mock_config_entry.entry_id, SUBENTRY_TYPE_ROUTE),
        context={"source": config_entries.SOURCE_USER},
    )


async def test_add_route_subentry(hass, mock_config_entry):
    """Adding a route subentry stores it on the entry with the route name as title."""
    mock_config_entry.add_to_hass(hass)

    result = await _start_route_subentry_flow(hass, mock_config_entry)
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"],
        {
            CONF_ROUTE_NAME: "UMCG naar Meadowfield",
            CONF_ORIGIN: "UMCG Noord, Groningen",
            CONF_DESTINATION: "Station Meadowfield",
            CONF_LANGUAGE: "nl",
        },
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    (subentry,) = mock_config_entry.subentries.values()
    assert subentry.title == "UMCG naar Meadowfield"
    assert subentry.data == {
        CONF_ORIGIN: "UMCG Noord, Groningen",
        CONF_DESTINATION: "Station Meadowfield",
        CONF_LANGUAGE: "nl",
    }


async def test_add_route_subentry_duplicate_name_shows_error(hass, mock_config_entry):
    """A second route with the same name is rejected instead of silently added."""
    mock_config_entry.add_to_hass(hass)

    result = await _start_route_subentry_flow(hass, mock_config_entry)
    await hass.config_entries.subentries.async_configure(
        result["flow_id"],
        {CONF_ROUTE_NAME: "Route 1", CONF_ORIGIN: "A", CONF_DESTINATION: "B"},
    )

    result = await _start_route_subentry_flow(hass, mock_config_entry)
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"],
        {CONF_ROUTE_NAME: "Route 1", CONF_ORIGIN: "C", CONF_DESTINATION: "D"},
    )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "already_configured"}


async def test_reconfigure_route_subentry(hass, mock_config_entry):
    """An existing route subentry can be edited, including renaming it."""
    mock_config_entry.add_to_hass(hass)

    result = await _start_route_subentry_flow(hass, mock_config_entry)
    await hass.config_entries.subentries.async_configure(
        result["flow_id"],
        {CONF_ROUTE_NAME: "Route 1", CONF_ORIGIN: "A", CONF_DESTINATION: "B"},
    )
    (subentry,) = mock_config_entry.subentries.values()

    result = await mock_config_entry.start_subentry_reconfigure_flow(
        hass, subentry.subentry_id
    )
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"],
        {
            CONF_ROUTE_NAME: "Route 1 renamed",
            CONF_ORIGIN: "New origin",
            CONF_DESTINATION: "New destination",
            CONF_LANGUAGE: "en",
        },
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"

    (updated_subentry,) = mock_config_entry.subentries.values()
    assert updated_subentry.subentry_id == subentry.subentry_id
    assert updated_subentry.title == "Route 1 renamed"
    assert updated_subentry.data[CONF_ORIGIN] == "New origin"


async def test_reconfigure_route_subentry_duplicate_name_shows_error(
    hass, mock_config_entry
):
    """Renaming a route to clash with another saved route is rejected."""
    mock_config_entry.add_to_hass(hass)

    result = await _start_route_subentry_flow(hass, mock_config_entry)
    await hass.config_entries.subentries.async_configure(
        result["flow_id"],
        {CONF_ROUTE_NAME: "Route 1", CONF_ORIGIN: "A", CONF_DESTINATION: "B"},
    )
    result = await _start_route_subentry_flow(hass, mock_config_entry)
    await hass.config_entries.subentries.async_configure(
        result["flow_id"],
        {CONF_ROUTE_NAME: "Route 2", CONF_ORIGIN: "C", CONF_DESTINATION: "D"},
    )
    route_2 = next(
        s for s in mock_config_entry.subentries.values() if s.title == "Route 2"
    )

    result = await mock_config_entry.start_subentry_reconfigure_flow(
        hass, route_2.subentry_id
    )
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"],
        {CONF_ROUTE_NAME: "Route 1", CONF_ORIGIN: "C", CONF_DESTINATION: "D"},
    )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "already_configured"}
