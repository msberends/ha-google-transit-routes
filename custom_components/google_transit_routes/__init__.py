"""The Google Transit Routes integration."""

from __future__ import annotations

import logging
from pathlib import Path

import voluptuous as vol
from homeassistant.components.frontend import add_extra_js_url
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse, SupportsResponse
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import GoogleRoutesApiClient
from .const import (
    ATTR_ALTERNATIVES,
    ATTR_ARRIVAL_TIME,
    ATTR_AVOID,
    ATTR_DEPARTURE_TIME,
    ATTR_DESTINATION,
    ATTR_LANGUAGE,
    ATTR_MODE,
    ATTR_ORIGIN,
    ATTR_ROUTING_PREFERENCE,
    ATTR_TRAFFIC_MODEL,
    ATTR_TRANSIT_MODE,
    CONF_API_KEY,
    DEFAULT_ALTERNATIVES,
    DEFAULT_LANGUAGE,
    DOMAIN,
    SERVICE_GET_TRANSIT_ROUTE,
    SERVICE_GET_TRAVEL_TIME,
)
from .exceptions import GoogleRoutesApiError
from .helpers import parse_transit_response, parse_travel_response, resolve_location

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[str] = ["sensor"]

CARD_FILENAME = "google-transit-routes-card.js"
CARD_URL_PATH = f"/{DOMAIN}_static/{CARD_FILENAME}"

GET_TRANSIT_ROUTE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ORIGIN): cv.string,
        vol.Required(ATTR_DESTINATION): cv.string,
        vol.Optional(ATTR_LANGUAGE, default=DEFAULT_LANGUAGE): cv.string,
        vol.Optional(ATTR_DEPARTURE_TIME): cv.string,
        vol.Optional(ATTR_ARRIVAL_TIME): cv.string,
        vol.Optional(ATTR_ALTERNATIVES, default=DEFAULT_ALTERNATIVES): cv.boolean,
        vol.Optional(ATTR_TRANSIT_MODE): vol.All(cv.ensure_list, [cv.string]),
        vol.Optional(ATTR_ROUTING_PREFERENCE): cv.string,
    }
)

GET_TRAVEL_TIME_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ORIGIN): cv.string,
        vol.Required(ATTR_DESTINATION): cv.string,
        vol.Required(ATTR_MODE): vol.In(
            ["driving", "walking", "bicycling", "two_wheeler"]
        ),
        vol.Optional(ATTR_LANGUAGE, default=DEFAULT_LANGUAGE): cv.string,
        vol.Optional(ATTR_DEPARTURE_TIME): cv.string,
        vol.Optional(ATTR_AVOID): vol.All(cv.ensure_list, [cv.string]),
        vol.Optional(ATTR_TRAFFIC_MODEL): cv.string,
    }
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Google Transit Routes from a config entry."""
    session = async_get_clientsession(hass)
    client = GoogleRoutesApiClient(entry.data[CONF_API_KEY], session)

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {"client": client}

    _async_register_services(hass)
    await _async_register_card(hass)

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def _async_register_card(hass: HomeAssistant) -> None:
    """Serve the Lovelace card and register it as a frontend module, once."""
    registered_key = f"{DOMAIN}_card_registered"
    if hass.data.get(registered_key):
        return
    hass.data[registered_key] = True

    file_path = str(Path(__file__).parent / "www" / CARD_FILENAME)

    if hasattr(hass.http, "async_register_static_paths"):
        from homeassistant.components.http import StaticPathConfig

        await hass.http.async_register_static_paths(
            [StaticPathConfig(CARD_URL_PATH, file_path, cache_headers=True)]
        )
    else:
        hass.http.register_static_path(CARD_URL_PATH, file_path, cache_headers=True)

    add_extra_js_url(hass, CARD_URL_PATH)


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the entry when its options change (e.g. saved routes edited)."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
        if not hass.data[DOMAIN]:
            hass.services.async_remove(DOMAIN, SERVICE_GET_TRANSIT_ROUTE)
            hass.services.async_remove(DOMAIN, SERVICE_GET_TRAVEL_TIME)
    return unload_ok


def _get_client(hass: HomeAssistant) -> GoogleRoutesApiClient:
    """Return the API client for the (single) configured entry."""
    entries = hass.data.get(DOMAIN, {})
    if not entries:
        raise HomeAssistantError("Google Transit Routes is not configured")
    return next(iter(entries.values()))["client"]


def _async_register_services(hass: HomeAssistant) -> None:
    """Register the get_transit_route and get_travel_time actions, once."""
    if hass.services.has_service(DOMAIN, SERVICE_GET_TRANSIT_ROUTE):
        return

    async def handle_get_transit_route(call: ServiceCall) -> ServiceResponse:
        client = _get_client(hass)
        try:
            origin = resolve_location(hass, call.data[ATTR_ORIGIN])
            destination = resolve_location(hass, call.data[ATTR_DESTINATION])
            language = call.data[ATTR_LANGUAGE]
            response = await client.get_transit_route(
                origin=origin,
                destination=destination,
                language=language,
                departure_time=call.data.get(ATTR_DEPARTURE_TIME),
                arrival_time=call.data.get(ATTR_ARRIVAL_TIME),
                alternatives=call.data[ATTR_ALTERNATIVES],
                transit_mode=call.data.get(ATTR_TRANSIT_MODE),
                routing_preference=call.data.get(ATTR_ROUTING_PREFERENCE),
            )
            routes = parse_transit_response(response, language)
        except GoogleRoutesApiError as err:
            raise HomeAssistantError(f"Google Routes API error: {err}") from err
        except ValueError as err:
            raise HomeAssistantError(str(err)) from err
        return {"routes": routes}

    async def handle_get_travel_time(call: ServiceCall) -> ServiceResponse:
        client = _get_client(hass)
        try:
            origin = resolve_location(hass, call.data[ATTR_ORIGIN])
            destination = resolve_location(hass, call.data[ATTR_DESTINATION])
            response = await client.get_travel_time(
                origin=origin,
                destination=destination,
                mode=call.data[ATTR_MODE],
                language=call.data[ATTR_LANGUAGE],
                departure_time=call.data.get(ATTR_DEPARTURE_TIME),
                avoid=call.data.get(ATTR_AVOID),
                traffic_model=call.data.get(ATTR_TRAFFIC_MODEL),
            )
            routes = parse_travel_response(response)
        except GoogleRoutesApiError as err:
            raise HomeAssistantError(f"Google Routes API error: {err}") from err
        except ValueError as err:
            raise HomeAssistantError(str(err)) from err
        return {"routes": routes}

    hass.services.async_register(
        DOMAIN,
        SERVICE_GET_TRANSIT_ROUTE,
        handle_get_transit_route,
        schema=GET_TRANSIT_ROUTE_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_GET_TRAVEL_TIME,
        handle_get_travel_time,
        schema=GET_TRAVEL_TIME_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )
