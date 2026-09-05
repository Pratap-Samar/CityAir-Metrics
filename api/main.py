from fastapi import FastAPI

from database.connection import get_connection
from database.repositories import get_cities
from processor.analytics import (
    get_latest_weather_by_city,
    get_latest_air_quality_by_city,
    get_latest_city_snapshot,
)
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

@app.get("/air-quality/latest")
def latest_air_quality():
    connection = get_connection()

    try:
        rows = get_latest_air_quality_by_city(connection)
        return [
            {
                "city_id": row[0],
                "name": row[1],
                "country": row[2],
                "observed_at": row[3],
                "pm10": row[4],
                "pm2_5": row[5],
                "carbon_monoxide": row[6],
                "nitrogen_dioxide": row[7],
                "sulphur_dioxide": row[8],
                "ozone": row[9],
                "us_aqi": row[10],
            }
            for row in rows
        ]
    finally:
        connection.close()

@app.get("/analytics")
def analytics():
    connection = get_connection()

    try:
        rows = get_latest_city_snapshot(connection)

        return [
            {
                "city_id": row[0],
                "name": row[1],
                "country": row[2],
                "weather": {
                    "observed_at": row[3],
                    "temperature_c": row[4],
                    "humidity_percent": row[5],
                    "apparent_temperature_c": row[6],
                    "precipitation_mm": row[7],
                    "weather_code": row[8],
                    "wind_speed_kmh": row[9],
                    "wind_direction_degrees": row[10],
                },
                "air_quality": {
                    "observed_at": row[11],
                    "pm10": row[12],
                    "pm2_5": row[13],
                    "carbon_monoxide": row[14],
                    "nitrogen_dioxide": row[15],
                    "sulphur_dioxide": row[16],
                    "ozone": row[17],
                    "us_aqi": row[18],
                },
            }
            for row in rows
        ]

    finally:
        connection.close()