from ingestion import pipeline


def test_pipeline_continues_when_city_fails(monkeypatch):

    cities = [
        {
            "name": "Delhi",
            "country": "India",
            "latitude": 28.6139,
            "longitude": 77.2090,
        },
        {
            "name": "Mumbai",
            "country": "India",
            "latitude": 19.0760,
            "longitude": 72.8777,
        },
        {
            "name": "Bengaluru",
            "country": "India",
            "latitude": 12.9716,
            "longitude": 77.5946,
        },
    ]

    monkeypatch.setattr(
        pipeline,
        "CITIES",
        cities,
    )

    def fake_get_or_create_city(city, connection):
        return 1

    monkeypatch.setattr(
        pipeline,
        "get_or_create_city",
        fake_get_or_create_city,
    )

    def fake_fetch_weather(latitude, longitude):

        if latitude == 19.0760:
            raise Exception("Weather API failed")

        return {
            "current": {
                "time": "2026-08-30T23:45",
                "temperature_2m": 29.0,
                "relative_humidity_2m": 70,
                "apparent_temperature": 32.0,
                "precipitation": 0.0,
                "weather_code": 1,
                "wind_speed_10m": 5.0,
                "wind_direction_10m": 180.0,
            }
        }

    monkeypatch.setattr(
        pipeline,
        "fetch_weather",
        fake_fetch_weather,
    )

    def fake_transform_weather(city, data):
        return object()

    def fake_save_weather_observation(observation, city_id, connection):
        return 1

    def fake_fetch_air_quality(latitude, longitude):
        return {}

    def fake_transform_air_quality(city, data):
        return object()

    def fake_save_air_quality_observation(observation, city_id, connection):
        return 1

    monkeypatch.setattr(
        pipeline,
        "transform_weather",
        fake_transform_weather,
    )

    monkeypatch.setattr(
        pipeline,
        "save_weather_observation",
        fake_save_weather_observation,
    )

    monkeypatch.setattr(
        pipeline,
        "fetch_air_quality",
        fake_fetch_air_quality,
    )

    monkeypatch.setattr(
        pipeline,
        "transform_air_quality",
        fake_transform_air_quality,
    )

    monkeypatch.setattr(
        pipeline,
        "save_air_quality_observation",
        fake_save_air_quality_observation,
    )

    messages = []

    class FakeLogger:

        def info(self, message):
            messages.append(message)

        def error(self, message):
            messages.append(message)

        def exception(self, message):
            messages.append(message)

    monkeypatch.setattr(
        pipeline,
        "logger",
        FakeLogger(),
    )

    pipeline.run_pipeline()

    assert any(
        "City ingestion successful: city=Delhi"
        in message
        for message in messages
    )

    assert any(
        "City ingestion failed: city=Mumbai"
        in message
        for message in messages
    )

    assert any(
        "City ingestion successful: city=Bengaluru"
        in message
        for message in messages
    )
