"""Sensor platform for Google Transit Routes saved routes."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry, ConfigSubentry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import ATTRIBUTION, CONF_DESTINATION, CONF_LANGUAGE, CONF_ORIGIN, DEFAULT_LANGUAGE, DOMAIN
from .coordinator import GoogleTransitRouteCoordinator
from .helpers import compute_duration_from_now

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up one sensor entity per saved-route subentry."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    client = entry_data["client"]

    coordinators: dict[str, GoogleTransitRouteCoordinator] = {}

    for subentry_id, subentry in entry.subentries.items():
        coordinator = GoogleTransitRouteCoordinator(hass, client, subentry)
        coordinators[subentry_id] = coordinator
        async_add_entities(
            [GoogleTransitSensor(coordinator, subentry)],
            config_subentry_id=subentry_id,
        )

    entry_data["coordinators"] = coordinators

    if coordinators:
        await asyncio.gather(
            *(coordinator.async_refresh() for coordinator in coordinators.values())
        )


class GoogleTransitSensor(CoordinatorEntity[GoogleTransitRouteCoordinator], SensorEntity):
    """Sensor showing the next arrival time for a saved transit route.

    Has no automatic polling: it only refreshes when the coordinator is
    explicitly triggered via the homeassistant.update_entity action.
    """

    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_attribution = ATTRIBUTION
    _attr_should_poll = False
    _attr_has_entity_name = True
    _attr_name = None

    def __init__(
        self, coordinator: GoogleTransitRouteCoordinator, subentry: ConfigSubentry
    ) -> None:
        """Initialise the sensor for one saved route."""
        super().__init__(coordinator)
        self._subentry = subentry
        self._attr_unique_id = subentry.subentry_id
        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, subentry.subentry_id)},
            name=subentry.title,
            manufacturer="Matthijs Berends",
        )

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
            "origin": self._subentry.data[CONF_ORIGIN],
            "destination": self._subentry.data[CONF_DESTINATION],
            "attribution": ATTRIBUTION,
        }

        routes = self.coordinator.data
        if not routes:
            return attributes

        language = self._subentry.data.get(CONF_LANGUAGE, DEFAULT_LANGUAGE)
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
