from fastapi.testclient import TestClient

from api.main import app
from database.connection import get_connection
from database.repositories import get_or_create_city


client = TestClient(app)


def test_get_cities():
    connection = get_connection()

    try:
        city = {
            "name": "Test API City",
            "country": "Test API Country",
            "latitude": 11.1234,
            "longitude": 21.5678,
        }

        get_or_create_city(
            city,
            connection,
        )
    finally:
        connection.close()

    response = client.get("/cities")

    assert response.status_code == 200

    cities = response.json()

    assert isinstance(cities, list)

    test_city = next(
        city
        for city in cities
        if city["name"] == "Test API City"
        and city["country"] == "Test API Country"
    )

    assert test_city["latitude"] == 11.1234
    assert test_city["longitude"] == 21.5678