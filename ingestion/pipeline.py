import logging 

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

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

def run_pipeline():
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
                
            except Exception:
                connection.rollback()
                logger.exception(f"City ingestion failed: city={city['name']}")
    finally:
        connection.close()

if __name__ == "__main__":
    run_pipeline()