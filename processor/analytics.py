def _calculate_trend(previous_average, recent_average):
    if previous_average is None or recent_average is None:
        return None, None

    change = recent_average - previous_average

    if change > 0:
        direction = "increasing"
    elif change < 0:
        direction = "decreasing"
    else:
        direction = "stable"

    return change, direction


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


def get_temperature_trend_by_city(connection, hours=24):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                c.id AS city_id,
                c.name,
                c.country,
                AVG(
                    CASE
                        WHEN w.observed_at >= NOW() - (%s * INTERVAL '1 hour')
                        AND w.observed_at < NOW() - ((%s / 2) * INTERVAL '1 hour')
                        THEN w.temperature_c
                    END
                ) AS previous_average_temperature_c,
                AVG(
                    CASE
                        WHEN w.observed_at >= NOW() - ((%s / 2) * INTERVAL '1 hour')
                        THEN w.temperature_c
                    END
                ) AS recent_average_temperature_c
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
            (hours, hours, hours, hours),
        )

        rows = cursor.fetchall()
        results = []

        for row in rows:
            previous_average = row[3]
            recent_average = row[4]

            change, direction = _calculate_trend(
                previous_average,
                recent_average,
            )

            results.append(
                (
                    row[0],
                    row[1],
                    row[2],
                    previous_average,
                    recent_average,
                    change,
                    direction,
                )
            )

        return results


def get_pm25_trend_by_city(connection, hours=24):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                c.id AS city_id,
                c.name,
                c.country,
                AVG(
                    CASE
                        WHEN a.observed_at >= NOW() - (%s * INTERVAL '1 hour')
                        AND a.observed_at < NOW() - ((%s / 2) * INTERVAL '1 hour')
                        THEN a.pm2_5
                    END
                ) AS previous_average_pm2_5,
                AVG(
                    CASE
                        WHEN a.observed_at >= NOW() - ((%s / 2) * INTERVAL '1 hour')
                        THEN a.pm2_5
                    END
                ) AS recent_average_pm2_5
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
            (hours, hours, hours, hours),
        )

        rows = cursor.fetchall()
        results = []

        for row in rows:
            previous_average = row[3]
            recent_average = row[4]

            change, direction = _calculate_trend(
                previous_average,
                recent_average,
            )

            results.append(
                (
                    row[0],
                    row[1],
                    row[2],
                    previous_average,
                    recent_average,
                    change,
                    direction,
                )
            )

        return results

    
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

