from datetime import datetime, timedelta, timezone
from ingestion.models import WeatherObservation, AirQualityObservation

def transform_weather(city, data):
    timezone_offset = data["utc_offset_seconds"]
    observations = []

    # Process hourly data
    if "hourly" in data:
        hourly = data["hourly"]
        times = hourly["time"]
        for i, t in enumerate(times):
            observed_at = datetime.fromisoformat(t)
            observed_at = (observed_at - timedelta(seconds=timezone_offset)).replace(tzinfo=timezone.utc)

            # Skip if temperature is None
            if hourly.get("temperature_2m")[i] is None:
                continue

            obs = WeatherObservation(
                city=city["name"],
                country=city["country"],
                latitude=city["latitude"],
                longitude=city["longitude"],
                observed_at=observed_at,
                temperature_c=hourly.get("temperature_2m")[i],
                humidity_percent=hourly.get("relative_humidity_2m")[i],
                apparent_temperature_c=hourly.get("apparent_temperature")[i],
                precipitation_mm=hourly.get("precipitation")[i],
                weather_code=hourly.get("weather_code")[i],
                wind_speed_kmh=hourly.get("wind_speed_10m")[i],
                wind_direction_degrees=hourly.get("wind_direction_10m")[i],
            )
            observations.append(obs)

    # Process current data
    if "current" in data:
        current = data["current"]
        observed_at = datetime.fromisoformat(current["time"])
        observed_at = (observed_at - timedelta(seconds=timezone_offset)).replace(tzinfo=timezone.utc)
        obs = WeatherObservation(
            city=city["name"],
            country=city["country"],
            latitude=city["latitude"],
            longitude=city["longitude"],
            observed_at=observed_at,
            temperature_c=current.get("temperature_2m"),
            humidity_percent=current.get("relative_humidity_2m"),
            apparent_temperature_c=current.get("apparent_temperature"),
            precipitation_mm=current.get("precipitation"),
            weather_code=current.get("weather_code"),
            wind_speed_kmh=current.get("wind_speed_10m"),
            wind_direction_degrees=current.get("wind_direction_10m"),
        )
        observations.append(obs)

    return observations

def transform_air_quality(city, data):
    timezone_offset = data["utc_offset_seconds"]
    observations = []

    if "hourly" in data:
        hourly = data["hourly"]
        times = hourly["time"]
        for i, t in enumerate(times):
            observed_at = datetime.fromisoformat(t)
            observed_at = (observed_at - timedelta(seconds=timezone_offset)).replace(tzinfo=timezone.utc)

            if hourly.get("us_aqi")[i] is None:
                continue

            obs = AirQualityObservation(
                city=city["name"],
                country=city["country"],
                latitude=city["latitude"],
                longitude=city["longitude"],
                observed_at=observed_at,
                pm10=hourly.get("pm10")[i],
                pm2_5=hourly.get("pm2_5")[i],
                carbon_monoxide=hourly.get("carbon_monoxide")[i],
                nitrogen_dioxide=hourly.get("nitrogen_dioxide")[i],
                sulphur_dioxide=hourly.get("sulphur_dioxide")[i],
                ozone=hourly.get("ozone")[i],
                us_aqi=hourly.get("us_aqi")[i],
            )
            observations.append(obs)

    if "current" in data:
        current = data["current"]
        observed_at = datetime.fromisoformat(current["time"])
        observed_at = (observed_at - timedelta(seconds=timezone_offset)).replace(tzinfo=timezone.utc)
        obs = AirQualityObservation(
            city=city["name"],
            country=city["country"],
            latitude=city["latitude"],
            longitude=city["longitude"],
            observed_at=observed_at,
            pm10=current.get("pm10"),
            pm2_5=current.get("pm2_5"),
            carbon_monoxide=current.get("carbon_monoxide"),
            nitrogen_dioxide=current.get("nitrogen_dioxide"),
            sulphur_dioxide=current.get("sulphur_dioxide"),
            ozone=current.get("ozone"),
            us_aqi=current.get("us_aqi"),
        )
        observations.append(obs)

    return observations
