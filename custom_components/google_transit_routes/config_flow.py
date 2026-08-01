"""Config flow for the Google Transit Routes integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import (
    SOURCE_USER,
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    ConfigSubentryFlow,
    FlowType,
    SubentryFlowContext,
    SubentryFlowResult,
)
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import GoogleRoutesApiClient
from .const import (
    CONF_API_KEY,
    CONF_DESTINATION,
    CONF_LANGUAGE,
    CONF_ORIGIN,
    CONF_ROUTE_NAME,
    DEFAULT_LANGUAGE,
    DOMAIN,
    SUBENTRY_TYPE_ROUTE,
)
from .exceptions import ApiUnavailable, InvalidApiKey, InvalidRequest, RateLimited

_LOGGER = logging.getLogger(__name__)

ROUTE_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_ROUTE_NAME): str,
        vol.Required(CONF_ORIGIN): str,
        vol.Required(CONF_DESTINATION): str,
        vol.Optional(CONF_LANGUAGE, default=DEFAULT_LANGUAGE): str,
    }
)


async def _validate_api_key(hass, api_key: str) -> None:
    """Validate an API key by making a minimal test request. Raises on failure."""
    session = async_get_clientsession(hass)
    client = GoogleRoutesApiClient(api_key, session)
    await client.validate_api_key()


class GoogleTransitRoutesConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Google Transit Routes."""

    VERSION = 1
    MINOR_VERSION = 2

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
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
                return self.async_create_entry(
                    title="Google Transit Routes",
                    data={CONF_API_KEY: api_key},
                    options={},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_API_KEY): str}),
            errors=errors,
        )

    async def async_on_create_entry(
        self, result: ConfigFlowResult
    ) -> ConfigFlowResult:
        """Offer to add the first saved route right after the entry is created."""
        subentry_result = await self.hass.config_entries.subentries.async_init(
            (result["result"].entry_id, SUBENTRY_TYPE_ROUTE),
            context=SubentryFlowContext(source=SOURCE_USER),
        )
        result["next_flow"] = (
            FlowType.CONFIG_SUBENTRIES_FLOW,
            subentry_result["flow_id"],
        )
        return result

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Change the stored API key for an existing entry."""
        errors: dict[str, str] = {}
        entry = self._get_reconfigure_entry()

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
                return self.async_update_and_abort(
                    entry, data_updates={CONF_API_KEY: api_key}
                )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema({vol.Required(CONF_API_KEY): str}),
            errors=errors,
        )

    @classmethod
    @callback
    def async_get_supported_subentry_types(
        cls, config_entry: ConfigEntry
    ) -> dict[str, type[ConfigSubentryFlow]]:
        """Return subentry types supported by this integration."""
        return {SUBENTRY_TYPE_ROUTE: RouteSubentryFlowHandler}


class RouteSubentryFlowHandler(ConfigSubentryFlow):
    """Handle adding and reconfiguring a single saved route."""

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        """Add a new saved route."""
        errors: dict[str, str] = {}

        if user_input is not None:
            name = user_input[CONF_ROUTE_NAME]
            if any(
                subentry.title == name
                for subentry in self._get_entry().subentries.values()
            ):
                errors["base"] = "already_configured"
            else:
                return self.async_create_entry(
                    title=name,
                    data={
                        CONF_ORIGIN: user_input[CONF_ORIGIN],
                        CONF_DESTINATION: user_input[CONF_DESTINATION],
                        CONF_LANGUAGE: user_input.get(
                            CONF_LANGUAGE, DEFAULT_LANGUAGE
                        ),
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=self.add_suggested_values_to_schema(
                data_schema=ROUTE_DATA_SCHEMA, suggested_values=user_input
            ),
            errors=errors,
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        """Edit an existing saved route (name, origin, destination, language)."""
        errors: dict[str, str] = {}
        entry = self._get_entry()
        subentry = self._get_reconfigure_subentry()

        if user_input is not None:
            name = user_input[CONF_ROUTE_NAME]
            if any(
                other.title == name
                for other in entry.subentries.values()
                if other.subentry_id != subentry.subentry_id
            ):
                errors["base"] = "already_configured"
            else:
                return self.async_update_and_abort(
                    entry=entry,
                    subentry=subentry,
                    title=name,
                    data_updates={
                        CONF_ORIGIN: user_input[CONF_ORIGIN],
                        CONF_DESTINATION: user_input[CONF_DESTINATION],
                        CONF_LANGUAGE: user_input.get(
                            CONF_LANGUAGE, DEFAULT_LANGUAGE
                        ),
                    },
                )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=self.add_suggested_values_to_schema(
                data_schema=ROUTE_DATA_SCHEMA,
                suggested_values={CONF_ROUTE_NAME: subentry.title, **subentry.data},
            ),
            errors=errors,
        )
