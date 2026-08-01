"""Tests for entity resolution and response parsing (helpers.py)."""

import json
from datetime import timedelta
from pathlib import Path

import pytest
from homeassistant.util import dt as dt_util

from custom_components.google_transit_routes.helpers import (
    compute_duration_from_now,
    parse_transit_response,
    parse_travel_response,
    resolve_entity_location,
    resolve_location,
)

FIXTURES = Path(__file__).parent / "fixtures"


def _load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


# --- resolve_location / resolve_entity_location ---------------------------


def test_resolve_location_address(hass):
    """A plain address string is passed through as an 'address' location."""
    assert resolve_location(hass, "UMCG Noord, Groningen") == {
        "address": "UMCG Noord, Groningen"
    }


def test_resolve_location_latlng(hass):
    """A 'lat,lng' string is parsed into a latLng location."""
    result = resolve_location(hass, "53.22, 6.57")
    assert result == {"location": {"latLng": {"latitude": 53.22, "longitude": 6.57}}}


def test_resolve_location_zone_entity(hass):
    """A zone.* entity resolves to its latitude/longitude attributes."""
    hass.states.async_set(
        "zone.umcg_noord", "zoning", {"latitude": 53.223, "longitude": 6.569}
    )
    result = resolve_location(hass, "zone.umcg_noord")
    assert result == {
        "location": {"latLng": {"latitude": 53.223, "longitude": 6.569}}
    }


def test_resolve_location_person_entity(hass):
    """A person.* entity resolves to its latitude/longitude attributes."""
    hass.states.async_set(
        "person.bob", "home", {"latitude": 53.1, "longitude": 6.5}
    )
    result = resolve_location(hass, "person.bob")
    assert result == {"location": {"latLng": {"latitude": 53.1, "longitude": 6.5}}}


def test_resolve_location_device_tracker_entity(hass):
    """A device_tracker.* entity resolves to its latitude/longitude attributes."""
    hass.states.async_set(
        "device_tracker.phone", "home", {"latitude": 53.2, "longitude": 6.6}
    )
    result = resolve_location(hass, "device_tracker.phone")
    assert result == {"location": {"latLng": {"latitude": 53.2, "longitude": 6.6}}}


def test_resolve_location_sensor_entity_with_coords(hass):
    """A sensor.* entity with lat/lng attributes resolves to a latLng location."""
    hass.states.async_set(
        "sensor.custom_gps", "somewhere", {"latitude": 53.3, "longitude": 6.7}
    )
    result = resolve_location(hass, "sensor.custom_gps")
    assert result == {"location": {"latLng": {"latitude": 53.3, "longitude": 6.7}}}


def test_resolve_location_sensor_entity_as_address(hass):
    """A sensor.* entity without lat/lng falls back to its state as an address."""
    hass.states.async_set("sensor.destination_address", "Station Meadowfield")
    result = resolve_location(hass, "sensor.destination_address")
    assert result == {"address": "Station Meadowfield"}


def test_resolve_entity_location_missing_entity_raises(hass):
    """Referencing a nonexistent entity raises ValueError."""
    with pytest.raises(ValueError):
        resolve_entity_location(hass, "zone.does_not_exist")


def test_resolve_entity_location_unsupported_domain_raises(hass):
    """Referencing an unsupported entity domain raises ValueError."""
    hass.states.async_set("light.kitchen", "on")
    with pytest.raises(ValueError):
        resolve_entity_location(hass, "light.kitchen")


# --- parse_transit_response -------------------------------------------------


def test_parse_transit_response_route_count_and_sort_order():
    """All routes are parsed and returned sorted by departure time."""
    routes = parse_transit_response(_load_fixture("transit_response.json"), "nl")

    assert len(routes) == 2
    assert routes[0]["departure_time"] < routes[1]["departure_time"]


def test_parse_transit_response_merges_walk_legs():
    """Consecutive WALK steps collapse into a single leg with the summed duration."""
    routes = parse_transit_response(_load_fixture("transit_response.json"), "nl")
    first_route_legs = routes[0]["legs"]

    walk_legs = [leg for leg in first_route_legs if leg["mode"] == "WALK"]
    transit_legs = [leg for leg in first_route_legs if leg["mode"] != "WALK"]

    # 5 leading WALK steps (48+204+155+130+31=568s) and 2 trailing (71+19=90s)
    # must collapse into exactly one leading and one trailing WALK leg.
    assert len(walk_legs) == 2
    assert walk_legs[0]["duration"] == 568
    assert walk_legs[1]["duration"] == 90
    assert len(transit_legs) == 1


def test_parse_transit_response_transit_leg_fields():
    """Transit leg fields are pulled from the correct nested API paths."""
    routes = parse_transit_response(_load_fixture("transit_response.json"), "nl")
    transit_leg = next(
        leg for leg in routes[0]["legs"] if leg["mode"] != "WALK"
    )

    assert transit_leg["line_name"] == "Stoptrein RS1"
    assert transit_leg["line_full_name"] == "Groningen <-> Leeuwarden ST37400"
    assert transit_leg["headsign"] == "Leeuwarden"
    assert transit_leg["departure_stop"] == "Groningen"
    assert transit_leg["arrival_stop"] == "Meadowfield"
    assert transit_leg["stop_count"] == 6
    assert transit_leg["agency"] == "Arriva"
    assert transit_leg["vehicle_type"] == "HEAVY_RAIL"
    # Not in the raw API response for TRANSIT steps (no staticDuration) —
    # must be derived from the scheduled departure/arrival stop times so the
    # journey bar can weight transit legs correctly against walk legs.
    assert transit_leg["duration"] == 1800


