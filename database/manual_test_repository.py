from ingestion.models import WeatherObservation
from database.repositories import save_weather_observation


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


observation_id = save_weather_observation(
    observation,
    city_id=1,
)

print("Saved weather observation ID:", observation_id)