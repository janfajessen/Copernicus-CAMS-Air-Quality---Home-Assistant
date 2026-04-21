# Copernicus CAMS Air Quality Integration for Home Assistant

A comprehensive Home Assistant integration that provides real-time and forecasted air quality data from the Copernicus CAMS (Copernicus Atmosphere Monitoring Service) via the free Open-Meteo Air Quality API.

## Features

- **Real-time Air Quality Data**: Current hourly measurements for multiple pollutants and indicators
- **4-Day Forecast**: 24-hour forecast data for each measured parameter
- **Daily Max Tracking**: Automatic detection and logging of daily maximum values and their timestamps
- **European AQI Index**: Calculated CITEAIR-based Air Quality Index combining PM2.5, PM10, NO2, and Ozone
- **Multiple Locations**: Configure and monitor multiple geographic locations simultaneously
- **No API Key Required**: Uses the free Open-Meteo Air Quality API with no authentication needed
- **Global Coverage**: Works anywhere in the world with OpenWeatherMap-compatible coordinates
- **Multi-language Support**: Translations in English and Spanish

## Measured Parameters

The integration tracks the following hourly variables:

### Particulates
- **PM10**: Coarse particulate matter (µg/m³)
- **PM2.5**: Fine particulate matter (µg/m³)
- **Dust**: Saharan dust surface concentration (µg/m³)

### Gases
- **Ozone (O₃)**: Tropospheric ozone (µg/m³)
- **Nitrogen Dioxide (NO₂)**: (µg/m³)
- **Sulphur Dioxide (SO₂)**: (µg/m³)

### UV Radiation
- **UV Index**: Current UV index
- **UV Index Clear Sky**: Clear-sky UV index reference

### Pollen (Europe only)
- **Birch Pollen**: (grains/m³)
- **Grass Pollen**: (grains/m³)
- **Olive Pollen**: (grains/m³)

### Composite Index
- **European AQI**: Calculated index (1-6 scale, based on CITEAIR methodology)

## Sensors Created

For each measured parameter, the integration creates three sensor entities:

1. **Current Value**: Hourly measurement at the time of update
2. **Daily Maximum**: Highest value recorded in the current day
3. **Maximum Time**: Timestamp when the daily maximum was recorded

Additionally:
- Each "current value" sensor includes a `forecast_24h` attribute with upcoming 24-hour values
- The European AQI sensor includes both current and 24-hour forecast values

## Installation

### Via HACS (Recommended)

1. Open HACS in Home Assistant
2. Go to Integrations → Custom Repositories
3. Add: `https://github.com/janfajessen/copernicus_cams_air_quality`
4. Category: Integration
5. Click "Install"
6. Restart Home Assistant

### Manual Installation

1. Copy the `copernicus_cams_air_quality` folder to `config/custom_components/`
2. Restart Home Assistant
3. Go to Settings → Devices & Services → Integrations
4. Search for "Copernicus CAMS" and click to set up

## Configuration

### Setup via UI

1. Go to Settings → Devices & Services → Integrations
2. Click "+ Create Integration"
3. Search for "Copernicus CAMS Air Quality"
4. Enter the following:
   - **Latitude**: Geographic latitude (-90 to 90)
   - **Longitude**: Geographic longitude (-180 to 180)
   - **Location Name**: Custom name for this location (e.g., "Home", "Office")

The integration will automatically suggest your Home Assistant default location coordinates.

### Multiple Locations

You can add multiple entries with different coordinates to monitor different areas. Each location will have its own set of sensors.

## Data Update Interval

Data is fetched from the API every **1 hour** by default. The API provides forecasts up to 4 days in advance, with hourly granularity.

## Device Organization

All sensors for a single location are grouped under a single device in Home Assistant named:
```
[Location Name] - Copernicus CAMS
```

## API Information

- **Data Source**: Open-Meteo Air Quality API (https://open-meteo.com/en/docs/air-quality-api)
- **Underlying Data**: Copernicus CAMS (ECMWF)
- **Licensing**: Data is freely available under Creative Commons Attribution 4.0 International License
- **Requirements**: Internet connection; no API key needed

## Sensor Naming

Sensors are automatically named following Home Assistant conventions:

```
sensor.[location_name]_[parameter]_current      # Current value
sensor.[location_name]_[parameter]_max          # Daily maximum
sensor.[location_name]_[parameter]_max_time     # Timestamp of maximum
sensor.[location_name]_aqi_european_current     # European AQI
```

## Home Assistant Requirements

- Home Assistant 2026.1.0 or later
- Python 3.11+

## Automations Example

Use these sensors to create automations and notifications:

```yaml
automation:
  - alias: "High PM2.5 Alert"
    trigger:
      platform: numeric_state
      entity_id: sensor.home_pm2_5_current
      above: 35
    action:
      - service: notify.telegram_jan
        data:
          message: "PM2.5 levels are high: {{ states('sensor.home_pm2_5_current') }} µg/m³"
```

## Troubleshooting

### No sensors appear after setup

1. Check the integration is listed in Settings → Devices & Services
2. Review the logs in Settings → System → Logs for error messages
3. Verify coordinates are correct (±180 longitude, ±90 latitude)
4. Ensure internet connectivity is available

### Data is stale or not updating

1. Check the coordinator's last update timestamp in the device details
2. Verify the Update Coordinator is running (restart HA if needed)
3. Check system logs for API connectivity issues

### Specific pollutants show "unavailable"

Some parameters (especially pollen) may not be available for all geographic locations. This is expected—the API returns `null` for regions where data is not available.

## License

MIT License - see LICENSE file in repository

## Support

For issues, feature requests, or contributions, visit:
https://github.com/janfajessen/copernicus_cams_air_quality

## Disclaimer

This integration is provided as-is. Air quality data from Copernicus CAMS is for informational purposes. Always consult official health authorities for air quality guidance and health recommendations.
