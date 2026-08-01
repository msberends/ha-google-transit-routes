"""Entity resolution and response parsing helpers."""

from __future__ import annotations

import re
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util

from .const import (
    ATTRIBUTION,
    ENTITY_DOMAIN_DEVICE_TRACKER,
    ENTITY_DOMAIN_PERSON,
    ENTITY_DOMAIN_SENSOR,
    ENTITY_DOMAIN_ZONE,
)

LATLNG_RE = re.compile(r"^\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*$")

_ENTITY_DOMAINS_WITH_COORDS = (
    ENTITY_DOMAIN_ZONE,
    ENTITY_DOMAIN_DEVICE_TRACKER,
    ENTITY_DOMAIN_PERSON,
)

_DURATION_UNITS = {
    "en": {"hour": "hr", "hours": "hr", "minute": "min", "minutes": "min"},
    "nl": {"hour": "uur", "hours": "uur", "minute": "min.", "minutes": "min."},
}


def _latlng(latitude: float, longitude: float) -> dict[str, Any]:
    """Build a Routes API location object from a latitude/longitude pair."""
    return {"location": {"latLng": {"latitude": latitude, "longitude": longitude}}}


def resolve_entity_location(hass: HomeAssistant, entity_id: str) -> dict[str, Any]:
    """Resolve a Home Assistant entity ID to a Routes API location object."""
    domain = entity_id.split(".", 1)[0]
    state = hass.states.get(entity_id)
    if state is None:
        raise ValueError(f"Entity {entity_id} not found")

    if domain in _ENTITY_DOMAINS_WITH_COORDS:
        latitude = state.attributes.get("latitude")
        longitude = state.attributes.get("longitude")
        if latitude is None or longitude is None:
            raise ValueError(f"Entity {entity_id} has no latitude/longitude")
        return _latlng(float(latitude), float(longitude))

    if domain == ENTITY_DOMAIN_SENSOR:
        latitude = state.attributes.get("latitude")
        longitude = state.attributes.get("longitude")
        if latitude is not None and longitude is not None:
            return _latlng(float(latitude), float(longitude))
        return {"address": state.state}

    raise ValueError(f"Unsupported entity domain for {entity_id}")


def resolve_location(hass: HomeAssistant, location_str: str) -> dict[str, Any]:
    """Resolve an origin/destination string to a Routes API location object.

    Accepts an HA entity ID, a "lat,lng" coordinate pair, or a free-form address.
    """
    location_str = location_str.strip()

    if "." in location_str and hass.states.get(location_str) is not None:
        return resolve_entity_location(hass, location_str)

    match = LATLNG_RE.match(location_str)
    if match:
        return _latlng(float(match.group(1)), float(match.group(2)))

    return {"address": location_str}


def _parse_duration_seconds(duration_str: str | None) -> int:
    """Parse a Routes API duration string like '4091s' into whole seconds."""
    if not duration_str:
        return 0
    return int(round(float(duration_str.rstrip("s"))))


