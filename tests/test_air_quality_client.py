import requests

from ingestion.air_quality_client import fetch_air_quality


class FakeResponse:

    def raise_for_status(self):
        pass

    def json(self):
        return {
            "current": {
                "time": "2026-08-30T23:45",
                "pm2_5": 20.0,
                "us_aqi": 50,
            }
        }


def test_fetch_air_quality_retries(monkeypatch):

    attempts = 0

    def fake_get(*args, **kwargs):
        nonlocal attempts

        attempts += 1

        if attempts < 3:
            raise requests.RequestException("Temporary failure")

        return FakeResponse()

    monkeypatch.setattr(
        "ingestion.air_quality_client.requests.get",
        fake_get,
    )

    monkeypatch.setattr(
        "ingestion.air_quality_client.time.sleep",
        lambda seconds: None,
    )

    result = fetch_air_quality(
        28.6139,
        77.2090,
    )

    assert attempts == 3
    assert result["current"]["pm2_5"] == 20.0
    assert result["current"]["us_aqi"] == 50
