from fastapi.testclient import TestClient
from datetime import datetime, timedelta

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
        connection.commit()
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
        connection.commit()

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
        connection.commit()

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
        connection.commit()

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


def test_weather_history():
    connection = get_connection()
    with connection.cursor() as c:
        c.execute("TRUNCATE TABLE weather_observations CASCADE;")
    connection.commit()

    try:
        city = {
            "name": "Test Weather History City",
            "country": "Test Weather History Country",
            "latitude": 15.3456,
            "longitude": 81.9012,
        }

        city_id = get_or_create_city(
            city,
            connection,
        )

        weather_1 = WeatherObservation(
            city="Test Weather History City",
            country="Test Weather History Country",
            latitude=15.3456,
            longitude=81.9012,
            observed_at=datetime.now() - timedelta(hours=2),
            temperature_c=28.0,
            humidity_percent=60.0,
            apparent_temperature_c=29.0,
            precipitation_mm=0.0,
            weather_code=1,
            wind_speed_kmh=8.0,
            wind_direction_degrees=180.0,
        )

        weather_2 = WeatherObservation(
            city="Test Weather History City",
            country="Test Weather History Country",
            latitude=15.3456,
            longitude=81.9012,
            observed_at=datetime.now() - timedelta(hours=1),
            temperature_c=29.0,
            humidity_percent=62.0,
            apparent_temperature_c=30.0,
            precipitation_mm=0.5,
            weather_code=2,
            wind_speed_kmh=9.0,
            wind_direction_degrees=190.0,
        )

        save_weather_observation(
            weather_1,
            city_id,
            connection,
        )

        save_weather_observation(
            weather_2,
            city_id,
            connection,
        )
        connection.commit()

    finally:
        connection.close()

    response = client.get(
        f"/weather/history/{city_id}?hours=24"
    )

    assert response.status_code == 200

    weather_data = response.json()

    assert isinstance(weather_data, list)
    assert len(weather_data) == 2

    assert weather_data[0]["temperature_c"] == 28.0
    assert weather_data[0]["humidity_percent"] == 60.0

    assert weather_data[1]["temperature_c"] == 29.0
    assert weather_data[1]["humidity_percent"] == 62.0

def test_air_quality_history():
    connection = get_connection()
    with connection.cursor() as c:
        c.execute("TRUNCATE TABLE air_quality_observations CASCADE;")
    connection.commit()

    try:
        city = {
            "name": "Test Air History City",
            "country": "Test Air History Country",
            "latitude": 16.3456,
            "longitude": 82.9012,
        }

        city_id = get_or_create_city(
            city,
            connection,
        )

        air_quality_1 = AirQualityObservation(
            city="Test Air History City",
            country="Test Air History Country",
            latitude=16.3456,
            longitude=82.9012,
            observed_at=datetime.now() - timedelta(hours=2),
            pm10=20.0,
            pm2_5=10.0,
            carbon_monoxide=300.0,
            nitrogen_dioxide=10.0,
            sulphur_dioxide=5.0,
            ozone=80.0,
            us_aqi=40.0,
        )

        air_quality_2 = AirQualityObservation(
            city="Test Air History City",
            country="Test Air History Country",
            latitude=16.3456,
            longitude=82.9012,
            observed_at=datetime.now() - timedelta(hours=1),
            pm10=25.0,
            pm2_5=15.0,
            carbon_monoxide=320.0,
            nitrogen_dioxide=12.0,
            sulphur_dioxide=6.0,
            ozone=85.0,
            us_aqi=50.0,
        )

        save_air_quality_observation(
            air_quality_1,
            city_id,
            connection,
        )

        save_air_quality_observation(
            air_quality_2,
            city_id,
            connection,
        )
        connection.commit()

    finally:
        connection.close()

    response = client.get(
        f"/air-quality/history/{city_id}?hours=24"
    )

    assert response.status_code == 200

    air_quality_data = response.json()

    assert isinstance(air_quality_data, list)
    assert len(air_quality_data) == 2

    assert air_quality_data[0]["pm10"] == 20.0
    assert air_quality_data[0]["pm2_5"] == 10.0
    assert air_quality_data[0]["us_aqi"] == 40.0

    assert air_quality_data[1]["pm10"] == 25.0
    assert air_quality_data[1]["pm2_5"] == 15.0
    assert air_quality_data[1]["us_aqi"] == 50.0


def test_pipeline_status():
    response = client.get("/pipeline/status")

    assert response.status_code == 200

    data = response.json()

    assert "status" in data
    assert "is_active" in data
    assert "started_at" in data
    assert "completed_at" in data
    assert "cities_processed" in data
    assert "cities_failed" in data
    assert isinstance(data["is_active"], bool)
def test_dashboard_summary():
    response = client.get("/dashboard/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_cities" in data
    assert "average_temperature_c" in data
    assert "average_aqi" in data

def test_dashboard_map():
    response = client.get("/dashboard/map")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "city_id" in data[0]
        assert "latitude" in data[0]
        assert "longitude" in data[0]
        assert "temperature_c" in data[0]
        assert "aqi" in data[0]

def test_dashboard_trends_success():
    connection = get_connection()
    try:
        city_id = get_or_create_city(
            {"name": "Trends API City", "country": "Test", "latitude": 0.0, "longitude": 0.0},
            connection
        )
        connection.commit()
    finally:
        connection.close()

    response = client.get(f"/dashboard/trends/{city_id}?metric=aqi&period=24h")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_dashboard_trends_invalid_city():
    response = client.get("/dashboard/trends/999999?metric=aqi&period=24h")
    assert response.status_code == 404

def test_dashboard_trends_invalid_metric():
    connection = get_connection()
    try:
        city_id = get_or_create_city({"name": "Test", "country": "Test", "latitude": 0, "longitude": 0}, connection)
        connection.commit()
    finally:
        connection.close()

    response = client.get(f"/dashboard/trends/{city_id}?metric=invalid&period=24h")
    assert response.status_code == 400

def test_dashboard_trends_invalid_period():
    connection = get_connection()
    try:
        city_id = get_or_create_city({"name": "Test", "country": "Test", "latitude": 0, "longitude": 0}, connection)
        connection.commit()
    finally:
        connection.close()

    response = client.get(f"/dashboard/trends/{city_id}?metric=aqi&period=99d")
    assert response.status_code == 400

def test_dashboard_changes_success():
    response = client.get("/dashboard/changes?metric=aqi")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_dashboard_changes_invalid_metric():
    response = client.get("/dashboard/changes?metric=temperature")
    assert response.status_code == 400

def test_dashboard_rankings_success():
    response = client.get("/dashboard/rankings?metric=aqi&period=24h")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_dashboard_rankings_invalid_metric():
    response = client.get("/dashboard/rankings?metric=invalid&period=24h")
    assert response.status_code == 400

def test_dashboard_pipeline():
    response = client.get("/dashboard/pipeline")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "cities_processed" in data
