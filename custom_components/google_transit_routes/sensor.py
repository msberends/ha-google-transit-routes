"""Sensor platform for Google Transit Routes saved routes."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util
from homeassistant.util import slugify

from .const import (
    ATTRIBUTION,
    CONF_DESTINATION,
    CONF_LANGUAGE,
    CONF_ORIGIN,
    CONF_ROUTE_NAME,
    CONF_ROUTES,
    DEFAULT_LANGUAGE,
    DOMAIN,
)
from .coordinator import GoogleTransitRouteCoordinator
from .helpers import compute_duration_from_now

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up sensor entities for each saved route."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    client = entry_data["client"]
    routes = entry.options.get(CONF_ROUTES, [])

    coordinators: dict[str, GoogleTransitRouteCoordinator] = {}
    entities: list[GoogleTransitSensor] = []

    for route_config in routes:
        coordinator = GoogleTransitRouteCoordinator(hass, client, route_config)
        coordinators[route_config[CONF_ROUTE_NAME]] = coordinator
        entities.append(GoogleTransitSensor(coordinator, route_config))

    entry_data["coordinators"] = coordinators
    async_add_entities(entities)


class GoogleTransitSensor(CoordinatorEntity[GoogleTransitRouteCoordinator], SensorEntity):
    """Sensor showing the next arrival time for a saved transit route.

    Has no automatic polling: it only refreshes when the coordinator is
    explicitly triggered via the homeassistant.update_entity action.
    """

    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_attribution = ATTRIBUTION
    _attr_should_poll = False

    def __init__(
        self, coordinator: GoogleTransitRouteCoordinator, route_config: dict[str, Any]
    ) -> None:
        """Initialise the sensor for one saved route."""
        super().__init__(coordinator)
        self._route_config = route_config
        name = route_config[CONF_ROUTE_NAME]
        slug = slugify(name)
        self._attr_name = name
        self._attr_unique_id = f"{DOMAIN}_{slug}"
        self.entity_id = f"sensor.google_transit_{slug}"

    @property
    def native_value(self):
        """Return the UTC arrival time of the next (earliest) route."""
        routes = self.coordinator.data
        if not routes:
            return None
        return dt_util.parse_datetime(routes[0]["arrival_time"])

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return route details; duration_from_now is recomputed on every read."""
        attributes: dict[str, Any] = {
            "origin": self._route_config[CONF_ORIGIN],
            "destination": self._route_config[CONF_DESTINATION],
            "attribution": ATTRIBUTION,
        }

        routes = self.coordinator.data
        if not routes:
            return attributes

        language = self._route_config.get(CONF_LANGUAGE, DEFAULT_LANGUAGE)
        primary = routes[0]
        alternatives = routes[1:]

        duration_from_now, duration_from_now_text = compute_duration_from_now(
            primary["arrival_time"], language
        )

        attributes.update(
            {
                "arrival_time": primary["arrival_time"],
                "arrival_time_local": primary["arrival_time_local"],
                "departure_time": primary["departure_time"],
                "departure_time_local": primary["departure_time_local"],
                "duration": primary["duration"],
                "duration_text": primary["duration_text"],
                "duration_from_now": duration_from_now,
                "duration_from_now_text": duration_from_now_text,
                "distance_text": primary["distance_text"],
                "legs": primary["legs"],
                "alternative_routes": alternatives,
                "route_count": len(routes),
            }
        )
        return attributes
