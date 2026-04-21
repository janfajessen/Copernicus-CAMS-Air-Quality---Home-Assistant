"""Sensors for Copernicus CAMS Air Quality."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import DOMAIN
from .coordinator import CopernicusCAMSCoordinator

_LOGGER = logging.getLogger(__name__)

# Unidades como strings directos — evita problemas de importación entre versiones de HA
UNIT_UGM3 = "µg/m³"
UNIT_GRAINS = "grains/m³"


@dataclass(frozen=True)
class CamsDesc(SensorEntityDescription):
    """Extends SensorEntityDescription."""

    var_key: str = ""
    value_type: str = "current"  # current | max | max_time


SENSORS: tuple[CamsDesc, ...] = (
    # ── Dust ──────────────────────────────────────────────────────────────────
    CamsDesc(key="dust_current", var_key="dust", value_type="current",
             name="Dust", icon="mdi:weather-dust",
             native_unit_of_measurement=UNIT_UGM3,
             device_class=SensorDeviceClass.PM1,
             state_class=SensorStateClass.MEASUREMENT),
    CamsDesc(key="dust_max", var_key="dust", value_type="max",
             name="Dust Max", icon="mdi:weather-dust",
             native_unit_of_measurement=UNIT_UGM3,
             device_class=SensorDeviceClass.PM1,
             state_class=SensorStateClass.MEASUREMENT),
    CamsDesc(key="dust_max_time", var_key="dust", value_type="max_time",
             name="Dust Max Time", icon="mdi:clock-outline",
             entity_registry_enabled_default=False),
    # ── PM10 ──────────────────────────────────────────────────────────────────
    CamsDesc(key="pm10_current", var_key="pm10", value_type="current",
             name="PM10", icon="mdi:molecule",
             native_unit_of_measurement=UNIT_UGM3,
             device_class=SensorDeviceClass.PM10,
             state_class=SensorStateClass.MEASUREMENT),
    CamsDesc(key="pm10_max", var_key="pm10", value_type="max",
             name="PM10 Max", icon="mdi:molecule",
             native_unit_of_measurement=UNIT_UGM3,
             device_class=SensorDeviceClass.PM10,
             state_class=SensorStateClass.MEASUREMENT),
    CamsDesc(key="pm10_max_time", var_key="pm10", value_type="max_time",
             name="PM10 Max Time", icon="mdi:clock-outline",
             entity_registry_enabled_default=False),
    # ── PM2.5 ─────────────────────────────────────────────────────────────────
    CamsDesc(key="pm2_5_current", var_key="pm2_5", value_type="current",
             name="PM2.5", icon="mdi:molecule",
             native_unit_of_measurement=UNIT_UGM3,
             device_class=SensorDeviceClass.PM25,
             state_class=SensorStateClass.MEASUREMENT),
    CamsDesc(key="pm2_5_max", var_key="pm2_5", value_type="max",
             name="PM2.5 Max", icon="mdi:molecule",
             native_unit_of_measurement=UNIT_UGM3,
             device_class=SensorDeviceClass.PM25,
             state_class=SensorStateClass.MEASUREMENT),
    CamsDesc(key="pm2_5_max_time", var_key="pm2_5", value_type="max_time",
             name="PM2.5 Max Time", icon="mdi:clock-outline",
             entity_registry_enabled_default=False),
    # ── Ozone ─────────────────────────────────────────────────────────────────
    CamsDesc(key="ozone_current", var_key="ozone", value_type="current",
             name="Ozone", icon="mdi:atom",
             native_unit_of_measurement=UNIT_UGM3,
             state_class=SensorStateClass.MEASUREMENT),
    CamsDesc(key="ozone_max", var_key="ozone", value_type="max",
             name="Ozone Max", icon="mdi:atom",
             native_unit_of_measurement=UNIT_UGM3,
             state_class=SensorStateClass.MEASUREMENT),
    CamsDesc(key="ozone_max_time", var_key="ozone", value_type="max_time",
             name="Ozone Max Time", icon="mdi:clock-outline",
             entity_registry_enabled_default=False),
    # ── NO2 ───────────────────────────────────────────────────────────────────
    CamsDesc(key="no2_current", var_key="nitrogen_dioxide", value_type="current",
             name="Nitrogen Dioxide", icon="mdi:molecule",
             native_unit_of_measurement=UNIT_UGM3,
             state_class=SensorStateClass.MEASUREMENT),
    CamsDesc(key="no2_max", var_key="nitrogen_dioxide", value_type="max",
             name="Nitrogen Dioxide Max", icon="mdi:molecule",
             native_unit_of_measurement=UNIT_UGM3,
             state_class=SensorStateClass.MEASUREMENT),
    CamsDesc(key="no2_max_time", var_key="nitrogen_dioxide", value_type="max_time",
             name="Nitrogen Dioxide Max Time", icon="mdi:clock-outline",
             entity_registry_enabled_default=False),
    # ── SO2 ───────────────────────────────────────────────────────────────────
    CamsDesc(key="so2_current", var_key="sulphur_dioxide", value_type="current",
             name="Sulphur Dioxide", icon="mdi:molecule",
             native_unit_of_measurement=UNIT_UGM3,
             state_class=SensorStateClass.MEASUREMENT),
    CamsDesc(key="so2_max", var_key="sulphur_dioxide", value_type="max",
             name="Sulphur Dioxide Max", icon="mdi:molecule",
             native_unit_of_measurement=UNIT_UGM3,
             state_class=SensorStateClass.MEASUREMENT),
    CamsDesc(key="so2_max_time", var_key="sulphur_dioxide", value_type="max_time",
             name="Sulphur Dioxide Max Time", icon="mdi:clock-outline",
             entity_registry_enabled_default=False),
    # ── UV Index ──────────────────────────────────────────────────────────────
    CamsDesc(key="uv_index_current", var_key="uv_index", value_type="current",
             name="UV Index", icon="mdi:sun-angle-outline",
             state_class=SensorStateClass.MEASUREMENT),
    CamsDesc(key="uv_index_max", var_key="uv_index", value_type="max",
             name="UV Index Max", icon="mdi:sun-angle-outline",
             state_class=SensorStateClass.MEASUREMENT),
    CamsDesc(key="uv_index_max_time", var_key="uv_index", value_type="max_time",
             name="UV Index Max Time", icon="mdi:clock-outline",
             entity_registry_enabled_default=False),
    # ── UV Clear Sky ──────────────────────────────────────────────────────────
    CamsDesc(key="uv_cs_current", var_key="uv_index_clear_sky", value_type="current",
             name="UV Index Clear Sky", icon="mdi:sun-angle-outline",
             state_class=SensorStateClass.MEASUREMENT,
             entity_registry_enabled_default=False),
    CamsDesc(key="uv_cs_max", var_key="uv_index_clear_sky", value_type="max",
             name="UV Index Clear Sky Max", icon="mdi:sun-angle-outline",
             state_class=SensorStateClass.MEASUREMENT,
             entity_registry_enabled_default=False),
    CamsDesc(key="uv_cs_max_time", var_key="uv_index_clear_sky", value_type="max_time",
             name="UV Index Clear Sky Max Time", icon="mdi:clock-outline",
             entity_registry_enabled_default=False),
    # ── Birch Pollen ──────────────────────────────────────────────────────────
    CamsDesc(key="birch_current", var_key="birch_pollen", value_type="current",
             name="Birch Pollen", icon="mdi:flower-pollen",
             native_unit_of_measurement=UNIT_GRAINS,
             state_class=SensorStateClass.MEASUREMENT),
    CamsDesc(key="birch_max", var_key="birch_pollen", value_type="max",
             name="Birch Pollen Max", icon="mdi:flower-pollen",
             native_unit_of_measurement=UNIT_GRAINS,
             state_class=SensorStateClass.MEASUREMENT),
    CamsDesc(key="birch_max_time", var_key="birch_pollen", value_type="max_time",
             name="Birch Pollen Max Time", icon="mdi:clock-outline",
             entity_registry_enabled_default=False),
    # ── Grass Pollen ──────────────────────────────────────────────────────────
    CamsDesc(key="grass_current", var_key="grass_pollen", value_type="current",
             name="Grass Pollen", icon="mdi:flower-pollen",
             native_unit_of_measurement=UNIT_GRAINS,
             state_class=SensorStateClass.MEASUREMENT),
    CamsDesc(key="grass_max", var_key="grass_pollen", value_type="max",
             name="Grass Pollen Max", icon="mdi:flower-pollen",
             native_unit_of_measurement=UNIT_GRAINS,
             state_class=SensorStateClass.MEASUREMENT),
    CamsDesc(key="grass_max_time", var_key="grass_pollen", value_type="max_time",
             name="Grass Pollen Max Time", icon="mdi:clock-outline",
             entity_registry_enabled_default=False),
    # ── Olive Pollen ──────────────────────────────────────────────────────────
    CamsDesc(key="olive_current", var_key="olive_pollen", value_type="current",
             name="Olive Pollen", icon="mdi:flower-pollen",
             native_unit_of_measurement=UNIT_GRAINS,
             state_class=SensorStateClass.MEASUREMENT),
    CamsDesc(key="olive_max", var_key="olive_pollen", value_type="max",
             name="Olive Pollen Max", icon="mdi:flower-pollen",
             native_unit_of_measurement=UNIT_GRAINS,
             state_class=SensorStateClass.MEASUREMENT),
    CamsDesc(key="olive_max_time", var_key="olive_pollen", value_type="max_time",
             name="Olive Pollen Max Time", icon="mdi:clock-outline",
             entity_registry_enabled_default=False),
    # ── European AQI ──────────────────────────────────────────────────────────
    CamsDesc(key="aqi_european", var_key="aqi_european", value_type="current",
             name="European AQI", icon="mdi:air-filter",
             state_class=SensorStateClass.MEASUREMENT),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors from config entry."""
    coordinator: CopernicusCAMSCoordinator = entry.runtime_data
    location_name: str = entry.data[CONF_NAME]

    device = DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name=f"{location_name} – Copernicus CAMS",
        manufacturer="ECMWF / Open-Meteo",
        model="Copernicus CAMS Air Quality",
        configuration_url="https://open-meteo.com/en/docs/air-quality-api",
    )

    async_add_entities(
        CamsEntity(coordinator, desc, device, entry.entry_id)
        for desc in SENSORS
    )


class CamsEntity(CoordinatorEntity[CopernicusCAMSCoordinator], SensorEntity):
    """A single sensor entity."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: CopernicusCAMSCoordinator,
        desc: CamsDesc,
        device: DeviceInfo,
        entry_id: str,
    ) -> None:
        """Init."""
        super().__init__(coordinator)
        self.entity_description = desc
        self._desc = desc
        self._attr_device_info = device
        self._attr_unique_id = f"{entry_id}_{desc.key}"
        if desc.entity_registry_enabled_default is not None:
            self._attr_entity_registry_enabled_default = (
                desc.entity_registry_enabled_default
            )

    @property
    def native_value(self) -> Any:
        """Return current sensor value."""
        if not self.coordinator.data:
            return None
        var_data: dict[str, Any] | None = self.coordinator.data.get(self._desc.var_key)
        if var_data is None:
            return None
        return var_data.get(self._desc.value_type)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Add forecast_24h to current-value sensors."""
        if self._desc.value_type != "current" or not self.coordinator.data:
            return {}
        var_data = self.coordinator.data.get(self._desc.var_key, {})
        fc = var_data.get("forecast_24h")
        return {"forecast_24h": fc} if fc else {}
