import requests

BASE_URL = "https://api.open-meteo.com/v1/forecast"

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

    response = requests.get(
        BASE_URL,
        params=params,
        timeout=10
    )
    response.raise_for_status()

    return response.json()

