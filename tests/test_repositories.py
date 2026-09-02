from datetime import datetime

from database.connection import get_connection
from database.repositories import (
    get_or_create_city,
    save_weather_observation,
    save_air_quality_observation,
    create_pipeline_run,
    complete_pipeline_run,
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

def test_pipeline_run_repository():
    connection = get_connection()

    try:
        started_at = datetime(2026, 9, 2, 10, 0)

        run_id = create_pipeline_run(
            started_at,
            connection,
        )

        assert run_id is not None

        completed_at = datetime(2026, 9, 2, 10, 0, 8)

        complete_pipeline_run(
            run_id=run_id,
            completed_at=completed_at,
            status="SUCCESS",
            cities_processed=5,
            cities_failed=0,
            duration_seconds=8.0,
            connection=connection,
        )

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    started_at,
                    completed_at,
                    status,
                    cities_processed,
                    cities_failed,
                    duration_seconds,
                    error_message
                FROM pipeline_runs
                WHERE id = %s;
                """,
                (run_id,),
            )

            row = cursor.fetchone()

        assert row is not None
        assert row[0] == started_at
        assert row[1] == completed_at
        assert row[2] == "SUCCESS"
        assert row[3] == 5
        assert row[4] == 0
        assert row[5] == 8.0
        assert row[6] is None

    finally:
        connection.close()