import time

import requests

from config.settings import API_MAX_RETRIES, API_TIMEOUT_SECONDS, WEATHER_API_URL


def fetch_weather(latitude: float, longitude: float) -> dict:
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

def fetch_forecast(latitude: float, longitude: float, days: int = 5) -> dict:
    params={
        "latitude": latitude,
        "longitude": longitude,
        "hourly": (
            "temperature_2m,"
            "apparent_temperature,"
            "precipitation_probability,"
            "weather_code"
        ),
        "daily": (
            "weather_code,"
            "temperature_2m_max,"
            "temperature_2m_min,"
            "precipitation_probability_max"
        ),
        "timezone": "auto",
        "forecast_days": days
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

