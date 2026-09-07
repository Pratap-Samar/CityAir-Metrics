from datetime import datetime, timezone

# ============================================================================
# Constants
# ============================================================================

VALID_HISTORY_PERIODS = {"24h", "7d", "30d"}
VALID_HISTORY_METRICS = {"weather", "air_quality"}


# ============================================================================
# Validation helpers
# ============================================================================


def _validate_history_period(period):
    if period not in VALID_HISTORY_PERIODS:
        raise ValueError(
            f"Unsupported history period: {period}. "
            f"Expected one of: {sorted(VALID_HISTORY_PERIODS)}"
        )


def _validate_history_metric(metric):
    if metric not in VALID_HISTORY_METRICS:
        raise ValueError(
            f"Unsupported history metric: {metric}. "
            f"Expected one of: {sorted(VALID_HISTORY_METRICS)}"
        )


# ============================================================================
# Trend helpers
# ============================================================================

def _calculate_trend(previous_average, recent_average):
    if previous_average is None or recent_average is None:
        return None, None, None

    change = recent_average - previous_average

    if previous_average == 0:
        percentage_change = None
    else:
        percentage_change = (
            change / abs(previous_average)
        ) * 100

    if percentage_change is None:
        direction = "increasing" if change > 0 else (
            "decreasing" if change < 0 else "stable"
        )
    elif percentage_change > 2:
        direction = "increasing"
    elif percentage_change < -2:
        direction = "decreasing"
    else:
        direction = "stable"

    return change, percentage_change, direction


# ============================================================================
# Latest / current-state analytics
# ============================================================================


def get_latest_weather_by_city(connection):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                c.id AS city_id,
                c.name,
                c.country,
                w.observed_at,
                w.temperature_c,
                w.humidity_percent,
                w.apparent_temperature_c,
                w.precipitation_mm,
                w.weather_code,
                w.wind_speed_kmh,
                w.wind_direction_degrees
            FROM cities c
            JOIN LATERAL (
                SELECT
                    observed_at,
                    temperature_c,
                    humidity_percent,
                    apparent_temperature_c,
                    precipitation_mm,
                    weather_code,
                    wind_speed_kmh,
                    wind_direction_degrees
                FROM weather_observations
                WHERE city_id = c.id
                ORDER BY observed_at DESC
                LIMIT 1
            ) w ON TRUE
            ORDER BY c.name;
            """
        )

        return cursor.fetchall()


def get_latest_air_quality_by_city(connection):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                c.id AS city_id,
                c.name,
                c.country,
                a.observed_at,
                a.pm10,
                a.pm2_5,
                a.carbon_monoxide,
                a.nitrogen_dioxide,
                a.sulphur_dioxide,
                a.ozone,
                a.us_aqi
            FROM cities c
            JOIN LATERAL (
                SELECT
                    observed_at,
                    pm10,
                    pm2_5,
                    carbon_monoxide,
                    nitrogen_dioxide,
                    sulphur_dioxide,
                    ozone,
                    us_aqi
                FROM air_quality_observations
                WHERE city_id = c.id
                ORDER BY observed_at DESC
                LIMIT 1
            ) a ON TRUE
            ORDER BY c.name;
            """
        )

        return cursor.fetchall()


