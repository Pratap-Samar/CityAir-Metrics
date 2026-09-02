import logging 
import time

from database.connection import get_connection
from ingestion.cities import CITIES
from ingestion.weather_client import fetch_weather
from ingestion.air_quality_client import fetch_air_quality
from ingestion.transform import (
    transform_weather,
    transform_air_quality,
)
from database.repositories import (
    get_or_create_city,
    save_weather_observation,
    save_air_quality_observation,
)
from ingestion.validation import (
    validate_weather_freshness,
    validate_air_quality_freshness,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

def run_pipeline():
    start_time = time.time()
    cities_processed = 0
    cities_failed = 0

    connection = get_connection()

    try:
        for city in CITIES:
            try:
                latitude = city["latitude"]
                longitude = city["longitude"]

                city_id = get_or_create_city(
                    city,
                    connection,
                )

                weather_data = fetch_weather(
                    latitude,
                    longitude,
                )

                weather_observation = transform_weather(
                    city,
                    weather_data,
                )

                validate_weather_freshness(weather_observation)

                weather_id = save_weather_observation(
                    weather_observation,
                    city_id,
                    connection,
                )

                air_quality_data = fetch_air_quality(
                    latitude,
                    longitude,
                )

                air_quality_observation = transform_air_quality(
                    city,
                    air_quality_data,
                )

                validate_air_quality_freshness(air_quality_observation)

                air_quality_id = save_air_quality_observation(
                    air_quality_observation,
                    city_id,
                    connection,
                )

                logger.info(
                    "City ingestion successful: "
                    f"city={city['name']}, "
                    f"weather_id={weather_id}, "
                    f"air_quality_id={air_quality_id}"
                )

                cities_processed += 1

            except Exception:
                connection.rollback()
                cities_failed += 1

                logger.exception(
                    f"City ingestion failed: city={city['name']}"
                )

        duration = time.time() - start_time

        logger.info(
            "Pipeline run completed: "
            f"processed={cities_processed}, "
            f"failed={cities_failed}, "
            f"duration_seconds={duration:.2f}"
        )

    finally:
        connection.close()

if __name__ == "__main__":
    run_pipeline()