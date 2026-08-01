"""Tests for the per-route sensor entity and its device grouping."""

import json
from pathlib import Path

from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.google_transit_routes.api import API_URL
from custom_components.google_transit_routes.const import (
    CONF_API_KEY,
    CONF_DESTINATION,
    CONF_LANGUAGE,
    CONF_ORIGIN,
    DOMAIN,
    SUBENTRY_TYPE_ROUTE,
)

FIXTURES = Path(__file__).parent / "fixtures"
TRANSIT_RESPONSE = json.loads((FIXTURES / "transit_response.json").read_text(encoding="utf-8"))

ROUTE_SUBENTRY = {
    "subentry_type": SUBENTRY_TYPE_ROUTE,
    "title": "UMCG Noord - Veenwouden",
    "unique_id": None,
    "data": {
        CONF_ORIGIN: "zone.umcg_noord",
        CONF_DESTINATION: "zone.station_veenwouden",
        CONF_LANGUAGE: "nl",
    },
}


async def test_route_subentry_gets_its_own_device_and_entity(
    hass, aioclient_mock, stub_frontend
):
    """Each saved-route subentry produces exactly one sensor on its own device."""
    aioclient_mock.post(API_URL, json=TRANSIT_RESPONSE)

    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_API_KEY: "existing-key"},
        options={},
        minor_version=2,
        subentries_data=[ROUTE_SUBENTRY],
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    (subentry,) = entry.subentries.values()

    entity_registry = er.async_get(hass)
    entity_entry = entity_registry.async_get_entity_id(
        "sensor", DOMAIN, subentry.subentry_id
    )
    assert entity_entry == "sensor.umcg_noord_veenwouden"

    registry_entry = entity_registry.async_get(entity_entry)
    assert registry_entry.config_subentry_id == subentry.subentry_id
    assert registry_entry.device_id is not None

    device_registry = dr.async_get(hass)
    device = device_registry.async_get(registry_entry.device_id)
    assert device.name == "UMCG Noord - Veenwouden"
    assert device.config_entries_subentries[entry.entry_id] == {subentry.subentry_id}

    state = hass.states.get(entity_entry)
    assert state is not None
    assert state.attributes["origin"] == "zone.umcg_noord"
    assert state.attributes["destination"] == "zone.station_veenwouden"


async def test_removing_route_subentry_removes_its_device(
    hass, aioclient_mock, stub_frontend
):
    """Deleting a saved route removes its sensor and device (no orphans)."""
    aioclient_mock.post(API_URL, json={"routes": []})

    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_API_KEY: "existing-key"},
        options={},
        minor_version=2,
        subentries_data=[ROUTE_SUBENTRY],
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    (subentry_id,) = entry.subentries.keys()
    assert hass.config_entries.async_remove_subentry(entry, subentry_id)
    await hass.async_block_till_done()

    entity_registry = er.async_get(hass)
    assert (
        entity_registry.async_get_entity_id("sensor", DOMAIN, subentry_id) is None
    )
