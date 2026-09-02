from datetime import datetime, timezone

from database.connection import get_connection
from processor.analytics import (
    get_latest_weather_by_city,
    get_latest_air_quality_by_city,
)


def test_get_latest_weather_by_city():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO cities (name, country, latitude, longitude)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (name, country)
                DO UPDATE SET
                    latitude = EXCLUDED.latitude,
                    longitude = EXCLUDED.longitude
                RETURNING id;
                """,
                ("Analytics Test City", "Test Country", 10.0, 20.0),
            )

            city_id = cursor.fetchone()[0]

            cursor.execute(
                """
                INSERT INTO weather_observations (
                    city_id,
                    observed_at,
                    temperature_c,
                    humidity_percent,
                    apparent_temperature_c,
                    precipitation_mm,
                    weather_code,
                    wind_speed_kmh,
                    wind_direction_degrees
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s
                );
                """,
                (
                    city_id,
                    datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc),
                    20.0,
                    60.0,
                    19.5,
                    0.0,
                    1,
                    10.0,
                    180.0,
                ),
            )

        connection.commit()

        rows = get_latest_weather_by_city(connection)

        assert rows

        test_city_rows = [
            row for row in rows
            if row[1] == "Analytics Test City"
        ]

        assert len(test_city_rows) == 1
        assert test_city_rows[0][4] == 20.0

    finally:
        connection.rollback()

        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM weather_observations
                WHERE city_id IN (
                    SELECT id
                    FROM cities
                    WHERE name = %s AND country = %s
                );
                """,
                ("Analytics Test City", "Test Country"),
            )

            cursor.execute(
                """
                DELETE FROM cities
                WHERE name = %s AND country = %s;
                """,
                ("Analytics Test City", "Test Country"),
            )

        connection.commit()
        connection.close()


def test_get_latest_air_quality_by_city():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO cities (name, country, latitude, longitude)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (name, country)
                DO UPDATE SET
                    latitude = EXCLUDED.latitude,
                    longitude = EXCLUDED.longitude
                RETURNING id;
                """,
                ("Analytics AQ Test City", "Test Country", 11.0, 21.0),
            )

            city_id = cursor.fetchone()[0]

            cursor.execute(
                """
                INSERT INTO air_quality_observations (
                    city_id,
                    observed_at,
                    pm10,
                    pm2_5,
                    carbon_monoxide,
                    nitrogen_dioxide,
                    sulphur_dioxide,
                    ozone,
                    us_aqi
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s
                );
                """,
                (
                    city_id,
                    datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc),
                    25.0,
                    15.0,
                    200.0,
                    10.0,
                    2.0,
                    80.0,
                    50.0,
                ),
            )

        connection.commit()

        rows = get_latest_air_quality_by_city(connection)

        assert rows

        test_city_rows = [
            row for row in rows
            if row[1] == "Analytics AQ Test City"
        ]

        assert len(test_city_rows) == 1
        assert test_city_rows[0][5] == 15.0

    finally:
        connection.rollback()

        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM air_quality_observations
                WHERE city_id IN (
                    SELECT id
                    FROM cities
                    WHERE name = %s AND country = %s
                );
                """,
                ("Analytics AQ Test City", "Test Country"),
            )

            cursor.execute(
                """
                DELETE FROM cities
                WHERE name = %s AND country = %s;
                """,
                ("Analytics AQ Test City", "Test Country"),
            )

        connection.commit()
        connection.close()