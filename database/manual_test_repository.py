from ingestion.models import WeatherObservation
from database.connection import get_connection
from database.repositories import (
    get_or_create_city,
    save_weather_observation,
)

city = {
    "name": "Delhi",
    "country": "India",
    "latitude": 28.6139,
    "longitude": 77.2090,
}

observation = WeatherObservation(
    city="Delhi",
    country="India",
    latitude=28.6139,
    longitude=77.2090,
    observed_at="2026-08-27T13:45",
    temperature_c=32.7,
    humidity_percent=66,
    apparent_temperature_c=38.7,
    precipitation_mm=0.0,
    weather_code=2,
    wind_speed_kmh=7.6,
    wind_direction_degrees=18,
)

connection = get_connection()

try:
    city_id = get_or_create_city(
        city,
        connection,
    )
    
    print("City ID:", city_id)

    observation_id = save_weather_observation(
        observation,
        city_id,
        connection,
    )
    
    print("Saved weather observation ID:", observation_id)

finally:
    connection.close()