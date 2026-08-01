"""DataUpdateCoordinator for a single saved Google Transit Routes route.

Deliberately has no automatic polling interval (update_interval=None): a
transit query hits the Compute Routes Pro SKU, which has a free cap of only
5,000 requests/month. Data is only refreshed when explicitly requested via
the homeassistant.update_entity action.
"""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigSubentry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import GoogleRoutesApiClient
from .const import CONF_DESTINATION, CONF_LANGUAGE, CONF_ORIGIN, DEFAULT_LANGUAGE, DOMAIN
from .exceptions import GoogleRoutesApiError
from .helpers import parse_transit_response, resolve_location

_LOGGER = logging.getLogger(__name__)


class GoogleTransitRouteCoordinator(DataUpdateCoordinator[list[dict[str, Any]]]):
    """Fetch and cache transit routes for a single saved route, on demand only."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: GoogleRoutesApiClient,
        subentry: ConfigSubentry,
    ) -> None:
        """Initialise the coordinator for one saved route."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{subentry.title}",
            update_interval=None,
        )
        self.client = client
        self.subentry = subentry

    async def _async_update_data(self) -> list[dict[str, Any]]:
        """Fetch a fresh set of routes from the Google Routes API."""
        route_data = self.subentry.data
        language = route_data.get(CONF_LANGUAGE, DEFAULT_LANGUAGE)
        try:
            origin = resolve_location(self.hass, route_data[CONF_ORIGIN])
            destination = resolve_location(self.hass, route_data[CONF_DESTINATION])
            response = await self.client.get_transit_route(
                origin=origin,
                destination=destination,
                language=language,
                alternatives=True,
            )
        except GoogleRoutesApiError as err:
            raise UpdateFailed(f"Error communicating with Google Routes API: {err}") from err
        except ValueError as err:
            raise UpdateFailed(str(err)) from err

        routes = parse_transit_response(response, language)
        if not routes:
            raise UpdateFailed("No transit routes found")
        return routes
