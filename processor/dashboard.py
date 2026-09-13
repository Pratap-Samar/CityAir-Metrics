from datetime import datetime, timezone
from .analytics import _calculate_trend

# ============================================================================
# Dashboard analytics
# ============================================================================

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
            c.state,
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
            'state': row[2],
            'country': row[3],
            'latitude': row[4],
            'longitude': row[5],
            'aqi': row[6],
            'pm2_5': row[7],
            'pm10': row[8],
            'temperature_c': row[9],
            'humidity_percent': row[10],
            'wind_speed_kmh': row[11],
            'precipitation_mm': row[12],
            'weather_observed_at': row[13],
            'air_quality_observed_at': row[14],
        })
    return results

def get_time_series_trends(connection, city_id=None, metric="aqi", period="24h"):
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

    expected_days = 1
    if period == "24h":
        start_time = "CURRENT_TIMESTAMP - INTERVAL '24 hours'"
        trunc = "hour"
        expected_days = 1
    elif period == "7d":
        start_time = "CURRENT_DATE - INTERVAL '6 days'"
        trunc = "day"
        expected_days = 7
    elif period == "30d":
        start_time = "CURRENT_DATE - INTERVAL '29 days'"
        trunc = "day"
        expected_days = 30

    city_filter = "AND city_id = %s" if city_id else ""
    params = (city_id,) if city_id else ()

    query = f"""
        SELECT
            DATE_TRUNC('{trunc}', observed_at) AS bucket_time,
            AVG({value_col}) AS bucket_value,
            COUNT({value_col}) AS obs_count
        FROM {table}
        WHERE observed_at >= {start_time}
          {city_filter}
        GROUP BY bucket_time
        ORDER BY bucket_time;
    """

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        rows = cursor.fetchall()

    trends = []
    unique_dates = set()
    for row in rows:
        # If daily, cast back to date
        ts = row[0].date() if trunc == 'day' else row[0]
        if trunc == 'day':
            unique_dates.add(ts)
        else:
            unique_dates.add(row[0].date())

        trends.append({
            'timestamp': ts,
            'value': row[1],
            'observation_count': row[2]
        })

    actual_days = len(unique_dates)
    completeness = (actual_days / expected_days) if expected_days > 0 else 0.0

    is_stale = True
    period_start = None
    period_end = None

    if trends:
        period_start = trends[0]['timestamp']
        period_end = trends[-1]['timestamp']

        last_dt = rows[-1][0]
        if last_dt.tzinfo is None:
            last_dt = last_dt.replace(tzinfo=timezone.utc)

        now = datetime.now(timezone.utc)
        diff_hours = (now - last_dt).total_seconds() / 3600
        if period == "24h":
            is_stale = diff_hours > 2
        else:
            is_stale = diff_hours > 24

    return {
        "trends": trends,
        "completeness": {
            "period_start": period_start,
            "period_end": period_end,
            "expected_days": expected_days,
            "actual_days": actual_days,
            "completeness": round(completeness, 2),
            "is_stale": is_stale
        }
    }

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
            c.state,
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
        GROUP BY c.id, c.name, c.state, c.country
    """

    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    results = []
    for row in rows:
        city_id, name, state, country, val, prev_val = row
        if val is None:
            continue

        change, pct_change, _ = _calculate_trend(prev_val, val)

        results.append({
            'city_id': city_id,
            'name': name,
            'state': state,
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
