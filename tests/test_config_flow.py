"""Tests for the Google Transit Routes config and options flow."""

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResultType

from custom_components.google_transit_routes.api import API_URL
from custom_components.google_transit_routes.const import (
    CONF_API_KEY,
    CONF_DESTINATION,
    CONF_LANGUAGE,
    CONF_ORIGIN,
    CONF_ROUTE_NAME,
    CONF_ROUTES,
    DOMAIN,
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


async def test_user_flow_skip_route_creates_entry_with_no_routes(hass, aioclient_mock):
    """Skipping the add_route step still creates a working config entry."""
    aioclient_mock.post(API_URL, json=VALID_KEY_RESPONSE)

    result = await _start_user_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_API_KEY: "good-key"}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "add_route"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"add_another": False}
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"] == {CONF_API_KEY: "good-key"}
    assert result["options"] == {CONF_ROUTES: []}


async def test_user_flow_add_one_route(hass, aioclient_mock):
    """Filling in a route on the add_route step saves it to options."""
    aioclient_mock.post(API_URL, json=VALID_KEY_RESPONSE)

    result = await _start_user_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_API_KEY: "good-key"}
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_ROUTE_NAME: "UMCG naar Meadowfield",
            CONF_ORIGIN: "UMCG Noord, Groningen",
            CONF_DESTINATION: "Station Meadowfield",
            CONF_LANGUAGE: "nl",
            "add_another": False,
        },
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["options"][CONF_ROUTES] == [
        {
            CONF_ROUTE_NAME: "UMCG naar Meadowfield",
            CONF_ORIGIN: "UMCG Noord, Groningen",
            CONF_DESTINATION: "Station Meadowfield",
            CONF_LANGUAGE: "nl",
        }
    ]


async def test_user_flow_add_another_loops_back(hass, aioclient_mock):
    """Checking 'add_another' returns to the add_route step instead of finishing."""
    aioclient_mock.post(API_URL, json=VALID_KEY_RESPONSE)

    result = await _start_user_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_API_KEY: "good-key"}
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_ROUTE_NAME: "Route 1",
            CONF_ORIGIN: "A",
            CONF_DESTINATION: "B",
            "add_another": True,
        },
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "add_route"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_ROUTE_NAME: "Route 2",
            CONF_ORIGIN: "C",
            CONF_DESTINATION: "D",
            "add_another": False,
        },
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert [r[CONF_ROUTE_NAME] for r in result["options"][CONF_ROUTES]] == [
        "Route 1",
        "Route 2",
    ]


async def test_user_flow_aborts_if_already_configured(hass, aioclient_mock, mock_config_entry):
    """A second config entry cannot be created once one already exists."""
    mock_config_entry.add_to_hass(hass)

    result = await _start_user_flow(hass)

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_options_change_api_key(hass, aioclient_mock, mock_config_entry):
    """The options flow can update the stored API key after validation."""
    mock_config_entry.add_to_hass(hass)
    aioclient_mock.post(API_URL, json=VALID_KEY_RESPONSE)

    result = await hass.config_entries.options.async_init(mock_config_entry.entry_id)
    assert result["type"] is FlowResultType.MENU

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "change_api_key"}
    )
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {CONF_API_KEY: "new-key"}
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert mock_config_entry.data[CONF_API_KEY] == "new-key"


async def test_options_add_route(hass, aioclient_mock, mock_config_entry):
    """The options flow can append a new saved route."""
    mock_config_entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(mock_config_entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "add_route"}
    )
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {
            CONF_ROUTE_NAME: "New route",
            CONF_ORIGIN: "X",
            CONF_DESTINATION: "Y",
            CONF_LANGUAGE: "en",
        },
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_ROUTES][-1][CONF_ROUTE_NAME] == "New route"


async def test_options_remove_route(hass, aioclient_mock, mock_config_entry):
    """The options flow can remove a previously saved route."""
    mock_config_entry.add_to_hass(hass)
    hass.config_entries.async_update_entry(
        mock_config_entry,
        options={
            CONF_ROUTES: [
                {
                    CONF_ROUTE_NAME: "Route to remove",
                    CONF_ORIGIN: "A",
                    CONF_DESTINATION: "B",
                    CONF_LANGUAGE: "en",
                }
            ]
        },
    )

    result = await hass.config_entries.options.async_init(mock_config_entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "remove_route"}
    )
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"route_name": ["Route to remove"]}
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_ROUTES] == []


async def test_options_remove_route_aborts_when_no_routes(hass, mock_config_entry):
    """Trying to remove a route when none are saved aborts cleanly."""
    mock_config_entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(mock_config_entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "remove_route"}
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "no_routes"
