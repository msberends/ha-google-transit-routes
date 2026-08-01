"""Config flow for the Google Transit Routes integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import GoogleRoutesApiClient
from .const import (
    CONF_API_KEY,
    CONF_DESTINATION,
    CONF_LANGUAGE,
    CONF_ORIGIN,
    CONF_ROUTE_NAME,
    CONF_ROUTES,
    DEFAULT_LANGUAGE,
    DOMAIN,
)
from .exceptions import ApiUnavailable, InvalidApiKey, InvalidRequest, RateLimited

_LOGGER = logging.getLogger(__name__)


async def _validate_api_key(hass, api_key: str) -> None:
    """Validate an API key by making a minimal test request. Raises on failure."""
    session = async_get_clientsession(hass)
    client = GoogleRoutesApiClient(api_key, session)
    await client.validate_api_key()


class GoogleTransitRoutesConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Google Transit Routes."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialise flow state."""
        self._api_key: str | None = None
        self._routes: list[dict[str, Any]] = []

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> Any:
        """Handle the initial step: API key entry and validation."""
        self._async_abort_entries_match({})
        errors: dict[str, str] = {}

        if user_input is not None:
            api_key = user_input[CONF_API_KEY]
            try:
                await _validate_api_key(self.hass, api_key)
            except InvalidApiKey:
                errors["base"] = "invalid_api_key"
            except InvalidRequest:
                errors["base"] = "invalid_request"
            except RateLimited:
                errors["base"] = "rate_limited"
            except ApiUnavailable:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Unexpected error validating API key")
                errors["base"] = "unknown"
            else:
                self._api_key = api_key
                return await self.async_step_add_route()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_API_KEY): str}),
            errors=errors,
        )

    async def async_step_add_route(
        self, user_input: dict[str, Any] | None = None
    ) -> Any:
        """Optionally add a saved route, looping until the user is done."""
        errors: dict[str, str] = {}

        if user_input is not None:
            name = user_input.get(CONF_ROUTE_NAME)
            origin = user_input.get(CONF_ORIGIN)
            destination = user_input.get(CONF_DESTINATION)
            if name and origin and destination:
                self._routes.append(
                    {
                        CONF_ROUTE_NAME: name,
                        CONF_ORIGIN: origin,
                        CONF_DESTINATION: destination,
                        CONF_LANGUAGE: user_input.get(
                            CONF_LANGUAGE, DEFAULT_LANGUAGE
                        ),
                    }
                )
            if user_input.get("add_another"):
                return await self.async_step_add_route()
            return self._async_create_entry()

        return self.async_show_form(
            step_id="add_route",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_ROUTE_NAME): str,
                    vol.Optional(CONF_ORIGIN): str,
                    vol.Optional(CONF_DESTINATION): str,
                    vol.Optional(CONF_LANGUAGE, default=DEFAULT_LANGUAGE): str,
                    vol.Optional("add_another", default=False): bool,
                }
            ),
            errors=errors,
        )

    def _async_create_entry(self) -> Any:
        """Create the config entry from the collected api key and routes."""
        return self.async_create_entry(
            title="Google Transit Routes",
            data={CONF_API_KEY: self._api_key},
            options={CONF_ROUTES: self._routes},
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Return the options flow handler."""
        return GoogleTransitRoutesOptionsFlow()


class GoogleTransitRoutesOptionsFlow(OptionsFlow):
    """Handle options: manage saved routes and the API key."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> Any:
        """Show the options menu."""
        return self.async_show_menu(
            step_id="init",
            menu_options=["change_api_key", "add_route", "remove_route"],
        )

    async def async_step_change_api_key(
        self, user_input: dict[str, Any] | None = None
    ) -> Any:
        """Change the stored API key."""
        errors: dict[str, str] = {}

        if user_input is not None:
            api_key = user_input[CONF_API_KEY]
            try:
                await _validate_api_key(self.hass, api_key)
            except InvalidApiKey:
                errors["base"] = "invalid_api_key"
            except InvalidRequest:
                errors["base"] = "invalid_request"
            except RateLimited:
                errors["base"] = "rate_limited"
            except ApiUnavailable:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Unexpected error validating API key")
                errors["base"] = "unknown"
            else:
                self.hass.config_entries.async_update_entry(
                    self.config_entry,
                    data={**self.config_entry.data, CONF_API_KEY: api_key},
                )
                return self.async_create_entry(title="", data=self.config_entry.options)

        return self.async_show_form(
            step_id="change_api_key",
            data_schema=vol.Schema({vol.Required(CONF_API_KEY): str}),
            errors=errors,
        )

    async def async_step_add_route(
        self, user_input: dict[str, Any] | None = None
    ) -> Any:
        """Add a saved route."""
        if user_input is not None:
            routes = list(self.config_entry.options.get(CONF_ROUTES, []))
            routes.append(
                {
                    CONF_ROUTE_NAME: user_input[CONF_ROUTE_NAME],
                    CONF_ORIGIN: user_input[CONF_ORIGIN],
                    CONF_DESTINATION: user_input[CONF_DESTINATION],
                    CONF_LANGUAGE: user_input.get(CONF_LANGUAGE, DEFAULT_LANGUAGE),
                }
            )
            return self.async_create_entry(
                title="", data={**self.config_entry.options, CONF_ROUTES: routes}
            )

        return self.async_show_form(
            step_id="add_route",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_ROUTE_NAME): str,
                    vol.Required(CONF_ORIGIN): str,
                    vol.Required(CONF_DESTINATION): str,
                    vol.Optional(CONF_LANGUAGE, default=DEFAULT_LANGUAGE): str,
                }
            ),
        )

    async def async_step_remove_route(
        self, user_input: dict[str, Any] | None = None
    ) -> Any:
        """Remove a saved route."""
        routes = list(self.config_entry.options.get(CONF_ROUTES, []))

        if not routes:
            return self.async_abort(reason="no_routes")

        names = {route[CONF_ROUTE_NAME]: route[CONF_ROUTE_NAME] for route in routes}

        if user_input is not None:
            remaining = [
                route
                for route in routes
                if route[CONF_ROUTE_NAME] not in user_input["route_name"]
            ]
            return self.async_create_entry(
                title="", data={**self.config_entry.options, CONF_ROUTES: remaining}
            )

        return self.async_show_form(
            step_id="remove_route",
            data_schema=vol.Schema(
                {vol.Required("route_name"): cv.multi_select(names)}
            ),
        )
