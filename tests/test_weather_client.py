import requests

from ingestion.weather_client import fetch_weather


class FakeResponse:

    def raise_for_status(self):
        pass

    def json(self):
        return {
            "current": {
                "time": "2026-08-30T23:45",
                "temperature_2m": 29.0,
                "relative_humidity_2m": 79,
            }
        }


def test_fetch_weather_retries(monkeypatch):

    attempts = 0

    def fake_get(*args, **kwargs):
        nonlocal attempts

        attempts += 1

        if attempts < 3:
            raise requests.RequestException("Temporary failure")

        return FakeResponse()

    monkeypatch.setattr(
        "ingestion.weather_client.requests.get",
        fake_get,
    )

    monkeypatch.setattr(
        "ingestion.weather_client.time.sleep",
        lambda seconds: None,
    )

    result = fetch_weather(
        28.6139,
        77.2090,
    )

    assert attempts == 3
    assert result["current"]["temperature_2m"] == 29.0
    assert result["current"]["relative_humidity_2m"] == 79
