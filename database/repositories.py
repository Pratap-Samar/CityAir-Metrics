def get_or_create_city(city, connection):

    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO cities (
                name,
                country,
                latitude,
                longitude
            )
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (name, country)
            DO UPDATE SET
                latitude = EXCLUDED.latitude,
                longitude = EXCLUDED.longitude
            RETURNING id;
            """,
            (
                city["name"],
                city["country"],
                city["latitude"],
                city["longitude"],
            ),
        )

        city_id = cursor.fetchone()[0]

    connection.commit()

    return city_id


def save_weather_observation(
    observation,
    city_id,
    connection,
):

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
            VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (city_id, observed_at)
            DO UPDATE SET
                temperature_c = EXCLUDED.temperature_c,
                humidity_percent = EXCLUDED.humidity_percent,
                apparent_temperature_c = EXCLUDED.apparent_temperature_c,
                precipitation_mm = EXCLUDED.precipitation_mm,
                weather_code = EXCLUDED.weather_code,
                wind_speed_kmh = EXCLUDED.wind_speed_kmh,
                wind_direction_degrees = EXCLUDED.wind_direction_degrees
            RETURNING id;
            """,
            (
                city_id,
                observation.observed_at,
                observation.temperature_c,
                observation.humidity_percent,
                observation.apparent_temperature_c,
                observation.precipitation_mm,
                observation.weather_code,
                observation.wind_speed_kmh,
                observation.wind_direction_degrees,
            ),
        )

        observation_id = cursor.fetchone()[0]

    connection.commit()

    return observation_id


def save_air_quality_observation(
    observation,
    city_id,
    connection,
):

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
            VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (city_id, observed_at)
            DO UPDATE SET
                pm10 = EXCLUDED.pm10,
                pm2_5 = EXCLUDED.pm2_5,
                carbon_monoxide = EXCLUDED.carbon_monoxide,
                nitrogen_dioxide = EXCLUDED.nitrogen_dioxide,
                sulphur_dioxide = EXCLUDED.sulphur_dioxide,
                ozone = EXCLUDED.ozone,
                us_aqi = EXCLUDED.us_aqi
            RETURNING id;
            """,
            (
                city_id,
                observation.observed_at,
                observation.pm10,
                observation.pm2_5,
                observation.carbon_monoxide,
                observation.nitrogen_dioxide,
                observation.sulphur_dioxide,
                observation.ozone,
                observation.us_aqi,
            ),
        )

        observation_id = cursor.fetchone()[0]

    connection.commit()

    return observation_id

def create_pipeline_run(started_at, connection):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO pipeline_runs (
                started_at,
                status
            )
            VALUES (%s, %s)
            RETURNING id;
            """,
            (
                started_at,
                "RUNNING",
            ),
        )
        run_id = cursor.fetchone()[0]

    connection.commit()
    return run_id

def complete_pipeline_run(
    run_id,
    completed_at,
    status,
    cities_processed,
    cities_failed,
    duration_seconds,
    connection,
    error_message=None,
):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            UPDATE pipeline_runs
            SET
                completed_at = %s,
                status = %s,
                cities_processed = %s,
                cities_failed = %s,
                duration_seconds = %s,
                error_message = %s
            WHERE id = %s;
            """,
            (
                completed_at,
                status,
                cities_processed,
                cities_failed,
                duration_seconds,
                error_message,
                run_id,
            ),
        )

    connection.commit()