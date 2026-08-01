"""Shared pytest fixtures for the Google Transit Routes test suite."""

from unittest.mock import MagicMock

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.google_transit_routes.const import CONF_API_KEY, DOMAIN

pytest_plugins = "pytest_homeassistant_custom_component"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Make custom_components/ discoverable as a domain in every test."""
    yield


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """A basic, current-schema config entry with an API key and no saved routes."""
    return MockConfigEntry(
        domain=DOMAIN,
        data={CONF_API_KEY: "existing-key"},
        options={},
        minor_version=2,
    )


@pytest.fixture
def stub_frontend(hass):
    """Stand in for the (heavyweight, separately-packaged) frontend component.

    Full config-entry setup registers the Lovelace card via `hass.http` and
    `homeassistant.components.frontend.add_extra_js_url`, which normally
    requires the real `http`/`frontend` components — and those in turn need
    the `hass_frontend` static-assets package, which isn't (and shouldn't be)
    a test dependency. Stub just the two touch points the integration
    actually calls, matching what `pytest-homeassistant-custom-component`
    does for other integrations with a Lovelace card.
    """
    hass.http = MagicMock()
    hass.data.setdefault("frontend_extra_module_url", set())
    return hass.http
