"""Config flow for Copernicus CAMS Air Quality."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE, CONF_NAME
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.selector import (
    LocationSelector,
    LocationSelectorConfig,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)


class CopernicusCAMSConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the user step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            name: str = user_input.get(CONF_NAME, "").strip()
            # LocationSelector devuelve dict {"latitude": x, "longitude": y}
            loc: dict[str, Any] = user_input.get("location", {})
            lat: float = float(loc.get("latitude", 0))
            lon: float = float(loc.get("longitude", 0))

            if not name:
                errors[CONF_NAME] = "location_name_required"

            if not errors:
                await self.async_set_unique_id(f"{lat:.3f}_{lon:.3f}")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=name,
                    data={
                        CONF_NAME: name,
                        CONF_LATITUDE: lat,
                        CONF_LONGITUDE: lon,
                    },
                )

        default_lat = self.hass.config.latitude
        default_lon = self.hass.config.longitude

        schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default="Home"): TextSelector(
                    TextSelectorConfig(type=TextSelectorType.TEXT)
                ),
                vol.Required(
                    "location",
                    default={"latitude": default_lat, "longitude": default_lon},
                ): LocationSelector(LocationSelectorConfig(radius=False)),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )
