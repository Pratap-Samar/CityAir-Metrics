from fastapi import FastAPI

from database.connection import get_connection
from database.repositories import get_cities
from processor.analytics import get_latest_weather_by_city

app = FastAPI(
    title="CityAir Metrics API",
    description="API for city weather and air-quality data",
    version="1.0.0"
)

@app.get("/")
def root():
    return {"message": "CityAir Metrics API"}


@app.get("/cities")
def cities():
    connection = get_connection()

    try:
        rows = get_cities(connection)

        return[
            {
                "id": row[0],
                "name": row[1],
                "country" : row[2],
                "latitude" : row[3],
                "longitude" : row[4],

            }
            for row in rows
        ]
    finally:
        connection.close()

@app.get("/weather/latest")
def latest_weather():
    connection = get_connection()

    try:
        rows = get_latest_weather_by_city(connection)

        return [
            {
                "city_id": row[0],
                "name": row[1],
                "country": row[2],
                "observed_at": row[3],
                "temperature_c": row[4],
                "humidity_percent": row[5],
                "apparent_temperature_c": row[6],
                "precipitation_mm": row[7],
                "weather_code": row[8],
                "wind_speed_kmh": row[9],
                "wind_direction_degrees": row[10],
            }
            for row in rows
        ]

    finally:
        connection.close()