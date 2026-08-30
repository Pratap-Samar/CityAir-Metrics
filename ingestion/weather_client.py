import time
import requests

from config.settings import WEATHER_API_URL, API_MAX_RETRIES, API_TIMEOUT_SECONDS


def fetch_weather(latitude: float,longitude: float) -> dict:
    params={
        "latitude" : latitude,
        "longitude" : longitude,
        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "apparent_temperature,"
            "precipitation,"
            "weather_code,"
            "wind_speed_10m,"
            "wind_direction_10m"
       ),
       "timezone" : "auto"
    }

    for attempt in range(API_MAX_RETRIES):

        try:
            response = requests.get(
                WEATHER_API_URL,
                params=params,
                timeout=API_TIMEOUT_SECONDS
            )

            response.raise_for_status()

            return response.json()

        except requests.RequestException:
            if attempt == API_MAX_RETRIES-1:
                raise
            
            time.sleep(2)
