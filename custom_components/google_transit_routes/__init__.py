"""The Google Transit Routes integration."""

from __future__ import annotations

import logging
from pathlib import Path

import voluptuous as vol
from aiohttp import web
from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import KEY_HASS, HomeAssistantView
from homeassistant.config_entries import ConfigEntry, ConfigSubentry
from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse, SupportsResponse
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.loader import async_get_integration
from homeassistant.util import slugify

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
    CONF_DESTINATION,
    CONF_LANGUAGE,
    CONF_ORIGIN,
    CONF_ROUTE_NAME,
    CONF_ROUTES,
    DEFAULT_ALTERNATIVES,
    DEFAULT_LANGUAGE,
    DOMAIN,
    SERVICE_GET_TRANSIT_ROUTE,
    SERVICE_GET_TRAVEL_TIME,
    SUBENTRY_TYPE_ROUTE,
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


class _CardJSView(HomeAssistantView):
    """Serve the Lovelace card JS with an explicit Cache-Control: no-store.

    HA's built-in static-path helper either sets an aggressive 31-day cache
    (cache_headers=True) or no Cache-Control header at all
    (cache_headers=False) — neither is safe here: with no explicit header, a
    client is free to apply its own caching heuristics, and at least one
    real client (the iOS app's WKWebView) has been observed getting stuck
    serving a single bad/interrupted fetch indefinitely. no-store forces
    every fetch to be a genuine network request, which combined with the
    version-busted URL in _async_register_card removes any ambiguity.
    """

    requires_auth = False
    url = CARD_URL_PATH
    name = "google_transit_routes:card_js"

    def __init__(self, file_path: Path) -> None:
        """Store the on-disk path to the compiled card bundle."""
        self._file_path = file_path

    async def get(self, request: web.Request) -> web.Response:
        """Return the card's JS source, read fresh from disk every time."""
        hass: HomeAssistant = request.app[KEY_HASS]
        content = await hass.async_add_executor_job(self._file_path.read_bytes)
        return web.Response(
            body=content,
            content_type="text/javascript",
            headers={"Cache-Control": "no-store"},
        )


async def _async_register_card(hass: HomeAssistant) -> None:
    """Serve the Lovelace card and register it as a frontend module, once."""
    registered_key = f"{DOMAIN}_card_registered"
    if hass.data.get(registered_key):
        return

    file_path = Path(__file__).parent / "www" / CARD_FILENAME

    try:
        hass.http.register_view(_CardJSView(file_path))

        # Append the integration version so the URL itself changes on every
        # release, forcing clients to fetch the new file instead of serving
        # a previously cached one.
        integration = await async_get_integration(hass, DOMAIN)
        add_extra_js_url(hass, f"{CARD_URL_PATH}?v={integration.version}")
    except Exception:  # noqa: BLE001 - registering the card must not block sensor setup
        _LOGGER.exception("Failed to register the Lovelace card")
        return

    # Only mark registration done once every step above has actually
    # succeeded — otherwise a transient failure here (e.g. during a racy
    # startup) would permanently skip the card for the rest of this HA
    # process's lifetime, with the failure never surfaced anywhere.
    hass.data[registered_key] = True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the entry when it changes (e.g. a saved route subentry is added,
    reconfigured, or removed)."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate saved routes from the legacy options list into subentries.

    Pre-0.2.0, every saved route lived in `entry.options[CONF_ROUTES]` and was
    edited through a bespoke options-flow menu. From 0.2.0 on, each route is
    its own config subentry, giving it a dedicated block in the integration UI
    with proper add/reconfigure/remove support. This runs once per entry, the
    first time it's loaded after upgrading.
    """
    if entry.version == 1 and entry.minor_version == 1:
        entity_registry = er.async_get(hass)

        for route in entry.options.get(CONF_ROUTES, []):
            subentry = ConfigSubentry(
                data={
                    CONF_ORIGIN: route[CONF_ORIGIN],
                    CONF_DESTINATION: route[CONF_DESTINATION],
                    CONF_LANGUAGE: route.get(CONF_LANGUAGE, DEFAULT_LANGUAGE),
                },
                subentry_type=SUBENTRY_TYPE_ROUTE,
                title=route[CONF_ROUTE_NAME],
                unique_id=None,
            )
            hass.config_entries.async_add_subentry(entry, subentry)

            legacy_unique_id = f"{DOMAIN}_{slugify(route[CONF_ROUTE_NAME])}"
            entity_id = entity_registry.async_get_entity_id(
                "sensor", DOMAIN, legacy_unique_id
            )
            if entity_id is not None:
                # Re-point the existing entity at the new subentry, keeping its
                # entity_id (and history/automations/dashboards) intact. Pre-0.2.0
                # sensors had no device, so there's no device to migrate here —
                # sensor.py creates the (new) per-route device on next setup.
                entity_registry.async_update_entity(
                    entity_id,
                    config_subentry_id=subentry.subentry_id,
                    new_unique_id=subentry.subentry_id,
                )

        hass.config_entries.async_update_entry(
            entry, options={}, minor_version=2
        )

    return True


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