def _format_duration_text(seconds: int, language: str) -> str:
    """Format a duration in seconds as a short localised text string."""
    units = _DURATION_UNITS.get(language, _DURATION_UNITS["en"])
    hours, minutes = divmod(seconds // 60, 60)
    parts = []
    if hours:
        parts.append(f"{hours} {units['hour']}")
    parts.append(f"{minutes} {units['minute']}")
    return " ".join(parts)


def compute_duration_from_now(
    arrival_time: str | None, language: str
) -> tuple[int | None, str | None]:
    """Compute seconds (and localised text) from now until an arrival timestamp."""
    if not arrival_time:
        return None, None
    arrival_dt = dt_util.parse_datetime(arrival_time)
    if arrival_dt is None:
        return None, None
    seconds = int((arrival_dt - dt_util.utcnow()).total_seconds())
    return seconds, _format_duration_text(seconds, language)


def _iter_transit_steps(route: dict[str, Any]) -> list[dict[str, Any]]:
    """Flatten all steps across all legs of a route into a single list."""
    steps: list[dict[str, Any]] = []
    for leg in route.get("legs", []):
        steps.extend(leg.get("steps", []))
    return _merge_consecutive_non_transit_steps(steps)


def _merge_consecutive_non_transit_steps(
    steps: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Collapse consecutive non-transit steps (e.g. turn-by-turn walking) into one.

    The Routes API returns walking directions as many small steps. The clean
    response structure only needs a single merged leg per walk/transfer, with
    the total duration.
    """
    merged: list[dict[str, Any]] = []
    for step in steps:
        travel_mode = step.get("travelMode", "WALK")
        if (
            travel_mode != "TRANSIT"
            and merged
            and merged[-1].get("travelMode") == travel_mode
        ):
            previous = merged[-1]
            total = _parse_duration_seconds(
                previous.get("staticDuration")
            ) + _parse_duration_seconds(step.get("staticDuration"))
            merged[-1] = {**previous, "staticDuration": f"{total}s"}
        else:
            merged.append(step)
    return merged


def _build_leg(step: dict[str, Any]) -> dict[str, Any]:
    """Build a single flattened leg dict from a route step."""
    travel_mode = step.get("travelMode", "WALK")

    if travel_mode != "TRANSIT" or "transitDetails" not in step:
        return {
            "mode": travel_mode,
            "duration": _parse_duration_seconds(step.get("staticDuration")),
        }

    details = step["transitDetails"]
    stop_details = details.get("stopDetails", {})
    localized = details.get("localizedValues", {})
    transit_line = details.get("transitLine", {})
    vehicle = transit_line.get("vehicle", {})
    agencies = transit_line.get("agencies", [])

    line_name = transit_line.get("nameShort") or transit_line.get("name")

    return {
        "mode": vehicle.get("type", "TRANSIT"),
        "line_name": line_name,
        "line_full_name": transit_line.get("name"),
        "headsign": details.get("headsign"),
        "departure_stop": stop_details.get("departureStop", {}).get("name"),
        "departure_time": stop_details.get("departureTime"),
        "departure_time_local": localized.get("departureTime", {})
        .get("time", {})
        .get("text"),
        "arrival_stop": stop_details.get("arrivalStop", {}).get("name"),
        "arrival_time": stop_details.get("arrivalTime"),
        "arrival_time_local": localized.get("arrivalTime", {})
        .get("time", {})
        .get("text"),
        "stop_count": details.get("stopCount"),
        "agency": agencies[0].get("name") if agencies else None,
        "line_color": transit_line.get("color"),
        "vehicle_type": vehicle.get("type"),
    }


def _parse_transit_route(route: dict[str, Any], language: str) -> dict[str, Any] | None:
    """Parse a single raw route object into the documented clean structure."""
    steps = _iter_transit_steps(route)
    legs = [_build_leg(step) for step in steps]
    transit_legs = [leg for leg in legs if "line_name" in leg]

    if not transit_legs:
        return None

    first_transit = transit_legs[0]
    last_transit = transit_legs[-1]

    localized = route.get("localizedValues", {})
    duration = _parse_duration_seconds(route.get("duration"))

    duration_from_now, duration_from_now_text = compute_duration_from_now(
        last_transit["arrival_time"], language
    )

    return {
        "arrival_time": last_transit["arrival_time"],
        "arrival_time_local": last_transit["arrival_time_local"],
        "arrival_timezone": _transit_timezone(steps, last=True),
        "departure_time": first_transit["departure_time"],
        "departure_time_local": first_transit["departure_time_local"],
        "departure_timezone": _transit_timezone(steps, last=False),
        "duration": duration,
        "duration_text": localized.get("duration", {}).get("text"),
        "duration_from_now": duration_from_now,
        "duration_from_now_text": duration_from_now_text,
        "distance_meters": route.get("distanceMeters"),
        "distance_text": localized.get("distance", {}).get("text"),
        "legs": legs,
        "attribution": ATTRIBUTION,
    }


def _transit_timezone(steps: list[dict[str, Any]], last: bool) -> str | None:
    """Extract the timezone of the first or last transit step's arrival/departure."""
    transit_steps = [s for s in steps if s.get("travelMode") == "TRANSIT"]
    if not transit_steps:
        return None
    step = transit_steps[-1] if last else transit_steps[0]
    localized = step.get("transitDetails", {}).get("localizedValues", {})
    key = "arrivalTime" if last else "departureTime"
    return localized.get(key, {}).get("timeZone")


def parse_transit_response(
    api_response: dict[str, Any], language: str = "en"
) -> list[dict[str, Any]]:
    """Transform a raw computeRoutes transit response into the clean structure."""
    routes = []
    for route in api_response.get("routes", []):
        parsed = _parse_transit_route(route, language)
        if parsed is not None:
            routes.append(parsed)

    routes.sort(key=lambda r: r["departure_time"] or "")
    return routes


def parse_travel_response(api_response: dict[str, Any]) -> list[dict[str, Any]]:
    """Transform a raw computeRoutes non-transit response into a simple structure."""
    routes = []
    for route in api_response.get("routes", []):
        localized = route.get("localizedValues", {})
        routes.append(
            {
                "duration": _parse_duration_seconds(route.get("duration")),
                "duration_text": localized.get("duration", {}).get("text"),
                "static_duration": _parse_duration_seconds(route.get("staticDuration")),
                "static_duration_text": localized.get("staticDuration", {}).get("text"),
                "distance_meters": route.get("distanceMeters"),
                "distance_text": localized.get("distance", {}).get("text"),
                "attribution": ATTRIBUTION,
            }
        )
    return routes
