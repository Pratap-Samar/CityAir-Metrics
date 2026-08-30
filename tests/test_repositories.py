from datetime import datetime

from database.connection import get_connection
from database.repositories import (
    get_or_create_city,
    save_weather_observation,
    save_air_quality_observation,
)
from ingestion.models import (
    WeatherObservation,
    AirQualityObservation,
)


def test_repository_integration():

    connection = get_connection()

    try:
        city = {
            "name": "Test City",
            "country": "Test Country",
            "latitude": 10.1234,
            "longitude": 20.5678,
        }

        city_id = get_or_create_city(
            city,
            connection,
        )

        assert city_id is not None

        weather = WeatherObservation(
            city="Test City",
            country="Test Country",
            latitude=10.1234,
            longitude=20.5678,
            observed_at=datetime(2026, 8, 31, 12, 0),
            temperature_c=30.0,
            humidity_percent=60.0,
            apparent_temperature_c=32.0,
            precipitation_mm=0.0,
            weather_code=1,
            wind_speed_kmh=5.0,
            wind_direction_degrees=180.0,
        )

        weather_id = save_weather_observation(
            weather,
            city_id,
            connection,
        )

        assert weather_id is not None

        air_quality = AirQualityObservation(
            city="Test City",
            country="Test Country",
            latitude=10.1234,
            longitude=20.5678,
            observed_at=datetime(2026, 8, 31, 12, 0),
            pm10=20.0,
            pm2_5=10.0,
            carbon_monoxide=300.0,
            nitrogen_dioxide=10.0,
            sulphur_dioxide=5.0,
            ozone=100.0,
            us_aqi=50.0,
        )

        air_quality_id = save_air_quality_observation(
            air_quality,
            city_id,
            connection,
        )

        assert air_quality_id is not None

    finally:
        connection.close()
