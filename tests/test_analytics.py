from datetime import datetime, timezone

from database.connection import get_connection
from processor.analytics import (
    get_latest_weather_by_city,
    get_latest_air_quality_by_city,
    get_average_weather_by_city,
    get_average_air_quality_by_city,
    get_temperature_trend_by_city,
    get_pm25_trend_by_city,
    get_latest_city_snapshot,
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

def test_get_average_weather_by_city():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO cities (name, country, latitude, longitude)
                VALUES (%s, %s, %s, %s)
                RETURNING id;
                """,
                ("Average Weather Test City", "Test Country", 12.0, 22.0),
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
                VALUES
                    (%s, NOW() - INTERVAL '1 hour', 20.0, 60.0, 19.0, 2.0, 1, 10.0, 180.0),
                    (%s, NOW() - INTERVAL '2 hours', 24.0, 70.0, 23.0, 4.0, 2, 14.0, 200.0);
                """,
                (city_id, city_id),
            )

        connection.commit()

        rows = get_average_weather_by_city(connection, hours=24)

        test_city_rows = [
            row for row in rows
            if row[1] == "Average Weather Test City"
        ]

        assert len(test_city_rows) == 1

        row = test_city_rows[0]

        assert row[3] == 22.0
        assert row[4] == 65.0
        assert row[5] == 21.0
        assert row[6] == 3.0
        assert row[7] == 12.0

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
                ("Average Weather Test City", "Test Country"),
            )

            cursor.execute(
                """
                DELETE FROM cities
                WHERE name = %s AND country = %s;
                """,
                ("Average Weather Test City", "Test Country"),
            )

        connection.commit()
        connection.close()


def test_get_average_air_quality_by_city():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO cities (name, country, latitude, longitude)
                VALUES (%s, %s, %s, %s)
                RETURNING id;
                """,
                ("Average AQ Test City", "Test Country", 13.0, 23.0),
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
                VALUES
                    (%s, NOW() - INTERVAL '1 hour', 20.0, 10.0, 100.0, 10.0, 2.0, 80.0, 40.0),
                    (%s, NOW() - INTERVAL '2 hours', 30.0, 20.0, 200.0, 20.0, 4.0, 100.0, 60.0);
                """,
                (city_id, city_id),
            )

        connection.commit()

        rows = get_average_air_quality_by_city(connection, hours=24)

        test_city_rows = [
            row for row in rows
            if row[1] == "Average AQ Test City"
        ]

        assert len(test_city_rows) == 1

        row = test_city_rows[0]

        assert row[3] == 25.0
        assert row[4] == 15.0
        assert row[5] == 150.0
        assert row[6] == 15.0
        assert row[7] == 3.0
        assert row[8] == 90.0
        assert row[9] == 50.0

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
                ("Average AQ Test City", "Test Country"),
            )

            cursor.execute(
                """
                DELETE FROM cities
                WHERE name = %s AND country = %s;
                """,
                ("Average AQ Test City", "Test Country"),
            )

        connection.commit()
        connection.close()

