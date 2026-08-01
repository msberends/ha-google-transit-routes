"""Async client for the Google Routes API (computeRoutes)."""

from __future__ import annotations

import json
import logging
from typing import Any

import aiohttp

from .const import API_URL, TRANSIT_FIELD_MASK, TRAVEL_FIELD_MASK
from .exceptions import (
    ApiUnavailable,
    GoogleRoutesApiError,
    InvalidApiKey,
    InvalidRequest,
    RateLimited,
)

_LOGGER = logging.getLogger(__name__)

TRANSIT_MODE_MAP = {
    "bus": "BUS",
    "subway": "SUBWAY",
    "train": "TRAIN",
    "light_rail": "LIGHT_RAIL",
    "rail": "RAIL",
}

ROUTING_PREFERENCE_MAP = {
    "less_walking": "LESS_WALKING",
    "fewer_transfers": "FEWER_TRANSFERS",
}

TRAVEL_MODE_MAP = {
    "driving": "DRIVE",
    "walking": "WALK",
    "bicycling": "BICYCLE",
    "two_wheeler": "TWO_WHEELER",
}

AVOID_MODIFIER_MAP = {
    "tolls": "avoidTolls",
    "highways": "avoidHighways",
    "ferries": "avoidFerries",
    "indoor": "avoidIndoor",
}

TRAFFIC_MODEL_MAP = {
    "best_guess": "BEST_GUESS",
    "pessimistic": "PESSIMISTIC",
    "optimistic": "OPTIMISTIC",
}


class GoogleRoutesApiClient:
    """Thin async wrapper around the Google Routes API computeRoutes endpoint."""

    def __init__(self, api_key: str, session: aiohttp.ClientSession) -> None:
        """Initialise the client with an API key and a shared aiohttp session."""
        self._api_key = api_key
        self._session = session

    async def _post(self, body: dict[str, Any], field_mask: str) -> dict[str, Any]:
        """POST a computeRoutes request and return the parsed JSON response."""
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self._api_key,
            "X-Goog-FieldMask": field_mask,
        }
        _LOGGER.debug("Google Routes API request: %s", body)
        async with self._session.post(
            API_URL, data=json.dumps(body), headers=headers
        ) as response:
            text = await response.text()
            if response.status == 200:
                _LOGGER.debug("Google Routes API response: %s", text)
                return json.loads(text)
            _LOGGER.error(
                "Google Routes API error (status %s): %s", response.status, text
            )
            self._raise_for_status(response.status, text)
            raise GoogleRoutesApiError(text)  # unreachable, satisfies type checkers

    @staticmethod
    def _raise_for_status(status: int, text: str) -> None:
        """Translate an HTTP error status into a domain-specific exception."""
        if status == 400:
            raise InvalidRequest(text)
        if status == 403:
            raise InvalidApiKey(text)
        if status == 429:
            raise RateLimited(text)
        if status >= 500:
            raise ApiUnavailable(text)
        raise GoogleRoutesApiError(text)

    async def get_transit_route(
        self,
        origin: dict[str, Any],
        destination: dict[str, Any],
        language: str,
        departure_time: str | None = None,
        arrival_time: str | None = None,
        alternatives: bool = True,
        transit_mode: list[str] | None = None,
        routing_preference: str | None = None,
    ) -> dict[str, Any]:
        """Request a transit route and return the raw API response."""
        body: dict[str, Any] = {
            "origin": origin,
            "destination": destination,
            "travelMode": "TRANSIT",
            "languageCode": language,
            "units": "METRIC",
            "computeAlternativeRoutes": bool(alternatives),
        }
        if departure_time:
            body["departureTime"] = departure_time
        if arrival_time:
            body["arrivalTime"] = arrival_time

        transit_preferences: dict[str, Any] = {}
        if transit_mode:
            allowed = [
                TRANSIT_MODE_MAP[mode]
                for mode in transit_mode
                if mode in TRANSIT_MODE_MAP
            ]
            if allowed:
                transit_preferences["allowedTravelModes"] = allowed
        if routing_preference and routing_preference in ROUTING_PREFERENCE_MAP:
            transit_preferences["routingPreference"] = ROUTING_PREFERENCE_MAP[
                routing_preference
            ]
        if transit_preferences:
            body["transitPreferences"] = transit_preferences

        return await self._post(body, TRANSIT_FIELD_MASK)

    async def get_travel_time(
        self,
        origin: dict[str, Any],
        destination: dict[str, Any],
        mode: str,
        language: str,
        departure_time: str | None = None,
        avoid: list[str] | None = None,
        traffic_model: str | None = None,
    ) -> dict[str, Any]:
        """Request a driving/walking/bicycling/two-wheeler route."""
        body: dict[str, Any] = {
            "origin": origin,
            "destination": destination,
            "travelMode": TRAVEL_MODE_MAP.get(mode, "DRIVE"),
            "languageCode": language,
            "units": "METRIC",
        }
        if departure_time:
            body["departureTime"] = departure_time

        route_modifiers = {
            AVOID_MODIFIER_MAP[item]: True
            for item in (avoid or [])
            if item in AVOID_MODIFIER_MAP
        }
        if route_modifiers:
            body["routeModifiers"] = route_modifiers

        if body["travelMode"] == "DRIVE":
            if traffic_model and traffic_model in TRAFFIC_MODEL_MAP:
                body["routingPreference"] = "TRAFFIC_AWARE_OPTIMAL"
                body["trafficModel"] = TRAFFIC_MODEL_MAP[traffic_model]
            elif departure_time:
                body["routingPreference"] = "TRAFFIC_AWARE"

        return await self._post(body, TRAVEL_FIELD_MASK)

    async def validate_api_key(self) -> bool:
        """Make a minimal test request to verify the API key works."""
        body = {
            "origin": {"address": "Amsterdam, Netherlands"},
            "destination": {"address": "Rotterdam, Netherlands"},
            "travelMode": "DRIVE",
            "languageCode": "en",
            "units": "METRIC",
        }
        await self._post(body, "routes.duration,routes.distanceMeters")
        return True
