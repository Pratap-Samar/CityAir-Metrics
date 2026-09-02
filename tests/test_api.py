from fastapi.testclient import TestClient

from api.main import app


client = TestClient(app)


def test_get_cities():
    response = client.get("/cities")

    assert response.status_code == 200

    cities = response.json()

    assert isinstance(cities, list)
    assert cities

    test_city = next(
        city
        for city in cities
        if city["name"] == "Test City"
        and city["country"] == "Test Country"
    )

    assert test_city["latitude"] == 10.1234
    assert test_city["longitude"] == 20.5678