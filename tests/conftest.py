"""Shared pytest fixtures for the Google Transit Routes test suite."""

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.google_transit_routes.const import CONF_API_KEY, CONF_ROUTES, DOMAIN

pytest_plugins = "pytest_homeassistant_custom_component"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Make custom_components/ discoverable as a domain in every test."""
    yield


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """A basic config entry with an API key and no saved routes."""
    return MockConfigEntry(
        domain=DOMAIN,
        data={CONF_API_KEY: "existing-key"},
        options={CONF_ROUTES: []},
    )
