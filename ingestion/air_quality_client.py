import time
import requests

from config.settings import AIR_QUALITY_API_URL, API_MAX_RETRIES, API_TIMEOUT_SECONDS


def fetch_air_quality(latitude: float, longitude: float) -> dict:

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": (
            "pm10,"
            "pm2_5,"
            "carbon_monoxide,"
            "nitrogen_dioxide,"
            "sulphur_dioxide,"
            "ozone,"
            "us_aqi"
        ),
        "timezone": "auto",
    }

    for attempt in range(API_MAX_RETRIES):

        try:
            response = requests.get(
                AIR_QUALITY_API_URL,
                params=params,
                timeout=API_TIMEOUT_SECONDS,
            )

            response.raise_for_status()

            return response.json()

        except requests.RequestException:

            if attempt == API_MAX_RETRIES-1:
                raise

            time.sleep(2)