from database.connection import get_connection
from processor.analytics import (
    get_latest_weather_by_city,
    get_latest_air_quality_by_city,
)


def test_get_latest_weather_by_city():
    connection = get_connection()

    try:
        rows = get_latest_weather_by_city(connection)

        assert rows
        assert all(len(row) == 11 for row in rows)

        city_names = {row[1] for row in rows}

        assert "Delhi" in city_names
        assert "Mumbai" in city_names

    finally:
        connection.close()


def test_get_latest_air_quality_by_city():
    connection = get_connection()

    try:
        rows = get_latest_air_quality_by_city(connection)

        assert rows
        assert all(len(row) == 11 for row in rows)

        city_names = {row[1] for row in rows}

        assert "Delhi" in city_names
        assert "Mumbai" in city_names

    finally:
        connection.close()