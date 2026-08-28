import requests

BASE_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"

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

    response = requests.get(
        BASE_URL,
        params=params,
        timeout=10,
    )

    response.raise_for_status()

    return response.json()