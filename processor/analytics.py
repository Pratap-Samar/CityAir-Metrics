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