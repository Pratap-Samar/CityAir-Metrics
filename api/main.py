from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database.connection import get_connection
from database.repositories import get_cities, get_city, get_latest_pipeline_run
from ingestion.weather_client import fetch_forecast
from processor.analytics import (
    get_latest_weather_by_city,
    get_latest_air_quality_by_city,
    get_latest_city_snapshot,
    get_weather_history_by_city,
    get_air_quality_history_by_city,
)

#=========================Pydantic models========================

class CityResponse(BaseModel):
    id: int
    name: str
    country: str
    latitude: float
    longitude: float

class WeatherResponse(BaseModel):
    city_id: int
    name: str
    country: str
    observed_at: datetime
    temperature_c: float | None
    humidity_percent: float | None
    apparent_temperature_c: float | None
    precipitation_mm: float | None
    weather_code: int | None
    wind_speed_kmh: float | None
    wind_direction_degrees: float | None


class AirQualityResponse(BaseModel):
    city_id: int
    name: str
    country: str
    observed_at: datetime
    pm10: float | None
    pm2_5: float | None
    carbon_monoxide: float | None
    nitrogen_dioxide: float | None
    sulphur_dioxide: float | None
    ozone: float | None
    us_aqi: float | None


class AnalyticsWeatherResponse(BaseModel):
    observed_at: datetime | None
    temperature_c: float | None
    humidity_percent: float | None
    apparent_temperature_c: float | None
    precipitation_mm: float | None
    weather_code: int | None
    wind_speed_kmh: float | None
    wind_direction_degrees: float | None


class AnalyticsAirQualityResponse(BaseModel):
    observed_at: datetime | None
    pm10: float | None
    pm2_5: float | None
    carbon_monoxide: float | None
    nitrogen_dioxide: float | None
    sulphur_dioxide: float | None
    ozone: float | None
    us_aqi: float | None


class AnalyticsResponse(BaseModel):
    city_id: int
    name: str
    country: str
    weather: AnalyticsWeatherResponse
    air_quality: AnalyticsAirQualityResponse


class WeatherHistoryResponse(BaseModel):
    observed_at: datetime
    temperature_c: float | None
    humidity_percent: float | None
    apparent_temperature_c: float | None
    precipitation_mm: float | None
    wind_speed_kmh: float | None


class AirQualityHistoryResponse(BaseModel):
    observed_at: datetime
    pm10: float | None
    pm2_5: float | None
    carbon_monoxide: float | None
    nitrogen_dioxide: float | None
    sulphur_dioxide: float | None
    ozone: float | None
    us_aqi: float | None


class ForecastHourly(BaseModel):
    time: str
    temperature_2m: float | None
    apparent_temperature: float | None
    precipitation_probability: float | None
    weather_code: int | None


class ForecastDaily(BaseModel):
    time: str
    weather_code: int | None
    temperature_2m_max: float | None
    temperature_2m_min: float | None
    precipitation_probability_max: float | None


class ForecastResponse(BaseModel):
    hourly: list[ForecastHourly]
    daily: list[ForecastDaily]


class PipelineStatusResponse(BaseModel):
    status: str
    is_active: bool
    started_at: datetime | None
    completed_at: datetime | None
    cities_processed: int | None
    cities_failed: int | None


app = FastAPI(
    title="CityAir Metrics API",
    description="API for city weather and air-quality data",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#===================API ENDPOINTS=======================
@app.get("/")
def root():
    return {"message": "CityAir Metrics API"}


@app.get("/cities", response_model=list[CityResponse])
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


@app.get("/weather/latest", response_model=list[WeatherResponse])
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


@app.get("/air-quality/latest", response_model=list[AirQualityResponse])
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


@app.get("/analytics", response_model=list[AnalyticsResponse])
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


@app.get("/weather/history/{city_id}", response_model=list[WeatherHistoryResponse])
def weather_history(city_id: int, hours: int = 24):
    connection = get_connection()
    try:
        rows = get_weather_history_by_city(connection, city_id, hours)
        return [
            {
                "observed_at": row[0],
                "temperature_c": row[1],
                "humidity_percent": row[2],
                "apparent_temperature_c": row[3],
                "precipitation_mm": row[4],
                "wind_speed_kmh": row[5],
            }
            for row in rows
        ]
    finally:
        connection.close()


@app.get("/weather/forecast/{city_id}", response_model=ForecastResponse)
def weather_forecast(city_id: int):
    connection = get_connection()
    try:
        city = get_city(connection, city_id)
        if not city:
            raise HTTPException(status_code=404, detail="City not found")
        
        latitude = city[3]
        longitude = city[4]
    finally:
        connection.close()
        
    data = fetch_forecast(latitude, longitude, days=5)
    
    hourly = []
    if "hourly" in data:
        for i in range(len(data["hourly"].get("time", []))):
            hourly.append({
                "time": data["hourly"]["time"][i],
                "temperature_2m": data["hourly"]["temperature_2m"][i],
                "apparent_temperature": data["hourly"]["apparent_temperature"][i],
                "precipitation_probability": data["hourly"]["precipitation_probability"][i],
                "weather_code": data["hourly"]["weather_code"][i],
            })
            
    daily = []
    if "daily" in data:
        for i in range(len(data["daily"].get("time", []))):
            daily.append({
                "time": data["daily"]["time"][i],
                "weather_code": data["daily"]["weather_code"][i],
                "temperature_2m_max": data["daily"]["temperature_2m_max"][i],
                "temperature_2m_min": data["daily"]["temperature_2m_min"][i],
                "precipitation_probability_max": data["daily"]["precipitation_probability_max"][i],
            })
            
    return {"hourly": hourly, "daily": daily}
@app.get("/air-quality/history/{city_id}",    response_model=list[AirQualityHistoryResponse],)
def air_quality_history(city_id: int, hours: int = 24):
    connection = get_connection()
    try:
        rows = get_air_quality_history_by_city(
            connection,
            city_id,
            hours,
        )

        return [
            {
                "observed_at": row[0],
                "pm10": row[1],
                "pm2_5": row[2],
                "carbon_monoxide": row[3],
                "nitrogen_dioxide": row[4],
                "sulphur_dioxide": row[5],
                "ozone": row[6],
                "us_aqi": row[7],
            }
            for row in rows
        ]
    finally:
        connection.close()


@app.get("/pipeline/status", response_model=PipelineStatusResponse)
def pipeline_status():
    connection = get_connection()
    try:
        run = get_latest_pipeline_run(connection)
        if not run:
            return {
                "status": "UNKNOWN",
                "is_active": False,
                "started_at": None,
                "completed_at": None,
                "cities_processed": None,
                "cities_failed": None,
            }
        
        # run = (id, started_at, completed_at, status, cities_processed, cities_failed, duration_seconds, error_message)
        status_str = run[3]
        is_active = status_str == "RUNNING"
        
        return {
            "status": status_str,
            "is_active": is_active,
            "started_at": run[1],
            "completed_at": run[2],
            "cities_processed": run[4],
            "cities_failed": run[5],
        }
    finally:
        connection.close()

