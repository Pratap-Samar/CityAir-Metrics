from datetime import datetime, timezone
import pytest

from database.connection import get_connection
from database.repositories import get_or_create_city
from processor.analytics import (
    _calculate_trend,
    get_latest_weather_by_city,
    get_latest_air_quality_by_city,
    get_average_weather_by_city,
    get_average_air_quality_by_city,
    get_temperature_trend_by_city,
    get_pm25_trend_by_city,
    get_latest_city_snapshot,
    get_weather_history_by_city,
    get_air_quality_history_by_city,
)

def test_calculate_trend_increasing():
    result = _calculate_trend(40.0, 50.0)

    assert result[0] == 10.0
    assert result[1] == 25.0
    assert result[2] == "increasing"

def test_calculate_trend_decreasing():
    result = _calculate_trend(50.0, 40.0)

    assert result[0] == -10.0
    assert result[1] == -20.0
    assert result[2] == "decreasing"

def test_calculate_trend_stable():
    result = _calculate_trend(50.0, 50.0)

    assert result[0] == 0.0
    assert result[1] == 0.0
    assert result[2] == "stable"


def test_calculate_trend_missing_previous_average():
    result = _calculate_trend(None, 50.0)

    assert result == (None, None, None)

def test_calculate_trend_missing_recent_average():
    result = _calculate_trend(50.0, None)

    assert result == (None, None, None)
def test_calculate_trend_stable_within_two_percent():
    result = _calculate_trend(100.0, 101.0)

    assert result[0] == 1.0
    assert result[1] == 1.0
    assert result[2] == "stable"


def test_calculate_trend_increasing_above_two_percent():
    result = _calculate_trend(100.0, 103.0)

    assert result[0] == 3.0
    assert result[1] == 3.0
    assert result[2] == "increasing"


def test_calculate_trend_decreasing_below_two_percent():
    result = _calculate_trend(100.0, 97.0)

    assert result[0] == -3.0
    assert result[1] == -3.0
    assert result[2] == "decreasing"


def test_calculate_trend_zero_previous_average():
    result = _calculate_trend(0.0, 10.0)

    assert result[0] == 10.0
    assert result[1] is None
    assert result[2] == "increasing"


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
                    (%s, NOW() - INTERVAL '42 hours', 20.0),
                    (%s, NOW() - INTERVAL '36 hours', 22.0),
                    (%s, NOW() - INTERVAL '18 hours', 26.0),
                    (%s, NOW() - INTERVAL '6 hours', 28.0);
                """,
                (city_id, city_id, city_id, city_id),
            )

        connection.commit()

        rows = get_temperature_trend_by_city(
            connection,
            period="24h",
        )

        test_city_rows = [
            row for row in rows
            if row[1] == "Temperature Trend Test City"
        ]

        assert len(test_city_rows) == 1

        row = test_city_rows[0]

        # Previous 24h: 24–48 hours ago
        assert row[3] == 21.0

        # Current 24h: 0–24 hours ago
        assert row[4] == 27.0

        # Absolute change
        assert row[5] == 6.0

        # Percentage change
        assert row[6] == pytest.approx(28.5714285714)

        # Direction
        assert row[7] == "increasing"

        # Coverage
        assert row[8] == 2
        assert row[9] == 2

    finally:
        connection.rollback()

        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM weather_observations
                WHERE city_id = (
                    SELECT id
                    FROM cities
                    WHERE name = %s
                      AND country = %s
                );
                """,
                (
                    "Temperature Trend Test City",
                    "Test Country",
                ),
            )

            cursor.execute(
                """
                DELETE FROM cities
                WHERE name = %s
                  AND country = %s;
                """,
                (
                    "Temperature Trend Test City",
                    "Test Country",
                ),
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
                    (%s, NOW() - INTERVAL '42 hours', 20.0),
                    (%s, NOW() - INTERVAL '36 hours', 30.0),
                    (%s, NOW() - INTERVAL '18 hours', 50.0),
                    (%s, NOW() - INTERVAL '6 hours', 60.0);
                """,
                (city_id, city_id, city_id, city_id),
            )

        connection.commit()

        rows = get_pm25_trend_by_city(
            connection,
            period="24h",
        )
        test_city_rows = [
            row for row in rows
            if row[1] == "PM2.5 Trend Test City"
        ]

        assert len(test_city_rows) == 1

        row = test_city_rows[0]

        assert row[3] == 25.0
        assert row[4] == 55.0
        assert row[5] == 30.0
        assert row[6] == pytest.approx(120.0)
        assert row[7] == "increasing"
        assert row[8] == 2
        assert row[9] == 2

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


def test_get_weather_history_by_city():
    connection = get_connection()

    try:
        city_id = get_or_create_city(
            {
                "name": "History Test City",
                "country": "Test Country",
                "latitude": 10.0,
                "longitude": 20.0,
            },
            connection,
        )

        with connection.cursor() as cursor:
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
                    (%s, NOW() - INTERVAL '2 hours', 20.0, 60.0, 19.0, 0.0, 1, 10.0, 180.0),
                    (%s, NOW() - INTERVAL '1 hour', 21.0, 62.0, 20.0, 0.5, 2, 11.0, 190.0)
                ON CONFLICT (city_id, observed_at) DO NOTHING;
                """,
                (city_id, city_id),
            )

        connection.commit()

        rows = get_weather_history_by_city(
            connection,
            city_id,
            hours=24,
        )

        assert len(rows) >= 2

        timestamps = [row[0] for row in rows]
        assert timestamps == sorted(timestamps)

        temperatures = [row[1] for row in rows]

        assert 20.0 in temperatures
        assert 21.0 in temperatures

    finally:
        connection.close()


