from ingestion.models import AirQualityObservation
from database.repositories import (
    get_or_create_city,
    save_air_quality_observation,
)


city = {
    "name": "Delhi",
    "country": "India",
    "latitude": 28.6139,
    "longitude": 77.2090,
}


city_id = get_or_create_city(city)


observation = AirQualityObservation(
    city="Delhi",
    country="India",
    latitude=28.6139,
    longitude=77.2090,
    observed_at="2026-08-27T13:30",
    pm10=91.5,
    pm2_5=67.3,
    carbon_monoxide=395.0,
    nitrogen_dioxide=13.9,
    sulphur_dioxide=47.0,
    ozone=277.0,
    us_aqi=171,
)


observation_id = save_air_quality_observation(
    observation,
    city_id=city_id,
)


print("City ID:", city_id)
print("Saved air quality observation ID:", observation_id)