def test_get_temperature_trend_by_city():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO cities (name, country, latitude, longitude)
                VALUES (%s, %s, %s, %s)
                RETURNING id;
                """,
                ("Temperature Trend Test City", "Test Country", 14.0, 24.0),
            )

            city_id = cursor.fetchone()[0]

            cursor.execute(
                """
                INSERT INTO weather_observations (
                    city_id,
                    observed_at,
                    temperature_c
                )
                VALUES
                    (%s, NOW() - INTERVAL '18 hours', 20.0),
                    (%s, NOW() - INTERVAL '16 hours', 22.0),
                    (%s, NOW() - INTERVAL '6 hours', 26.0),
                    (%s, NOW() - INTERVAL '4 hours', 28.0);
                """,
                (city_id, city_id, city_id, city_id),
            )

        connection.commit()

        rows = get_temperature_trend_by_city(connection, hours=24)

        test_city_rows = [
            row for row in rows
            if row[1] == "Temperature Trend Test City"
        ]

        assert len(test_city_rows) == 1

        row = test_city_rows[0]

        assert row[3] == 21.0
        assert row[4] == 27.0
        assert row[5] == 6.0
        assert row[6] == "increasing"

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
                ("Temperature Trend Test City", "Test Country"),
            )

            cursor.execute(
                """
                DELETE FROM cities
                WHERE name = %s AND country = %s;
                """,
                ("Temperature Trend Test City", "Test Country"),
            )

        connection.commit()
        connection.close()


def test_get_pm25_trend_by_city():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO cities (name, country, latitude, longitude)
                VALUES (%s, %s, %s, %s)
                RETURNING id;
                """,
                ("PM2.5 Trend Test City", "Test Country", 15.0, 25.0),
            )

            city_id = cursor.fetchone()[0]

            cursor.execute(
                """
                INSERT INTO air_quality_observations (
                    city_id,
                    observed_at,
                    pm2_5
                )
                VALUES
                    (%s, NOW() - INTERVAL '18 hours', 20.0),
                    (%s, NOW() - INTERVAL '16 hours', 30.0),
                    (%s, NOW() - INTERVAL '6 hours', 50.0),
                    (%s, NOW() - INTERVAL '4 hours', 60.0);
                """,
                (city_id, city_id, city_id, city_id),
            )

        connection.commit()

        rows = get_pm25_trend_by_city(connection, hours=24)

        test_city_rows = [
            row for row in rows
            if row[1] == "PM2.5 Trend Test City"
        ]

        assert len(test_city_rows) == 1

        row = test_city_rows[0]

        assert row[3] == 25.0
        assert row[4] == 55.0
        assert row[5] == 30.0
        assert row[6] == "increasing"

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
                ("PM2.5 Trend Test City", "Test Country"),
            )

            cursor.execute(
                """
                DELETE FROM cities
                WHERE name = %s AND country = %s;
                """,
                ("PM2.5 Trend Test City", "Test Country"),
            )

        connection.commit()
        connection.close()

def test_get_latest_city_snapshot():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO cities (name, country, latitude, longitude)
                VALUES (%s, %s, %s, %s)
                RETURNING id;
                """,
                ("City Snapshot Test City", "Test Country", 16.0, 26.0),
            )

            city_id = cursor.fetchone()[0]

            cursor.execute(
                """
                INSERT INTO weather_observations (
                    city_id,
                    observed_at,
                    temperature_c,
                    humidity_percent
                )
                VALUES (
                    %s,
                    NOW() - INTERVAL '1 hour',
                    25.0,
                    65.0
                );
                """,
                (city_id,),
            )

            cursor.execute(
                """
                INSERT INTO air_quality_observations (
                    city_id,
                    observed_at,
                    pm10,
                    pm2_5,
                    us_aqi
                )
                VALUES (
                    %s,
                    NOW() - INTERVAL '2 hours',
                    30.0,
                    15.0,
                    50.0
                );
                """,
                (city_id,),
            )

        connection.commit()

        rows = get_latest_city_snapshot(connection)

        test_city_rows = [
            row for row in rows
            if row[1] == "City Snapshot Test City"
        ]

        assert len(test_city_rows) == 1

        row = test_city_rows[0]

        assert row[4] == 25.0
        assert row[5] == 65.0

        assert row[12] == 30.0
        assert row[13] == 15.0
        assert row[18] == 50.0

        assert row[3] is not None
        assert row[11] is not None

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
                ("City Snapshot Test City", "Test Country"),
            )

            cursor.execute(
                """
                DELETE FROM air_quality_observations
                WHERE city_id IN (
                    SELECT id
                    FROM cities
                    WHERE name = %s AND country = %s
                );
                """,
                ("City Snapshot Test City", "Test Country"),
            )

            cursor.execute(
                """
                DELETE FROM cities
                WHERE name = %s AND country = %s;
                """,
                ("City Snapshot Test City", "Test Country"),
            )

        connection.commit()
        connection.close()