def test_get_air_quality_history_by_city():
    connection = get_connection()

    try:
        city_id = get_or_create_city(
            {
                "name": "AQ History Test City",
                "country": "Test Country",
                "latitude": 11.0,
                "longitude": 21.0,
            },
            connection,
        )

        with connection.cursor() as cursor:
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
                    (%s, NOW() - INTERVAL '2 hours', 30.0, 15.0, 200.0, 20.0, 5.0, 80.0, 60.0),
                    (%s, NOW() - INTERVAL '1 hour', 32.0, 17.0, 210.0, 22.0, 6.0, 82.0, 65.0)
                ON CONFLICT (city_id, observed_at) DO NOTHING;
                """,
                (city_id, city_id),
            )

        connection.commit()

        rows = get_air_quality_history_by_city(
            connection,
            city_id,
            hours=24,
        )

        assert len(rows) >= 2

        timestamps = [row[0] for row in rows]
        assert timestamps == sorted(timestamps)

        pm25_values = [row[2] for row in rows]

        assert 15.0 in pm25_values
        assert 17.0 in pm25_values

    finally:
        connection.close()
def test_get_dashboard_summary():
    from processor.analytics import get_dashboard_summary
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE weather_observations, air_quality_observations, cities, pipeline_runs CASCADE;")

            cursor.execute(
                "INSERT INTO cities (name, country, latitude, longitude) VALUES (%s, %s, %s, %s) RETURNING id;",
                ("Summary City 1", "Test", 1, 1)
            )
            c1 = cursor.fetchone()[0]

            cursor.execute(
                "INSERT INTO cities (name, country, latitude, longitude) VALUES (%s, %s, %s, %s) RETURNING id;",
                ("Summary City 2", "Test", 2, 2)
            )
            c2 = cursor.fetchone()[0]

            # City 1: latest weather 20C, prev weather 10C
            cursor.execute("INSERT INTO weather_observations (city_id, observed_at, temperature_c) VALUES (%s, CURRENT_TIMESTAMP - INTERVAL '2 hours', %s);", (c1, 20.0))
            cursor.execute("INSERT INTO weather_observations (city_id, observed_at, temperature_c) VALUES (%s, CURRENT_TIMESTAMP - INTERVAL '26 hours', %s);", (c1, 10.0))

            # City 2: latest weather 30C, prev weather 10C
            cursor.execute("INSERT INTO weather_observations (city_id, observed_at, temperature_c) VALUES (%s, CURRENT_TIMESTAMP - INTERVAL '1 hours', %s);", (c2, 30.0))
            cursor.execute("INSERT INTO weather_observations (city_id, observed_at, temperature_c) VALUES (%s, CURRENT_TIMESTAMP - INTERVAL '25 hours', %s);", (c2, 10.0))

            # City 1: latest AQI 100, prev 50
            cursor.execute("INSERT INTO air_quality_observations (city_id, observed_at, us_aqi) VALUES (%s, CURRENT_TIMESTAMP - INTERVAL '2 hours', %s);", (c1, 100.0))
            cursor.execute("INSERT INTO air_quality_observations (city_id, observed_at, us_aqi) VALUES (%s, CURRENT_TIMESTAMP - INTERVAL '26 hours', %s);", (c1, 50.0))

            # City 2: latest AQI 200, prev 50
            cursor.execute("INSERT INTO air_quality_observations (city_id, observed_at, us_aqi) VALUES (%s, CURRENT_TIMESTAMP - INTERVAL '1 hours', %s);", (c2, 200.0))
            cursor.execute("INSERT INTO air_quality_observations (city_id, observed_at, us_aqi) VALUES (%s, CURRENT_TIMESTAMP - INTERVAL '25 hours', %s);", (c2, 50.0))

        connection.commit()

        summary = get_dashboard_summary(connection)

        assert summary['total_cities'] == 2

        # Avg temp: (20 + 30)/2 = 25
        assert summary['average_temperature_c'] == 25.0
        # Prev avg temp: (10 + 10)/2 = 10
        assert summary['previous_period_temperature_c'] == 10.0
        assert summary['temperature_absolute_change'] == 15.0
        assert summary['temperature_percentage_change'] == 150.0
        assert summary['temperature_direction'] == "increasing"

        # Avg AQI: (100 + 200)/2 = 150
        assert summary['average_aqi'] == 150.0
        assert summary['previous_period_aqi'] == 50.0

        # Freshness
        assert summary['last_observation_at'] is not None
        assert summary['weather_freshness_minutes'] >= 60  # oldest is 2h, latest is 1h => 60m
        assert summary['air_quality_freshness_minutes'] >= 60
        assert summary['data_freshness_minutes'] >= 60

    finally:
        connection.rollback()
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE weather_observations, air_quality_observations, cities, pipeline_runs CASCADE;")
        connection.commit()
        connection.close()


def test_get_dashboard_map_data():
    from processor.analytics import get_dashboard_map_data
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE weather_observations, air_quality_observations, cities CASCADE;")
            cursor.execute(
                "INSERT INTO cities (name, country, latitude, longitude) VALUES (%s, %s, %s, %s) RETURNING id;",
                ("Map City 1", "Test", 1.0, 1.0)
            )
            c1 = cursor.fetchone()[0]

            # City 1: weather but NO air quality
            cursor.execute(
                "INSERT INTO weather_observations (city_id, observed_at, temperature_c, humidity_percent, wind_speed_kmh, precipitation_mm) VALUES (%s, CURRENT_TIMESTAMP, %s, %s, %s, %s);",
                (c1, 25.0, 60.0, 15.0, 0.0)
            )

            cursor.execute(
                "INSERT INTO cities (name, country, latitude, longitude) VALUES (%s, %s, %s, %s) RETURNING id;",
                ("Map City 2", "Test", 2.0, 2.0)
            )
            c2 = cursor.fetchone()[0]

            # City 2: air quality but NO weather
            cursor.execute(
                "INSERT INTO air_quality_observations (city_id, observed_at, us_aqi, pm2_5, pm10) VALUES (%s, CURRENT_TIMESTAMP, %s, %s, %s);",
                (c2, 100.0, 25.0, 50.0)
            )

        connection.commit()

        map_data = get_dashboard_map_data(connection)
        assert len(map_data) == 2

        # Check City 1
        city1 = next(c for c in map_data if c['city_id'] == c1)
        assert city1['temperature_c'] == 25.0
        assert city1['aqi'] is None
        assert city1['weather_observed_at'] is not None
        assert city1['air_quality_observed_at'] is None

        # Check City 2
        city2 = next(c for c in map_data if c['city_id'] == c2)
        assert city2['temperature_c'] is None
        assert city2['aqi'] == 100.0
        assert city2['weather_observed_at'] is None
        assert city2['air_quality_observed_at'] is not None

    finally:
        connection.rollback()
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE weather_observations, air_quality_observations, cities CASCADE;")
        connection.commit()
        connection.close()

def test_get_time_series_trends():
    from processor.analytics import get_time_series_trends
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE weather_observations, air_quality_observations, cities CASCADE;")
            cursor.execute("INSERT INTO cities (name, country, latitude, longitude) VALUES (%s, %s, %s, %s) RETURNING id;", ("Trend City", "Test", 1.0, 1.0))
            c1 = cursor.fetchone()[0]

            # 24h: hourly data (2 observations in same hour should aggregate)
            cursor.execute("INSERT INTO air_quality_observations (city_id, observed_at, us_aqi) VALUES (%s, CURRENT_TIMESTAMP - INTERVAL '2 hours', %s);", (c1, 100.0))
            cursor.execute("INSERT INTO air_quality_observations (city_id, observed_at, us_aqi) VALUES (%s, CURRENT_TIMESTAMP - INTERVAL '2 hours' - INTERVAL '10 minutes', %s);", (c1, 150.0))

            # 7d: daily data
            cursor.execute("INSERT INTO weather_observations (city_id, observed_at, temperature_c) VALUES (%s, CURRENT_DATE - INTERVAL '1 days', %s);", (c1, 20.0))
            cursor.execute("INSERT INTO weather_observations (city_id, observed_at, temperature_c) VALUES (%s, CURRENT_DATE - INTERVAL '1 days' + INTERVAL '5 hours', %s);", (c1, 30.0))

        connection.commit()

        # Test 24h AQI
        aqi_24h = get_time_series_trends(connection, c1, metric="aqi", period="24h")
        assert len(aqi_24h) == 1
        assert aqi_24h[0]['value'] == 125.0
        assert aqi_24h[0]['observation_count'] == 2

        # Test 7d Temperature
        temp_7d = get_time_series_trends(connection, c1, metric="temperature", period="7d")
        assert len(temp_7d) == 1
        assert temp_7d[0]['value'] == 25.0
        assert temp_7d[0]['observation_count'] == 2

    finally:
        connection.rollback()
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE weather_observations, air_quality_observations, cities CASCADE;")
        connection.commit()
        connection.close()

def test_get_biggest_changes():
    from processor.analytics import get_biggest_changes
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE weather_observations, air_quality_observations, cities CASCADE;")

            cursor.execute("INSERT INTO cities (name, country, latitude, longitude) VALUES (%s, %s, %s, %s) RETURNING id;", ("Change City A", "Test", 1.0, 1.0))
            c_a = cursor.fetchone()[0]
            cursor.execute("INSERT INTO cities (name, country, latitude, longitude) VALUES (%s, %s, %s, %s) RETURNING id;", ("Change City B", "Test", 2.0, 2.0))
            c_b = cursor.fetchone()[0]

            # City A: prev 50, curr 100 -> +50, +100%
            cursor.execute("INSERT INTO air_quality_observations (city_id, observed_at, us_aqi) VALUES (%s, CURRENT_TIMESTAMP - INTERVAL '26 hours', %s);", (c_a, 50.0))
            cursor.execute("INSERT INTO air_quality_observations (city_id, observed_at, us_aqi) VALUES (%s, CURRENT_TIMESTAMP - INTERVAL '2 hours', %s);", (c_a, 100.0))

            # City B: prev 100, curr 250 -> +150, +150%
            cursor.execute("INSERT INTO air_quality_observations (city_id, observed_at, us_aqi) VALUES (%s, CURRENT_TIMESTAMP - INTERVAL '26 hours', %s);", (c_b, 100.0))
            cursor.execute("INSERT INTO air_quality_observations (city_id, observed_at, us_aqi) VALUES (%s, CURRENT_TIMESTAMP - INTERVAL '2 hours', %s);", (c_b, 250.0))

        connection.commit()

        changes = get_biggest_changes(connection, metric="aqi")
        assert len(changes) == 2

        # Primary ordering by percentage magnitude DESC
        assert changes[0]['city_id'] == c_b
        assert changes[0]['percentage_change'] == 150.0
        assert changes[0]['absolute_change'] == 150.0

        assert changes[1]['city_id'] == c_a
        assert changes[1]['percentage_change'] == 100.0

    finally:
        connection.rollback()
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE weather_observations, air_quality_observations, cities CASCADE;")
        connection.commit()
        connection.close()


def test_get_city_rankings():
    from processor.analytics import get_city_rankings
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE weather_observations, air_quality_observations, cities CASCADE;")

            cursor.execute("INSERT INTO cities (name, country, latitude, longitude) VALUES (%s, %s, %s, %s) RETURNING id;", ("Rank City 1", "Test", 1.0, 1.0))
            c1 = cursor.fetchone()[0]
            cursor.execute("INSERT INTO cities (name, country, latitude, longitude) VALUES (%s, %s, %s, %s) RETURNING id;", ("Rank City 2", "Test", 2.0, 2.0))
            c2 = cursor.fetchone()[0]

            # City 1 AQI 150
            cursor.execute("INSERT INTO air_quality_observations (city_id, observed_at, us_aqi) VALUES (%s, CURRENT_TIMESTAMP - INTERVAL '2 hours', %s);", (c1, 150.0))

            # City 2 AQI 100
            cursor.execute("INSERT INTO air_quality_observations (city_id, observed_at, us_aqi) VALUES (%s, CURRENT_TIMESTAMP - INTERVAL '2 hours', %s);", (c2, 100.0))

        connection.commit()

        rankings = get_city_rankings(connection, metric="aqi", period="24h")
        assert len(rankings) == 2

        # ordered DESC
        assert rankings[0]['city_id'] == c1
        assert rankings[0]['value'] == 150.0

        assert rankings[1]['city_id'] == c2
        assert rankings[1]['value'] == 100.0

    finally:
        connection.rollback()
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE weather_observations, air_quality_observations, cities CASCADE;")
        connection.commit()
        connection.close()


def test_get_dashboard_pipeline_status():
    from processor.analytics import get_dashboard_pipeline_status
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE pipeline_runs CASCADE;")
            cursor.execute("INSERT INTO pipeline_runs (status, started_at, completed_at, duration_seconds, cities_processed, cities_failed, error_message) VALUES (%s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 10, 20, 0, NULL);", ("SUCCESS",))

        connection.commit()

        status = get_dashboard_pipeline_status(connection)
        assert status is not None
        assert status['status'] == "SUCCESS"
        assert status['duration_seconds'] == 10
        assert status['cities_processed'] == 20
        assert status['cities_failed'] == 0

    finally:
        connection.rollback()
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE pipeline_runs CASCADE;")
        connection.commit()
        connection.close()
def test_get_time_series_trends_extended():
    from processor.analytics import get_time_series_trends
    import pytest
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE weather_observations, air_quality_observations, cities CASCADE;")
            cursor.execute("INSERT INTO cities (name, country, latitude, longitude) VALUES (%s, %s, %s, %s) RETURNING id;", ("Trend City 2", "Test", 1.0, 1.0))
            c1 = cursor.fetchone()[0]

            cursor.execute("INSERT INTO weather_observations (city_id, observed_at, temperature_c) VALUES (%s, CURRENT_TIMESTAMP - INTERVAL '1 hours', %s);", (c1, 20.0))
            cursor.execute("INSERT INTO air_quality_observations (city_id, observed_at, us_aqi) VALUES (%s, CURRENT_DATE - INTERVAL '2 days', %s);", (c1, 100.0))
            cursor.execute("INSERT INTO weather_observations (city_id, observed_at, temperature_c) VALUES (%s, CURRENT_DATE - INTERVAL '20 days', %s);", (c1, 15.0))
            cursor.execute("INSERT INTO air_quality_observations (city_id, observed_at, us_aqi) VALUES (%s, CURRENT_DATE - INTERVAL '20 days', %s);", (c1, 150.0))
        connection.commit()

        temp_24h = get_time_series_trends(connection, c1, metric="temperature", period="24h")
        assert len(temp_24h) >= 1
        assert any(x['value'] == 20.0 for x in temp_24h)

        aqi_7d = get_time_series_trends(connection, c1, metric="aqi", period="7d")
        assert len(aqi_7d) >= 1
        assert any(x['value'] == 100.0 for x in aqi_7d)

        temp_30d = get_time_series_trends(connection, c1, metric="temperature", period="30d")
        assert len(temp_30d) >= 1
        assert any(x['value'] == 15.0 for x in temp_30d)

        aqi_30d = get_time_series_trends(connection, c1, metric="aqi", period="30d")
        assert len(aqi_30d) >= 1
        assert any(x['value'] == 150.0 for x in aqi_30d)

        with pytest.raises(ValueError, match="Unsupported metric"):
            get_time_series_trends(connection, c1, metric="invalid", period="24h")

        with pytest.raises(ValueError, match="Unsupported period"):
            get_time_series_trends(connection, c1, metric="aqi", period="99d")

    finally:
        connection.rollback()
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE weather_observations, air_quality_observations, cities CASCADE;")
        connection.commit()
        connection.close()

def test_dashboard_summary_null_metrics():
    from processor.analytics import get_dashboard_summary
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE weather_observations, air_quality_observations, cities CASCADE;")
            cursor.execute("INSERT INTO cities (name, country, latitude, longitude) VALUES (%s, %s, %s, %s) RETURNING id;", ("Null City", "Test", 1.0, 1.0))
            c1 = cursor.fetchone()[0]

            cursor.execute("INSERT INTO weather_observations (city_id, observed_at, temperature_c) VALUES (%s, CURRENT_TIMESTAMP - INTERVAL '3 hours', %s);", (c1, 20.0))
            cursor.execute("INSERT INTO air_quality_observations (city_id, observed_at, us_aqi) VALUES (%s, CURRENT_TIMESTAMP - INTERVAL '3 hours', %s);", (c1, 100.0))

            cursor.execute("INSERT INTO weather_observations (city_id, observed_at, temperature_c) VALUES (%s, CURRENT_TIMESTAMP - INTERVAL '1 hours', NULL);", (c1,))
            cursor.execute("INSERT INTO air_quality_observations (city_id, observed_at, us_aqi) VALUES (%s, CURRENT_TIMESTAMP - INTERVAL '1 hours', NULL);", (c1,))
        connection.commit()

        summary = get_dashboard_summary(connection)
        assert summary['average_temperature_c'] == 20.0
        assert summary['average_aqi'] == 100.0

        assert 170 <= summary['weather_freshness_minutes'] <= 190
        assert 170 <= summary['air_quality_freshness_minutes'] <= 190

    finally:
        connection.rollback()
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE weather_observations, air_quality_observations, cities CASCADE;")
        connection.commit()
        connection.close()

def test_biggest_changes_zero_previous():
    from processor.analytics import get_biggest_changes
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE weather_observations, air_quality_observations, cities CASCADE;")

            cursor.execute("INSERT INTO cities (name, country, latitude, longitude) VALUES (%s, %s, %s, %s) RETURNING id;", ("Zero City", "Test", 1.0, 1.0))
            c_zero = cursor.fetchone()[0]
            cursor.execute("INSERT INTO cities (name, country, latitude, longitude) VALUES (%s, %s, %s, %s) RETURNING id;", ("Normal City", "Test", 2.0, 2.0))
            c_norm = cursor.fetchone()[0]

            cursor.execute("INSERT INTO air_quality_observations (city_id, observed_at, us_aqi) VALUES (%s, CURRENT_TIMESTAMP - INTERVAL '26 hours', %s);", (c_zero, 0.0))
            cursor.execute("INSERT INTO air_quality_observations (city_id, observed_at, us_aqi) VALUES (%s, CURRENT_TIMESTAMP - INTERVAL '2 hours', %s);", (c_zero, 50.0))

            cursor.execute("INSERT INTO air_quality_observations (city_id, observed_at, us_aqi) VALUES (%s, CURRENT_TIMESTAMP - INTERVAL '26 hours', %s);", (c_norm, 10.0))
            cursor.execute("INSERT INTO air_quality_observations (city_id, observed_at, us_aqi) VALUES (%s, CURRENT_TIMESTAMP - INTERVAL '2 hours', %s);", (c_norm, 20.0))

        connection.commit()

        changes = get_biggest_changes(connection, metric="aqi")
        assert len(changes) == 2

        assert changes[0]['city_id'] == c_norm
        assert changes[1]['city_id'] == c_zero
        assert changes[1]['percentage_change'] is None
        assert changes[1]['absolute_change'] == 50.0

    finally:
        connection.rollback()
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE weather_observations, air_quality_observations, cities CASCADE;")
        connection.commit()
        connection.close()
