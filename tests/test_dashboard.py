import pytest
from database.connection import get_connection

def test_get_dashboard_summary():
    from processor.dashboard import get_dashboard_summary
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
            cursor.execute("INSERT INTO weather_observations (city_id, observed_at, temperature_c) VALUES (%s, DATE_TRUNC('hour', CURRENT_TIMESTAMP) - INTERVAL '2 hours' + INTERVAL '10 minutes', %s);", (c1, 20.0))
            cursor.execute("INSERT INTO weather_observations (city_id, observed_at, temperature_c) VALUES (%s, CURRENT_TIMESTAMP - INTERVAL '26 hours', %s);", (c1, 10.0))

            # City 2: latest weather 30C, prev weather 10C
            cursor.execute("INSERT INTO weather_observations (city_id, observed_at, temperature_c) VALUES (%s, CURRENT_TIMESTAMP - INTERVAL '1 hours', %s);", (c2, 30.0))
            cursor.execute("INSERT INTO weather_observations (city_id, observed_at, temperature_c) VALUES (%s, CURRENT_TIMESTAMP - INTERVAL '25 hours', %s);", (c2, 10.0))

            # City 1: latest AQI 100, prev 50
            cursor.execute("INSERT INTO air_quality_observations (city_id, observed_at, us_aqi) VALUES (%s, DATE_TRUNC('hour', CURRENT_TIMESTAMP) - INTERVAL '2 hours' + INTERVAL '10 minutes', %s);", (c1, 100.0))
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
    from processor.dashboard import get_dashboard_map_data
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
    from processor.dashboard import get_time_series_trends
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE weather_observations, air_quality_observations, cities CASCADE;")
            cursor.execute("INSERT INTO cities (name, country, latitude, longitude) VALUES (%s, %s, %s, %s) RETURNING id;", ("Trend City", "Test", 1.0, 1.0))
            c1 = cursor.fetchone()[0]

            # 24h: hourly data (2 observations in same hour should aggregate)
            cursor.execute("INSERT INTO air_quality_observations (city_id, observed_at, us_aqi) VALUES (%s, DATE_TRUNC('hour', CURRENT_TIMESTAMP) - INTERVAL '2 hours' + INTERVAL '10 minutes', %s);", (c1, 100.0))
            cursor.execute("INSERT INTO air_quality_observations (city_id, observed_at, us_aqi) VALUES (%s, DATE_TRUNC('hour', CURRENT_TIMESTAMP) - INTERVAL '2 hours' + INTERVAL '10 minutes' - INTERVAL '10 minutes', %s);", (c1, 150.0))

            # 7d: daily data
            cursor.execute("INSERT INTO weather_observations (city_id, observed_at, temperature_c) VALUES (%s, CURRENT_DATE - INTERVAL '1 days', %s);", (c1, 20.0))
            cursor.execute("INSERT INTO weather_observations (city_id, observed_at, temperature_c) VALUES (%s, CURRENT_DATE - INTERVAL '1 days' + INTERVAL '5 hours', %s);", (c1, 30.0))

        connection.commit()

        # Test 24h AQI
        aqi_24h = get_time_series_trends(connection, c1, metric="aqi", period="24h")['trends']
        assert len(aqi_24h) == 1
        assert aqi_24h[0]['value'] == 125.0
        assert aqi_24h[0]['observation_count'] == 2

        # Test 7d Temperature
        temp_7d = get_time_series_trends(connection, c1, metric="temperature", period="7d")['trends']
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
    from processor.dashboard import get_biggest_changes
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
            cursor.execute("INSERT INTO air_quality_observations (city_id, observed_at, us_aqi) VALUES (%s, DATE_TRUNC('hour', CURRENT_TIMESTAMP) - INTERVAL '2 hours' + INTERVAL '10 minutes', %s);", (c_a, 100.0))

            # City B: prev 100, curr 250 -> +150, +150%
            cursor.execute("INSERT INTO air_quality_observations (city_id, observed_at, us_aqi) VALUES (%s, CURRENT_TIMESTAMP - INTERVAL '26 hours', %s);", (c_b, 100.0))
            cursor.execute("INSERT INTO air_quality_observations (city_id, observed_at, us_aqi) VALUES (%s, DATE_TRUNC('hour', CURRENT_TIMESTAMP) - INTERVAL '2 hours' + INTERVAL '10 minutes', %s);", (c_b, 250.0))

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
    from processor.dashboard import get_city_rankings
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE weather_observations, air_quality_observations, cities CASCADE;")

            cursor.execute("INSERT INTO cities (name, country, latitude, longitude) VALUES (%s, %s, %s, %s) RETURNING id;", ("Rank City 1", "Test", 1.0, 1.0))
            c1 = cursor.fetchone()[0]
            cursor.execute("INSERT INTO cities (name, country, latitude, longitude) VALUES (%s, %s, %s, %s) RETURNING id;", ("Rank City 2", "Test", 2.0, 2.0))
            c2 = cursor.fetchone()[0]

            # City 1 AQI 150
            cursor.execute("INSERT INTO air_quality_observations (city_id, observed_at, us_aqi) VALUES (%s, DATE_TRUNC('hour', CURRENT_TIMESTAMP) - INTERVAL '2 hours' + INTERVAL '10 minutes', %s);", (c1, 150.0))

            # City 2 AQI 100
            cursor.execute("INSERT INTO air_quality_observations (city_id, observed_at, us_aqi) VALUES (%s, DATE_TRUNC('hour', CURRENT_TIMESTAMP) - INTERVAL '2 hours' + INTERVAL '10 minutes', %s);", (c2, 100.0))

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
    from processor.dashboard import get_dashboard_pipeline_status
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
    from processor.dashboard import get_time_series_trends
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
        assert len(temp_24h['trends']) >= 1
        assert any(x['value'] == 20.0 for x in temp_24h['trends'])

        aqi_7d = get_time_series_trends(connection, c1, metric="aqi", period="7d")
        assert len(aqi_7d['trends']) >= 1
        assert any(x['value'] == 100.0 for x in aqi_7d['trends'])

        temp_30d = get_time_series_trends(connection, c1, metric="temperature", period="30d")
        assert len(temp_30d['trends']) >= 1
        assert any(x['value'] == 15.0 for x in temp_30d['trends'])

        aqi_30d = get_time_series_trends(connection, c1, metric="aqi", period="30d")
        assert len(aqi_30d['trends']) >= 1
        assert any(x['value'] == 150.0 for x in aqi_30d['trends'])

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
    from processor.dashboard import get_dashboard_summary
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
    from processor.dashboard import get_biggest_changes
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE weather_observations, air_quality_observations, cities CASCADE;")

            cursor.execute("INSERT INTO cities (name, country, latitude, longitude) VALUES (%s, %s, %s, %s) RETURNING id;", ("Zero City", "Test", 1.0, 1.0))
            c_zero = cursor.fetchone()[0]
            cursor.execute("INSERT INTO cities (name, country, latitude, longitude) VALUES (%s, %s, %s, %s) RETURNING id;", ("Normal City", "Test", 2.0, 2.0))
            c_norm = cursor.fetchone()[0]

            cursor.execute("INSERT INTO air_quality_observations (city_id, observed_at, us_aqi) VALUES (%s, CURRENT_TIMESTAMP - INTERVAL '26 hours', %s);", (c_zero, 0.0))
            cursor.execute("INSERT INTO air_quality_observations (city_id, observed_at, us_aqi) VALUES (%s, DATE_TRUNC('hour', CURRENT_TIMESTAMP) - INTERVAL '2 hours' + INTERVAL '10 minutes', %s);", (c_zero, 50.0))

            cursor.execute("INSERT INTO air_quality_observations (city_id, observed_at, us_aqi) VALUES (%s, CURRENT_TIMESTAMP - INTERVAL '26 hours', %s);", (c_norm, 10.0))
            cursor.execute("INSERT INTO air_quality_observations (city_id, observed_at, us_aqi) VALUES (%s, DATE_TRUNC('hour', CURRENT_TIMESTAMP) - INTERVAL '2 hours' + INTERVAL '10 minutes', %s);", (c_norm, 20.0))

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

def test_get_time_series_trends_empty_db():
    from processor.dashboard import get_time_series_trends
    connection = get_connection()
    try:
        # Just testing it doesn't crash on empty db
        result = get_time_series_trends(connection, city_id=None, metric="aqi", period="24h")
        assert "trends" in result
        assert "completeness" in result

        comp = result["completeness"]
        assert comp["expected_days"] == 1
        assert comp["actual_days"] == 0
        assert comp["completeness"] == 0.0
        assert comp["is_stale"] is True
    finally:
        connection.close()

