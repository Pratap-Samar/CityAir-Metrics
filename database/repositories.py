from database.connection import get_connection

def save_city(city):
    connection = get_connection()

    try:
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

    finally:
        connection.close()


def save_weather_observation(observation,city_id):
    connection = get_connection()

    try:
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

    finally:
        connection.close()

def save_air_quality_observation(observation, city_id):
    connection = get_connection()

    try:
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

    finally:
        connection.close()