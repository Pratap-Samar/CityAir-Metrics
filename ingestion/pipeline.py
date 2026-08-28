from ingestion.cities import CITIES
from ingestion.weather_client import fetch_weather
from ingestion.air_quality_client import fetch_air_quality
from ingestion.transform import (
    transform_weather,
    transform_air_quality,
)


def run_pipeline():

    for city in CITIES:

        latitude = city["latitude"]
        longitude = city["longitude"]

        weather_data = fetch_weather(
            latitude,
            longitude,
        )

        weather_observation = transform_weather(
            city,
            weather_data,
        )

        air_quality_data = fetch_air_quality(
            latitude,
            longitude,
        )

        air_quality_observation = transform_air_quality(
            city,
            air_quality_data,
        )

        print("Weather:")
        print(weather_observation.model_dump())

        print("Air Quality:")
        print(air_quality_observation.model_dump())


if __name__ == "__main__":
    run_pipeline()