def get_latest_city_snapshot(connection):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                c.id AS city_id,
                c.name,
                c.country,

                w.observed_at AS weather_observed_at,
                w.temperature_c,
                w.humidity_percent,
                w.apparent_temperature_c,
                w.precipitation_mm,
                w.weather_code,
                w.wind_speed_kmh,
                w.wind_direction_degrees,

                a.observed_at AS air_quality_observed_at,
                a.pm10,
                a.pm2_5,
                a.carbon_monoxide,
                a.nitrogen_dioxide,
                a.sulphur_dioxide,
                a.ozone,
                a.us_aqi

            FROM cities c

            LEFT JOIN LATERAL (
                SELECT
                    observed_at,
                    temperature_c,
                    humidity_percent,
                    apparent_temperature_c,
                    precipitation_mm,
                    weather_code,
                    wind_speed_kmh,
                    wind_direction_degrees
                FROM weather_observations
                WHERE city_id = c.id
                ORDER BY observed_at DESC
                LIMIT 1
            ) w ON TRUE

            LEFT JOIN LATERAL (
                SELECT
                    observed_at,
                    pm10,
                    pm2_5,
                    carbon_monoxide,
                    nitrogen_dioxide,
                    sulphur_dioxide,
                    ozone,
                    us_aqi
                FROM air_quality_observations
                WHERE city_id = c.id
                ORDER BY observed_at DESC
                LIMIT 1
            ) a ON TRUE

            ORDER BY c.name;
            """
        )

        return cursor.fetchall()


# ============================================================================
# Aggregate analytics
# ============================================================================


def get_average_weather_by_city(connection, hours=24):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                c.id AS city_id,
                c.name,
                c.country,
                AVG(w.temperature_c) AS avg_temperature_c,
                AVG(w.humidity_percent) AS avg_humidity_percent,
                AVG(w.apparent_temperature_c) AS avg_apparent_temperature_c,
                AVG(w.precipitation_mm) AS avg_precipitation_mm,
                AVG(w.wind_speed_kmh) AS avg_wind_speed_kmh
            FROM cities c
            JOIN weather_observations w
                ON w.city_id = c.id
            WHERE w.observed_at >= NOW() - (%s * INTERVAL '1 hour')
            GROUP BY
                c.id,
                c.name,
                c.country
            ORDER BY c.name;
            """,
            (hours,),
        )

        return cursor.fetchall()


def get_average_air_quality_by_city(connection, hours=24):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                c.id AS city_id,
                c.name,
                c.country,
                AVG(a.pm10) AS avg_pm10,
                AVG(a.pm2_5) AS avg_pm2_5,
                AVG(a.carbon_monoxide) AS avg_carbon_monoxide,
                AVG(a.nitrogen_dioxide) AS avg_nitrogen_dioxide,
                AVG(a.sulphur_dioxide) AS avg_sulphur_dioxide,
                AVG(a.ozone) AS avg_ozone,
                AVG(a.us_aqi) AS avg_us_aqi
            FROM cities c
            JOIN air_quality_observations a
                ON a.city_id = c.id
            WHERE a.observed_at >= NOW() - (%s * INTERVAL '1 hour')
            GROUP BY
                c.id,
                c.name,
                c.country
            ORDER BY c.name;
            """,
            (hours,),
        )

        return cursor.fetchall()


# ============================================================================
# Historical analytics
# ============================================================================


def get_weather_history_by_city(connection, city_id, hours=24):
    """
    Return raw weather observations for the requested number of hours.
    Used for hourly history such as the 24h view.
    """

    if hours < 1:
        raise ValueError("hours must be at least 1")

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                observed_at,
                temperature_c,
                humidity_percent,
                apparent_temperature_c,
                precipitation_mm,
                wind_speed_kmh
            FROM weather_observations
            WHERE city_id = %s
              AND observed_at >= NOW() - (%s * INTERVAL '1 hour')
            ORDER BY observed_at;
            """,
            (city_id, hours),
        )

        return cursor.fetchall()