def test_parse_transit_response_top_level_fields():
    """Top-level arrival/departure are the true door-to-door times, including
    the walk before boarding and after alighting — not just the vehicle's own
    schedule. The fixture's last leg is a 90s trailing walk, so arrival is
    90s after the train itself arrives (04:54:00Z); departure is derived by
    subtracting the route's total duration (4008s) from that true arrival,
    which absorbs the ~26 minutes of walking-to-the-stop-and-waiting before
    the train departs at 04:24:00Z.
    """
    routes = parse_transit_response(_load_fixture("transit_response.json"), "nl")
    route = routes[0]

    assert route["arrival_time"] == "2026-08-01T04:55:30Z"
    assert route["arrival_time_local"] == "06:55"
    assert route["arrival_timezone"] == "Europe/Amsterdam"
    assert route["departure_time"] == "2026-08-01T03:48:42Z"
    assert route["departure_time_local"] == "05:48"
    assert route["duration"] == 4008
    assert route["duration_text"] == "1 uur 7 min."
    assert route["distance_meters"] == 42673
    assert route["distance_text"] == "42,7 km"
    assert route["attribution"] == "Powered by Google"


def test_parse_transit_response_second_route_has_two_transit_legs():
    """A route with a bus + train combination keeps both transit legs distinct."""
    routes = parse_transit_response(_load_fixture("transit_response.json"), "nl")
    second_route_legs = routes[1]["legs"]
    transit_legs = [leg for leg in second_route_legs if leg["mode"] != "WALK"]

    assert len(transit_legs) == 2
    assert transit_legs[0]["mode"] == "BUS"
    assert transit_legs[0]["line_name"] == "4"
    assert transit_legs[0]["line_color"] == "#00bcf2"
    assert transit_legs[1]["mode"] == "HEAVY_RAIL"


def test_parse_transit_response_walk_legs_are_anchored_with_no_gaps():
    """WALK legs get absolute times chained to their neighbouring transit legs,
    so consecutive legs always meet exactly with no unexplained gap — any
    waiting time (e.g. arriving at a stop before the vehicle departs, or a
    slow transfer) is absorbed into the adjoining walk leg's span rather than
    disappearing between two legs.
    """
    routes = parse_transit_response(_load_fixture("transit_response.json"), "nl")
    legs = routes[1]["legs"]

    assert [leg["mode"] for leg in legs] == ["WALK", "BUS", "WALK", "HEAVY_RAIL", "WALK"]

    # Every leg's arrival lines up exactly with the next leg's departure.
    for current, following in zip(legs, legs[1:]):
        assert current["arrival_time"] == following["departure_time"]

    # The leading walk (route's true departure) absorbs the wait before
    # boarding the bus: real walking time is 265s, but the bus doesn't leave
    # until 184s later.
    leading_walk = legs[0]
    assert leading_walk["departure_time"] == routes[1]["departure_time"]
    assert leading_walk["arrival_time"] == legs[1]["departure_time"] == "2026-08-01T05:03:00Z"

    # The transfer walk absorbs the wait between the bus arriving and the
    # train departing: real walking time is 213s, but the gap is 900s.
    transfer_walk = legs[2]
    assert transfer_walk["departure_time"] == legs[1]["arrival_time"] == "2026-08-01T05:09:00Z"
    assert transfer_walk["arrival_time"] == legs[3]["departure_time"] == "2026-08-01T05:24:00Z"

    # The trailing walk (route's true arrival) matches its own real duration
    # exactly, since nothing follows it to introduce a gap.
    trailing_walk = legs[4]
    assert trailing_walk["departure_time"] == legs[3]["arrival_time"] == "2026-08-01T05:54:00Z"
    assert trailing_walk["arrival_time"] == routes[1]["arrival_time"] == "2026-08-01T05:55:30Z"


def test_parse_transit_response_empty_routes_returns_empty_list():
    """An API response with no routes parses to an empty list, not an error."""
    assert parse_transit_response({"routes": []}) == []


# --- parse_travel_response ---------------------------------------------------


def test_parse_travel_response():
    """Non-transit responses parse into the simple duration/distance structure."""
    routes = parse_travel_response(_load_fixture("travel_response.json"))

    assert len(routes) == 1
    assert routes[0]["duration"] == 3695
    assert routes[0]["duration_text"] == "1 uur 2 min."
    assert routes[0]["distance_meters"] == 78005
    assert routes[0]["distance_text"] == "78,0 km"
    assert routes[0]["attribution"] == "Powered by Google"


# --- compute_duration_from_now ------------------------------------------------


def test_compute_duration_from_now_future_time():
    """A future arrival time yields a positive seconds count and localised text."""
    future = dt_util.utcnow() + timedelta(minutes=42)
    seconds, text = compute_duration_from_now(future.isoformat(), "nl")

    assert 2510 <= seconds <= 2530
    assert "min" in text


def test_compute_duration_from_now_missing_time_returns_none():
    """A missing arrival time returns (None, None) rather than raising."""
    assert compute_duration_from_now(None, "en") == (None, None)
