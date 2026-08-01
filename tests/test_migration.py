"""Tests for migrating legacy options-based saved routes into subentries."""

from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.google_transit_routes.api import API_URL
from custom_components.google_transit_routes.const import (
    CONF_API_KEY,
    CONF_DESTINATION,
    CONF_LANGUAGE,
    CONF_ORIGIN,
    CONF_ROUTE_NAME,
    CONF_ROUTES,
    DOMAIN,
    SUBENTRY_TYPE_ROUTE,
)


async def test_legacy_routes_become_subentries(hass, aioclient_mock, stub_frontend):
    """A pre-0.2.0 entry with options-based routes migrates them to subentries."""
    aioclient_mock.post(API_URL, json={"routes": []})

    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_API_KEY: "existing-key"},
        options={
            CONF_ROUTES: [
                {
                    CONF_ROUTE_NAME: "UMCG Noord - Veenwouden",
                    CONF_ORIGIN: "zone.umcg_noord",
                    CONF_DESTINATION: "zone.station_veenwouden",
                    CONF_LANGUAGE: "nl",
                }
            ]
        },
        version=1,
        minor_version=1,
    )
    entry.add_to_hass(hass)

    registry = er.async_get(hass)
    legacy_entity = registry.async_get_or_create(
        "sensor",
        DOMAIN,
        f"{DOMAIN}_umcg_noord_veenwouden",
        config_entry=entry,
        suggested_object_id="google_transit_umcg_noord_veenwouden",
    )

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert entry.minor_version == 2
    assert entry.options == {}
    (subentry,) = entry.subentries.values()
    assert subentry.subentry_type == SUBENTRY_TYPE_ROUTE
    assert subentry.title == "UMCG Noord - Veenwouden"
    assert subentry.data == {
        CONF_ORIGIN: "zone.umcg_noord",
        CONF_DESTINATION: "zone.station_veenwouden",
        CONF_LANGUAGE: "nl",
    }

    migrated_entry = registry.async_get(legacy_entity.entity_id)
    assert migrated_entry.unique_id == subentry.subentry_id
    assert migrated_entry.config_subentry_id == subentry.subentry_id
    # The entity_id itself must not have changed, so dashboards/automations
    # that reference it keep working after the upgrade.
    assert legacy_entity.entity_id == "sensor.google_transit_umcg_noord_veenwouden"
