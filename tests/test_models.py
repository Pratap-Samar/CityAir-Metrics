import pytest
from pydantic import ValidationError

from ingestion.models import WeatherObservation


def test_valid_weather_observation():
    observation = WeatherObservation(
        city="Delhi",
        country="India",
        latitude=28.6139,
        longitude=77.2090,
        observed_at="2026-08-25T23:00",
        temperature_c=28.4,
        humidity_percent=88,
        precipitation_mm=0.0,
    )

    assert observation.city == "Delhi"
    assert observation.temperature_c == 28.4
    assert observation.humidity_percent == 88


def test_invalid_humidity():
    with pytest.raises(ValidationError):
        WeatherObservation(
            city="Delhi",
            country="India",
            latitude=28.6139,
            longitude=77.2090,
            observed_at="2026-08-25T23:00",
            temperature_c=28.4,
            humidity_percent=150,
            precipitation_mm=0.0,
        )


def test_negative_precipitation():
    with pytest.raises(ValidationError):
        WeatherObservation(
            city="Delhi",
            country="India",
            latitude=28.6139,
            longitude=77.2090,
            observed_at="2026-08-25T23:00",
            temperature_c=28.4,
            humidity_percent=88,
            precipitation_mm=-5,
        )