def get_air_quality_history_by_city(connection, city_id, hours=24):
    """
    Return raw air-quality observations for the requested number of hours.
    Used for hourly history such as the 24h view.
    """

    if hours < 1:
        raise ValueError("hours must be at least 1")

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                observed_at,
                pm10,
                pm2_5,
                carbon_monoxide,
                nitrogen_dioxide,
                sulphur_dioxide,
                ozone,
                us_aqi
            FROM air_quality_observations
            WHERE city_id = %s
              AND observed_at >= NOW() - (%s * INTERVAL '1 hour')
            ORDER BY observed_at;
            """,
            (city_id, hours),
        )

        return cursor.fetchall()


def get_daily_weather_history_by_city(connection, city_id, days=7):
    """
    Return daily weather aggregates for the requested number of
    calendar days.
    """

    if days < 1:
        raise ValueError("days must be at least 1")

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                DATE(observed_at) AS observation_date,
                AVG(temperature_c) AS average_temperature_c,
                MIN(temperature_c) AS minimum_temperature_c,
                MAX(temperature_c) AS maximum_temperature_c,
                AVG(humidity_percent) AS average_humidity_percent,
                AVG(apparent_temperature_c) AS average_apparent_temperature_c,
                SUM(precipitation_mm) AS total_precipitation_mm,
                AVG(wind_speed_kmh) AS average_wind_speed_kmh
            FROM weather_observations
            WHERE city_id = %s
              AND observed_at >= CURRENT_DATE
                  - ((%s - 1) * INTERVAL '1 day')
            GROUP BY DATE(observed_at)
            ORDER BY observation_date;
            """,
            (city_id, days),
        )

        return cursor.fetchall()


