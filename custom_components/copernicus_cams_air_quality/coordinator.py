"""Coordinator for Copernicus CAMS Air Quality."""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import Any

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)

API_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"

VARIABLES = [
    "dust",
    "pm10",
    "pm2_5",
    "ozone",
    "nitrogen_dioxide",
    "sulphur_dioxide",
    "uv_index",
    "uv_index_clear_sky",
    "birch_pollen",
    "grass_pollen",
    "olive_pollen",
]


class CopernicusCAMSCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Fetch and process air quality data."""

    def __init__(
        self,
        hass: HomeAssistant,
        session: aiohttp.ClientSession,
        latitude: float,
        longitude: float,
        location_name: str,
    ) -> None:
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"Copernicus CAMS – {location_name}",
            update_interval=timedelta(hours=1),
        )
        self.session = session
        self.latitude = latitude
        self.longitude = longitude
        self.location_name = location_name

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from Open-Meteo."""
        params = {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "hourly": ",".join(VARIABLES),
            "timezone": self.hass.config.time_zone,
            "forecast_days": 4,
        }
        try:
            async with self.session.get(
                API_URL,
                params=params,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    raise UpdateFailed(f"HTTP {resp.status}")
                raw: dict[str, Any] = await resp.json()
        except asyncio.TimeoutError as err:
            raise UpdateFailed("Timeout") from err
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Network error: {err}") from err

        return self._process(raw)

    def _process(self, raw: dict[str, Any]) -> dict[str, Any]:
        """Structure API response."""
        hourly = raw.get("hourly", {})
        times: list[str] = hourly.get("time", [])
        if not times:
            raise UpdateFailed("Empty response from Open-Meteo")

        result: dict[str, Any] = {}

        for var in VARIABLES:
            values: list[Any] = hourly.get(var, [])
            if not values:
                continue
            valid = [v for v in values if v is not None]
            if not valid:
                continue

            max_val = max(valid)
            max_idx = next(i for i, v in enumerate(values) if v == max_val)

            result[var] = {
                "current": values[0],
                "max": max_val,
                "max_time": times[max_idx] if max_idx < len(times) else None,
                "forecast_24h": values[:24],
            }

        result["aqi_european"] = self._calc_aqi(result)
        return result

    def _calc_aqi(self, data: dict[str, Any]) -> dict[str, Any]:
        """European AQI (CITEAIR 1-6)."""

        def sub_pm25(v: float) -> int:
            if v <= 11: return 1
            if v <= 23: return 2
            if v <= 35: return 3
            if v <= 41: return 4
            if v <= 47: return 5
            return 6

        def sub_pm10(v: float) -> int:
            if v <= 20: return 1
            if v <= 35: return 2
            if v <= 50: return 3
            if v <= 75: return 4
            if v <= 100: return 5
            return 6

        def sub_no2(v: float) -> int:
            if v <= 40: return 1
            if v <= 90: return 2
            if v <= 120: return 3
            if v <= 230: return 4
            if v <= 320: return 5
            return 6

        def sub_o3(v: float) -> int:
            if v <= 60: return 1
            if v <= 100: return 2
            if v <= 130: return 3
            if v <= 240: return 4
            if v <= 380: return 5
            return 6

        def aqi(pm25: Any, pm10: Any, no2: Any, o3: Any) -> int | None:
            subs = []
            if pm25 is not None: subs.append(sub_pm25(pm25))
            if pm10 is not None: subs.append(sub_pm10(pm10))
            if no2  is not None: subs.append(sub_no2(no2))
            if o3   is not None: subs.append(sub_o3(o3))
            return max(subs) if subs else None

        current = aqi(
            data.get("pm2_5", {}).get("current"),
            data.get("pm10", {}).get("current"),
            data.get("nitrogen_dioxide", {}).get("current"),
            data.get("ozone", {}).get("current"),
        )

        pm25_fc = data.get("pm2_5", {}).get("forecast_24h", [])
        pm10_fc = data.get("pm10", {}).get("forecast_24h", [])
        no2_fc  = data.get("nitrogen_dioxide", {}).get("forecast_24h", [])
        o3_fc   = data.get("ozone", {}).get("forecast_24h", [])
        length = max(len(pm25_fc), len(pm10_fc), len(no2_fc), len(o3_fc), 0)

        return {
            "current": current,
            "forecast_24h": [
                aqi(
                    pm25_fc[i] if i < len(pm25_fc) else None,
                    pm10_fc[i] if i < len(pm10_fc) else None,
                    no2_fc[i]  if i < len(no2_fc)  else None,
                    o3_fc[i]   if i < len(o3_fc)   else None,
                )
                for i in range(length)
            ],
        }
