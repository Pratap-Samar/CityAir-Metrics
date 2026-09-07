from ingestion import pipeline

class FakeConnection:
    def __init__(self):
        self.commit_count = 0
        self.rollback_count = 0
        self.closed = False

    def commit(self):
        self.commit_count += 1

    def rollback(self):
        self.rollback_count += 1

    def close(self):
        self.closed = True

def test_pipeline_transaction_boundaries(monkeypatch):
    cities = [
        {
            "name": "Delhi",      # Success
            "country": "India",
            "latitude": 28.6,
            "longitude": 77.2,
        },
        {
            "name": "Mumbai",     # Fails at weather fetch
            "country": "India",
            "latitude": 19.0,
            "longitude": 72.8,
        },
        {
            "name": "Bengaluru",  # Fails at air quality fetch
            "country": "India",
            "latitude": 12.9,
            "longitude": 77.5,
        },
        {
            "name": "Chennai",    # Success
            "country": "India",
            "latitude": 13.0,
            "longitude": 80.2,
        },
    ]

    monkeypatch.setattr(pipeline, "CITIES", cities)

    fake_conn = FakeConnection()
    monkeypatch.setattr(pipeline, "get_connection", lambda: fake_conn)

    saved_weather_cities = []
    saved_air_quality_cities = []

    def fake_get_or_create_city(city, connection):
        return city["name"]

    monkeypatch.setattr(pipeline, "get_or_create_city", fake_get_or_create_city)

    def fake_fetch_weather(latitude, longitude):
        if latitude == 19.0:
            raise Exception("Weather API failed for Mumbai")
        return {"current": {"weather_code": 1}}

    monkeypatch.setattr(pipeline, "fetch_weather", fake_fetch_weather)

    def fake_transform_weather(city, data):
        return object()

    def fake_save_weather_observation(observation, city_id, connection):
        saved_weather_cities.append(city_id)
        return 1

    monkeypatch.setattr(pipeline, "transform_weather", fake_transform_weather)
    monkeypatch.setattr(pipeline, "save_weather_observation", fake_save_weather_observation)

    def fake_fetch_air_quality(latitude, longitude):
        if latitude == 12.9:
            raise Exception("Air Quality API failed for Bengaluru")
        return {}

    monkeypatch.setattr(pipeline, "fetch_air_quality", fake_fetch_air_quality)

    def fake_transform_air_quality(city, data):
        return object()

    def fake_save_air_quality_observation(observation, city_id, connection):
        saved_air_quality_cities.append(city_id)
        return 1

    monkeypatch.setattr(pipeline, "transform_air_quality", fake_transform_air_quality)
    monkeypatch.setattr(pipeline, "save_air_quality_observation", fake_save_air_quality_observation)

    monkeypatch.setattr(pipeline, "validate_weather_freshness", lambda observation: None)
    monkeypatch.setattr(pipeline, "validate_air_quality_freshness", lambda observation: None)
    monkeypatch.setattr(pipeline, "create_pipeline_run", lambda started_at, connection: 1)
    monkeypatch.setattr(pipeline, "complete_pipeline_run", lambda **kwargs: None)

    messages = []

    class FakeLogger:
        def info(self, message):
            messages.append(message)
        def error(self, message):
            messages.append(message)
        def exception(self, message):
            messages.append(message)

    monkeypatch.setattr(pipeline, "logger", FakeLogger())

    pipeline.run_pipeline()

    # Verify pipeline continued after failures
    assert any("City ingestion successful: city=Delhi" in msg for msg in messages)
    assert any("City ingestion failed: city=Mumbai" in msg for msg in messages)
    assert any("City ingestion failed: city=Bengaluru" in msg for msg in messages)
    assert any("City ingestion successful: city=Chennai" in msg for msg in messages)

    # Verify commit/rollback call counts (2 successes, 2 failures)
    assert fake_conn.commit_count == 2
    assert fake_conn.rollback_count == 2
    assert fake_conn.closed is True

    # Verify partial save tracking logic:
    # Verifies rollback is triggered after the partial weather save
    assert "Delhi" in saved_weather_cities
    assert "Delhi" in saved_air_quality_cities

    assert "Mumbai" not in saved_weather_cities
    assert "Mumbai" not in saved_air_quality_cities

    assert "Bengaluru" in saved_weather_cities
    assert "Bengaluru" not in saved_air_quality_cities

    assert "Chennai" in saved_weather_cities
    assert "Chennai" in saved_air_quality_cities
