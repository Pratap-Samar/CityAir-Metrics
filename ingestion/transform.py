from ingestion.models import WeatherObservation, AirQualityObservation

def transform_weather(city, data):
    current = data["current"]

    Observation = WeatherObservation(
        city=city["name"],
        country=city["country"],
        latitude=city["latitude"],
        longitude=city["longitude"],
        observed_at=current["time"],
        temperature_c=current.get("temperature_2m"),
        humidity_percent=current.get("relative_humidity_2m"),
        apparent_temperature_c=current.get("apparent_temperature"),
        precipitation_mm=current.get("precipitation"),
        weather_code=current.get("weather_code"),
        wind_speed_kmh=current.get("wind_speed_10m"),
        wind_direction_degrees=current.get("wind_direction_10m"),
    )
    return Observation

def transform_air_quality(city, data):
    current = data["current"]
    observation = AirQualityObservation(
        city=city["name"],
        country=city["country"],
        latitude=city["latitude"],
        longitude=city["longitude"],
        observed_at=current["time"],
        pm10=current.get("pm10"),
        pm2_5=current.get("pm2_5"),
        carbon_monoxide=current.get("carbon_monoxide"),
        nitrogen_dioxide=current.get("nitrogen_dioxide"),
        sulphur_dioxide=current.get("sulphur_dioxide"),
        ozone=current.get("ozone"),
        us_aqi=current.get("us_aqi"),
    )

    return observation