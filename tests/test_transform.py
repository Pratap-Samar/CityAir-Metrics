from ingestion.transform import transform_weather


def test_transform_weather():

    city = {
        "name": "Delhi",
        "country": "India",
        "latitude": 28.6139,
        "longitude": 77.2090,
    }

    data = {
        "current": {
            "time": "2026-08-25T23:00",
            "temperature_2m": 28.4,
            "relative_humidity_2m": 88,
            "apparent_temperature": 35.3,
            "precipitation": 0.0,
            "weather_code": 3,
            "wind_speed_10m": 4.9,
            "wind_direction_10m": 184,
        }
    }

    observation = transform_weather(city,data)

    assert observation.city == "Delhi"
    assert observation.temperature_c == 28.4
    assert observation.humidity_percent == 88
    assert observation.apparent_temperature_c == 35.3
    assert observation.precipitation_mm == 0.0
    assert observation.weather_code == 3
    assert observation.wind_speed_kmh == 4.9
    assert observation.wind_direction_degrees == 184