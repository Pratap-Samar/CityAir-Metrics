from fastapi.testclient import TestClient
from datetime import datetime

from api.main import app
from database.connection import get_connection
from ingestion.models import WeatherObservation
from database.repositories import (
    get_or_create_city,
    save_weather_observation,
)

client = TestClient(app)


def test_get_cities():
    connection = get_connection()

    try:
        city = {
            "name": "Test API City",
            "country": "Test API Country",
            "latitude": 11.1234,
            "longitude": 21.5678,
        }

        get_or_create_city(
            city,
            connection,
        )
    finally:
        connection.close()

    response = client.get("/cities")

    assert response.status_code == 200

    cities = response.json()

    assert isinstance(cities, list)

    test_city = next(
        city
        for city in cities
        if city["name"] == "Test API City"
        and city["country"] == "Test API Country"
    )

    assert test_city["latitude"] == 11.1234
    assert test_city["longitude"] == 21.5678

def test_get_latest_weather():
    connection = get_connection()

    try:
        city = {
            "name": "Test Weather City",
            "country": "Test Weather Country",
            "latitude": 12.3456,
            "longitude": 78.9012,
        }

        city_id = get_or_create_city(
            city,
            connection,
        )

        weather = WeatherObservation(
            city="Test Weather City",
            country="Test Weather Country",
            latitude=12.3456,
            longitude=78.9012,
            observed_at=datetime(2026, 9, 2, 12, 0),
            temperature_c=30.0,
            humidity_percent=65.0,
            apparent_temperature_c=32.0,
            precipitation_mm=0.0,
            weather_code=1,
            wind_speed_kmh=8.0,
            wind_direction_degrees=180.0,
        )

        save_weather_observation(
            weather,
            city_id,
            connection,
        )

    finally:
        connection.close()

    response = client.get("/weather/latest")

    assert response.status_code == 200

    weather_data = response.json()

    assert isinstance(weather_data, list)

    test_city = next(
        item
        for item in weather_data
        if item["name"] == "Test Weather City"
        and item["country"] == "Test Weather Country"
    )

    assert test_city["temperature_c"] == 30.0
    assert test_city["humidity_percent"] == 65.0
    assert test_city["apparent_temperature_c"] == 32.0
    assert test_city["precipitation_mm"] == 0.0
    assert test_city["weather_code"] == 1
    assert test_city["wind_speed_kmh"] == 8.0
    assert test_city["wind_direction_degrees"] == 180.0