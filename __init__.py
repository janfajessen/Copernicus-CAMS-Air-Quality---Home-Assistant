"""Copernicus CAMS Air Quality integration."""
from __future__ import annotations

import logging
from typing import Final

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE, CONF_NAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .coordinator import CopernicusCAMSCoordinator

_LOGGER = logging.getLogger(__name__)

DOMAIN: Final = "copernicus_cams_air_quality"
PLATFORMS: Final[list[Platform]] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up from a config entry."""
    coordinator = CopernicusCAMSCoordinator(
        hass=hass,
        session=async_get_clientsession(hass),
        latitude=entry.data[CONF_LATITUDE],
        longitude=entry.data[CONF_LONGITUDE],
        location_name=entry.data[CONF_NAME],
    )
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
