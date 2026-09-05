from fastapi.testclient import TestClient
from datetime import datetime

from api.main import app
from database.connection import get_connection
from ingestion.models import (
    WeatherObservation,
    AirQualityObservation,
)
from database.repositories import (
    get_or_create_city,
    save_weather_observation,
    save_air_quality_observation,
    save_air_quality_observation,
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

def test_get_latest_air_quality():
    connection = get_connection()

    try:
        city = {
            "name": "Test Air Quality City",
            "country": "Test Air Quality Country",
            "latitude": 13.3456,
            "longitude": 79.9012,
        }

        city_id = get_or_create_city(
            city,
            connection,
        )

        air_quality = AirQualityObservation(
            city="Test Air Quality City",
            country="Test Air Quality Country",
            latitude=13.3456,
            longitude=79.9012,
            observed_at=datetime(2026, 9, 2, 12, 0),
            pm10=20.0,
            pm2_5=10.0,
            carbon_monoxide=300.0,
            nitrogen_dioxide=10.0,
            sulphur_dioxide=5.0,
            ozone=100.0,
            us_aqi=50.0,
        )

        save_air_quality_observation(
            air_quality,
            city_id,
            connection,
        )

    finally:
        connection.close()

    response = client.get("/air-quality/latest")

    assert response.status_code == 200

    air_quality_data = response.json()

    assert isinstance(air_quality_data, list)

    test_city = next(
        item
        for item in air_quality_data
        if item["name"] == "Test Air Quality City"
        and item["country"] == "Test Air Quality Country"
    )

    assert test_city["pm10"] == 20.0
    assert test_city["pm2_5"] == 10.0
    assert test_city["carbon_monoxide"] == 300.0
    assert test_city["nitrogen_dioxide"] == 10.0
    assert test_city["sulphur_dioxide"] == 5.0
    assert test_city["ozone"] == 100.0
    assert test_city["us_aqi"] == 50.0


def test_get_analytics():
    connection = get_connection()

    try:
        city = {
            "name": "Test Analytics City",
            "country": "Test Analytics Country",
            "latitude": 14.3456,
            "longitude": 80.9012,
        }

        city_id = get_or_create_city(
            city,
            connection,
        )

        weather = WeatherObservation(
            city="Test Analytics City",
            country="Test Analytics Country",
            latitude=14.3456,
            longitude=80.9012,
            observed_at=datetime(2026, 9, 2, 12, 0),
            temperature_c=31.0,
            humidity_percent=70.0,
            apparent_temperature_c=33.0,
            precipitation_mm=1.0,
            weather_code=2,
            wind_speed_kmh=10.0,
            wind_direction_degrees=200.0,
        )

        save_weather_observation(
            weather,
            city_id,
            connection,
        )

        air_quality = AirQualityObservation(
            city="Test Analytics City",
            country="Test Analytics Country",
            latitude=14.3456,
            longitude=80.9012,
            observed_at=datetime(2026, 9, 2, 12, 0),
            pm10=25.0,
            pm2_5=12.0,
            carbon_monoxide=350.0,
            nitrogen_dioxide=15.0,
            sulphur_dioxide=6.0,
            ozone=90.0,
            us_aqi=55.0,
        )

        save_air_quality_observation(
            air_quality,
            city_id,
            connection,
        )

    finally:
        connection.close()

    response = client.get("/analytics")

    assert response.status_code == 200

    analytics_data = response.json()

    assert isinstance(analytics_data, list)

    test_city = next(
        item
        for item in analytics_data
        if item["name"] == "Test Analytics City"
        and item["country"] == "Test Analytics Country"
    )

    assert test_city["weather"]["temperature_c"] == 31.0
    assert test_city["weather"]["humidity_percent"] == 70.0
    assert test_city["weather"]["weather_code"] == 2

    assert test_city["air_quality"]["pm10"] == 25.0
    assert test_city["air_quality"]["pm2_5"] == 12.0
    assert test_city["air_quality"]["us_aqi"] == 55.0