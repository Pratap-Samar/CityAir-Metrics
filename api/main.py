from fastapi import FastAPI

from database.connection import get_connection
from database.repositories import get_cities

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
        