def get_daily_air_quality_history_by_city(connection, city_id, days=7):
    """
    Return daily air-quality aggregates for the requested number of
    calendar days.
    """

    if days < 1:
        raise ValueError("days must be at least 1")

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                DATE(observed_at) AS observation_date,
                AVG(pm10) AS average_pm10,
                MAX(pm10) AS maximum_pm10,
                AVG(pm2_5) AS average_pm2_5,
                MAX(pm2_5) AS maximum_pm2_5,
                AVG(carbon_monoxide) AS average_carbon_monoxide,
                AVG(nitrogen_dioxide) AS average_nitrogen_dioxide,
                AVG(sulphur_dioxide) AS average_sulphur_dioxide,
                AVG(ozone) AS average_ozone,
                AVG(us_aqi) AS average_us_aqi,
                MAX(us_aqi) AS maximum_us_aqi
            FROM air_quality_observations
            WHERE city_id = %s
              AND observed_at >= CURRENT_DATE
                  - ((%s - 1) * INTERVAL '1 day')
            GROUP BY DATE(observed_at)
            ORDER BY observation_date;
            """,
            (city_id, days),
        )

        return cursor.fetchall()


def get_history_by_city(
    connection,
    city_id,
    metric,
    period="24h",
):
    """
    Unified history interface.

    Metrics:
        weather
        air_quality

    Periods:
        24h
        7d
        30d

    24h returns raw/hourly observations.

    7d and 30d return daily aggregates.
    """

    _validate_history_metric(metric)
    _validate_history_period(period)

    if metric == "weather":
        if period == "24h":
            return get_weather_history_by_city(
                connection,
                city_id,
                hours=24,
            )

        days = 7 if period == "7d" else 30

        return get_daily_weather_history_by_city(
            connection,
            city_id,
            days=days,
        )

    if period == "24h":
        return get_air_quality_history_by_city(
            connection,
            city_id,
            hours=24,
        )

    days = 7 if period == "7d" else 30

    return get_daily_air_quality_history_by_city(
        connection,
        city_id,
        days=days,
    )


# ============================================================================
# Trend analytics
# ============================================================================


def get_temperature_trend_by_city(connection, period="24h"):
    _validate_history_period(period)

    if period == "24h":
        current_start = "CURRENT_TIMESTAMP - INTERVAL '24 hours'"
        previous_start = "CURRENT_TIMESTAMP - INTERVAL '48 hours'"
        previous_end = "CURRENT_TIMESTAMP - INTERVAL '24 hours'"
    elif period == "7d":
        current_start = "CURRENT_DATE - INTERVAL '6 days'"
        previous_start = "CURRENT_DATE - INTERVAL '13 days'"
        previous_end = "CURRENT_DATE - INTERVAL '7 days'"
    else:
        current_start = "CURRENT_DATE - INTERVAL '29 days'"
        previous_start = "CURRENT_DATE - INTERVAL '59 days'"
        previous_end = "CURRENT_DATE - INTERVAL '30 days'"

    query = f"""
        SELECT
            c.id AS city_id,
            c.name,
            c.country,
            AVG(
                CASE
                    WHEN w.observed_at >= {previous_start}
                     AND w.observed_at < {previous_end}
                    THEN w.temperature_c
                END
            ) AS previous_average,
            AVG(
                CASE
                    WHEN w.observed_at >= {current_start}
                    THEN w.temperature_c
                END
            ) AS recent_average,
            COUNT(
                CASE
                    WHEN w.observed_at >= {previous_start}
                     AND w.observed_at < {previous_end}
                    THEN w.temperature_c
                END
            ) AS previous_observation_count,
            COUNT(
                CASE
                    WHEN w.observed_at >= {current_start}
                    THEN w.temperature_c
                END
            ) AS recent_observation_count
        FROM cities c
        LEFT JOIN weather_observations w
            ON w.city_id = c.id
            AND w.observed_at >= {previous_start}
        GROUP BY c.id, c.name, c.country
        ORDER BY c.name;
    """

    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    results = []

    for row in rows:
        (
            city_id,
            name,
            country,
            previous_average,
            recent_average,
            previous_observation_count,
            recent_observation_count,
        ) = row

        change, percentage_change, direction = _calculate_trend(
            previous_average,
            recent_average,
        )

        results.append(
            (
                city_id,
                name,
                country,
                previous_average,
                recent_average,
                change,
                percentage_change,
                direction,
                previous_observation_count,
                recent_observation_count,
            )
        )

    return results


def get_pm25_trend_by_city(connection, period="24h"):
    _validate_history_period(period)

    if period == "24h":
        current_start = "CURRENT_TIMESTAMP - INTERVAL '24 hours'"
        previous_start = "CURRENT_TIMESTAMP - INTERVAL '48 hours'"
        previous_end = "CURRENT_TIMESTAMP - INTERVAL '24 hours'"
    elif period == "7d":
        current_start = "CURRENT_DATE - INTERVAL '6 days'"
        previous_start = "CURRENT_DATE - INTERVAL '13 days'"
        previous_end = "CURRENT_DATE - INTERVAL '7 days'"
    else:
        current_start = "CURRENT_DATE - INTERVAL '29 days'"
        previous_start = "CURRENT_DATE - INTERVAL '59 days'"
        previous_end = "CURRENT_DATE - INTERVAL '30 days'"

    query = f"""
        SELECT
            c.id AS city_id,
            c.name,
            c.country,
            AVG(
                CASE
                    WHEN aq.observed_at >= {previous_start}
                     AND aq.observed_at < {previous_end}
                    THEN aq.pm2_5
                END
            ) AS previous_average,
            AVG(
                CASE
                    WHEN aq.observed_at >= {current_start}
                    THEN aq.pm2_5
                END
            ) AS recent_average,
            COUNT(
                CASE
                    WHEN aq.observed_at >= {previous_start}
                     AND aq.observed_at < {previous_end}
                    THEN aq.pm2_5
                END
            ) AS previous_observation_count,
            COUNT(
                CASE
                    WHEN aq.observed_at >= {current_start}
                    THEN aq.pm2_5
                END
            ) AS recent_observation_count
        FROM cities c
        LEFT JOIN air_quality_observations aq
            ON aq.city_id = c.id
            AND aq.observed_at >= {previous_start}
        GROUP BY c.id, c.name, c.country
        ORDER BY c.name;
    """

    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    results = []

    for row in rows:
        (
            city_id,
            name,
            country,
            previous_average,
            recent_average,
            previous_observation_count,
            recent_observation_count,
        ) = row

        change, percentage_change, direction = _calculate_trend(
            previous_average,
            recent_average,
        )

        results.append(
            (
                city_id,
                name,
                country,
                previous_average,
                recent_average,
                change,
                percentage_change,
                direction,
                previous_observation_count,
                recent_observation_count,
            )
        )

    return results

def get_dashboard_summary(connection):
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(id) FROM cities;")
        total_cities = cursor.fetchone()[0] or 0

        # Current weather (latest per city)
        cursor.execute("""
            SELECT AVG(temperature_c), MAX(observed_at)
            FROM (
                SELECT temperature_c, observed_at,
                       ROW_NUMBER() OVER(PARTITION BY city_id ORDER BY observed_at DESC) as rn
                FROM weather_observations
                WHERE temperature_c IS NOT NULL
            ) latest
            WHERE rn = 1
        """)
        w_row = cursor.fetchone()
        avg_temp = w_row[0] if w_row else None
        last_weather_at = w_row[1] if w_row else None

        # Previous weather (average of city averages 24-48h ago)
        cursor.execute("""
            SELECT AVG(city_avg)
            FROM (
                SELECT AVG(temperature_c) as city_avg
                FROM weather_observations
                WHERE observed_at >= NOW() - INTERVAL '48 hours'
                  AND observed_at < NOW() - INTERVAL '24 hours'
                GROUP BY city_id
            ) sub
        """)
        prev_temp_row = cursor.fetchone()
        prev_avg_temp = prev_temp_row[0] if prev_temp_row else None

        # Current AQI (latest per city)
        cursor.execute("""
            SELECT AVG(us_aqi), MAX(observed_at)
            FROM (
                SELECT us_aqi, observed_at,
                       ROW_NUMBER() OVER(PARTITION BY city_id ORDER BY observed_at DESC) as rn
                FROM air_quality_observations
                WHERE us_aqi IS NOT NULL
            ) latest
            WHERE rn = 1
        """)
        aq_row = cursor.fetchone()
        avg_aqi = aq_row[0] if aq_row else None
        last_aq_at = aq_row[1] if aq_row else None

        # Previous AQI
        cursor.execute("""
            SELECT AVG(city_avg)
            FROM (
                SELECT AVG(us_aqi) as city_avg
                FROM air_quality_observations
                WHERE observed_at >= NOW() - INTERVAL '48 hours'
                  AND observed_at < NOW() - INTERVAL '24 hours'
                GROUP BY city_id
            ) sub
        """)
        prev_aq_row = cursor.fetchone()
        prev_avg_aqi = prev_aq_row[0] if prev_aq_row else None

    aqi_abs, aqi_pct, aqi_dir = _calculate_trend(prev_avg_aqi, avg_aqi)
    temp_abs, temp_pct, temp_dir = _calculate_trend(prev_avg_temp, avg_temp)

    now = datetime.now(timezone.utc)

    def get_freshness(obs_time):
        if not obs_time:
            return None
        if obs_time.tzinfo is None:
            obs_time = obs_time.replace(tzinfo=timezone.utc)
        diff = now - obs_time
        return max(0, int(diff.total_seconds() / 60))

    w_fresh = get_freshness(last_weather_at)
    aq_fresh = get_freshness(last_aq_at)

    obs_times = [t for t in (last_weather_at, last_aq_at) if t]
    last_obs_at = max(obs_times) if obs_times else None
    data_fresh = get_freshness(last_obs_at)

    return {
        'total_cities': total_cities,
        'average_aqi': avg_aqi,
        'previous_period_aqi': prev_avg_aqi,
        'aqi_absolute_change': aqi_abs,
        'aqi_percentage_change': aqi_pct,
        'aqi_direction': aqi_dir,
        'average_temperature_c': avg_temp,
        'previous_period_temperature_c': prev_avg_temp,
        'temperature_absolute_change': temp_abs,
        'temperature_percentage_change': temp_pct,
        'temperature_direction': temp_dir,
        'last_observation_at': last_obs_at,
        'weather_freshness_minutes': w_fresh,
        'air_quality_freshness_minutes': aq_fresh,
        'data_freshness_minutes': data_fresh,
    }

def get_dashboard_map_data(connection):
    query = """
        SELECT
            c.id AS city_id,
            c.name AS city_name,
            c.country,
            c.latitude,
            c.longitude,
            a.us_aqi AS aqi,
            a.pm2_5,
            a.pm10,
            w.temperature_c,
            w.humidity_percent,
            w.wind_speed_kmh,
            w.precipitation_mm,
            w.observed_at AS weather_observed_at,
            a.observed_at AS air_quality_observed_at
        FROM cities c
        LEFT JOIN LATERAL (
            SELECT
                observed_at,
                temperature_c,
                humidity_percent,
                wind_speed_kmh,
                precipitation_mm
            FROM weather_observations
            WHERE city_id = c.id
            ORDER BY observed_at DESC
            LIMIT 1
        ) w ON TRUE
        LEFT JOIN LATERAL (
            SELECT
                observed_at,
                us_aqi,
                pm2_5,
                pm10
            FROM air_quality_observations
            WHERE city_id = c.id
            ORDER BY observed_at DESC
            LIMIT 1
        ) a ON TRUE
        ORDER BY c.name;
    """
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    results = []
    for row in rows:
        results.append({
            'city_id': row[0],
            'city_name': row[1],
            'country': row[2],
            'latitude': row[3],
            'longitude': row[4],
            'aqi': row[5],
            'pm2_5': row[6],
            'pm10': row[7],
            'temperature_c': row[8],
            'humidity_percent': row[9],
            'wind_speed_kmh': row[10],
            'precipitation_mm': row[11],
            'weather_observed_at': row[12],
            'air_quality_observed_at': row[13],
        })
    return results

def get_time_series_trends(connection, city_id, metric="aqi", period="24h"):
    if metric not in ("aqi", "temperature"):
        raise ValueError("Unsupported metric")
    if period not in ("24h", "7d", "30d"):
        raise ValueError("Unsupported period")

    if metric == "aqi":
        table = "air_quality_observations"
        value_col = "us_aqi"
    else:
        table = "weather_observations"
        value_col = "temperature_c"

    if period == "24h":
        start_time = "CURRENT_TIMESTAMP - INTERVAL '24 hours'"
        trunc = "hour"
    elif period == "7d":
        start_time = "CURRENT_DATE - INTERVAL '6 days'"
        trunc = "day"
    elif period == "30d":
        start_time = "CURRENT_DATE - INTERVAL '29 days'"
        trunc = "day"

    query = f"""
        SELECT
            DATE_TRUNC('{trunc}', observed_at) AS bucket_time,
            AVG({value_col}) AS bucket_value,
            COUNT({value_col}) AS obs_count
        FROM {table}
        WHERE city_id = %s
          AND observed_at >= {start_time}
        GROUP BY bucket_time
        ORDER BY bucket_time;
    """

    with connection.cursor() as cursor:
        cursor.execute(query, (city_id,))
        rows = cursor.fetchall()

    results = []
    for row in rows:
        # If daily, cast back to date
        ts = row[0].date() if trunc == 'day' else row[0]
        results.append({
            'timestamp': ts,
            'value': row[1],
            'observation_count': row[2]
        })
    return results

def get_biggest_changes(connection, metric="aqi"):
    if metric != "aqi":
        raise ValueError("Unsupported metric for biggest changes")

    query = """
        SELECT
            c.id AS city_id,
            c.name,
            AVG(
                CASE
                    WHEN a.observed_at >= CURRENT_TIMESTAMP - INTERVAL '48 hours'
                     AND a.observed_at < CURRENT_TIMESTAMP - INTERVAL '24 hours'
                    THEN a.us_aqi
                END
            ) AS previous_average,
            AVG(
                CASE
                    WHEN a.observed_at >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
                    THEN a.us_aqi
                END
            ) AS current_average
        FROM cities c
        LEFT JOIN air_quality_observations a
            ON a.city_id = c.id
            AND a.observed_at >= CURRENT_TIMESTAMP - INTERVAL '48 hours'
        GROUP BY c.id, c.name
    """

    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    results = []
    for row in rows:
        city_id, name, prev_avg, curr_avg = row
        if prev_avg is None and curr_avg is None:
            continue

        change, pct_change, direction = _calculate_trend(prev_avg, curr_avg)
        if change is None:
            continue

        results.append({
            'city_id': city_id,
            'name': name,
            'previous_average': prev_avg,
            'current_average': curr_avg,
            'absolute_change': change,
            'percentage_change': pct_change,
            'direction': direction
        })

    def sort_key(item):
        pct = item['percentage_change']
        abs_val = item['absolute_change']
        sort_pct = -abs(pct) if pct is not None else float('inf')
        sort_abs = -abs(abs_val) if abs_val is not None else float('inf')
        return (sort_pct, sort_abs)

    results.sort(key=sort_key)
    return results

def get_city_rankings(connection, metric="aqi", period="24h"):
    if metric not in ("aqi", "pm2_5", "pm10"):
        raise ValueError("Unsupported ranking metric")
    if period not in ("24h", "7d", "30d"):
        raise ValueError("Unsupported ranking period")

    if metric == "aqi":
        value_col = "us_aqi"
    else:
        value_col = metric

    if period == "24h":
        curr_start = "CURRENT_TIMESTAMP - INTERVAL '24 hours'"
        prev_start = "CURRENT_TIMESTAMP - INTERVAL '48 hours'"
        prev_end = "CURRENT_TIMESTAMP - INTERVAL '24 hours'"
    elif period == "7d":
        curr_start = "CURRENT_DATE - INTERVAL '6 days'"
        prev_start = "CURRENT_DATE - INTERVAL '13 days'"
        prev_end = "CURRENT_DATE - INTERVAL '7 days'"
    elif period == "30d":
        curr_start = "CURRENT_DATE - INTERVAL '29 days'"
        prev_start = "CURRENT_DATE - INTERVAL '59 days'"
        prev_end = "CURRENT_DATE - INTERVAL '30 days'"

    query = f"""
        SELECT
            c.id AS city_id,
            c.name,
            c.country,
            AVG(
                CASE
                    WHEN a.observed_at >= {curr_start}
                    THEN a.{value_col}
                END
            ) AS value,
            AVG(
                CASE
                    WHEN a.observed_at >= {prev_start}
                     AND a.observed_at < {prev_end}
                    THEN a.{value_col}
                END
            ) AS previous_value
        FROM cities c
        LEFT JOIN air_quality_observations a
            ON a.city_id = c.id
            AND a.observed_at >= {prev_start}
        GROUP BY c.id, c.name, c.country
    """

    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    results = []
    for row in rows:
        city_id, name, country, val, prev_val = row
        if val is None:
            continue

        change, pct_change, _ = _calculate_trend(prev_val, val)

        results.append({
            'city_id': city_id,
            'name': name,
            'country': country,
            'value': val,
            'previous_value': prev_val,
            'change': change,
            'percentage_change': pct_change
        })

    results.sort(key=lambda x: x['value'], reverse=True)
    return results

def get_dashboard_pipeline_status(connection):
    query = """
        SELECT
            status,
            started_at,
            completed_at,
            duration_seconds,
            cities_processed,
            cities_failed,
            error_message
        FROM pipeline_runs
        ORDER BY started_at DESC
        LIMIT 1
    """
    with connection.cursor() as cursor:
        cursor.execute(query)
        row = cursor.fetchone()

    if not row:
        return None

    return {
        'status': row[0],
        'started_at': row[1],
        'completed_at': row[2],
        'duration_seconds': row[3],
        'cities_processed': row[4],
        'cities_failed': row[5],
        'error_message': row[6]
    }
