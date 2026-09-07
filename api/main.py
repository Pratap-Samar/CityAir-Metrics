from datetime import datetime

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database.connection import get_connection
from database.repositories import (
    get_cities,
    get_city,
    get_latest_pipeline_run,
)
from ingestion.weather_client import fetch_forecast
from processor.analytics import (
    get_history_by_city,
    get_latest_air_quality_by_city,
    get_latest_city_snapshot,
    get_latest_weather_by_city,
    VALID_HISTORY_METRICS,
    VALID_HISTORY_PERIODS,
    get_dashboard_summary,
    get_dashboard_map_data,
    get_time_series_trends,
    get_biggest_changes,
    get_city_rankings,
    get_dashboard_pipeline_status,
)


# ============================================================================
# FastAPI application
# ============================================================================


app = FastAPI(
    title="CityAir Metrics API",
    description="API for city weather and air-quality data",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Pydantic response models
# ============================================================================


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


# ----------------------------------------------------------------------------
# History response models
# ----------------------------------------------------------------------------


class WeatherHistoryResponse(BaseModel):
    observed_at: datetime
    temperature_c: float | None
    humidity_percent: float | None
    apparent_temperature_c: float | None
    precipitation_mm: float | None
    wind_speed_kmh: float | None


class WeatherDailyHistoryResponse(BaseModel):
    observation_date: datetime | None
    average_temperature_c: float | None
    minimum_temperature_c: float | None
    maximum_temperature_c: float | None
    average_humidity_percent: float | None
    average_apparent_temperature_c: float | None
    total_precipitation_mm: float | None
    average_wind_speed_kmh: float | None


class AirQualityHistoryResponse(BaseModel):
    observed_at: datetime
    pm10: float | None
    pm2_5: float | None
    carbon_monoxide: float | None
    nitrogen_dioxide: float | None
    sulphur_dioxide: float | None
    ozone: float | None
    us_aqi: float | None


class AirQualityDailyHistoryResponse(BaseModel):
    observation_date: datetime | None
    average_pm10: float | None
    maximum_pm10: float | None
    average_pm2_5: float | None
    maximum_pm2_5: float | None
    average_carbon_monoxide: float | None
    average_nitrogen_dioxide: float | None
    average_sulphur_dioxide: float | None
    average_ozone: float | None
    average_us_aqi: float | None
    maximum_us_aqi: float | None


# ----------------------------------------------------------------------------
# Forecast response models
# ----------------------------------------------------------------------------


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


# ----------------------------------------------------------------------------
# Pipeline response model
# ----------------------------------------------------------------------------


class PipelineStatusResponse(BaseModel):
    status: str
    is_active: bool
    started_at: datetime | None
    completed_at: datetime | None
    cities_processed: int | None
    cities_failed: int | None


# ============================================================================
# Database helpers
# ============================================================================


def _get_city_coordinates(city_id: int):
    connection = get_connection()

    try:
        city = get_city(connection, city_id)

        if not city:
            raise HTTPException(
                status_code=404,
                detail="City not found",
            )

        return city[3], city[4]

    finally:
        connection.close()


# ============================================================================
# Row transformation helpers
# ============================================================================


def _weather_row_to_response(row):
    return {
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


def _air_quality_row_to_response(row):
    return {
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


def _city_row_to_response(row):
    return {
        "id": row[0],
        "name": row[1],
        "country": row[2],
        "latitude": row[3],
        "longitude": row[4],
    }


def _analytics_row_to_response(row):
    return {
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


def _weather_history_row_to_response(row):
    return {
        "observed_at": row[0],
        "temperature_c": row[1],
        "humidity_percent": row[2],
        "apparent_temperature_c": row[3],
        "precipitation_mm": row[4],
        "wind_speed_kmh": row[5],
    }


def _weather_daily_history_row_to_response(row):
    return {
        "observation_date": row[0],
        "average_temperature_c": row[1],
        "minimum_temperature_c": row[2],
        "maximum_temperature_c": row[3],
        "average_humidity_percent": row[4],
        "average_apparent_temperature_c": row[5],
        "total_precipitation_mm": row[6],
        "average_wind_speed_kmh": row[7],
    }


def _air_quality_history_row_to_response(row):
    return {
        "observed_at": row[0],
        "pm10": row[1],
        "pm2_5": row[2],
        "carbon_monoxide": row[3],
        "nitrogen_dioxide": row[4],
        "sulphur_dioxide": row[5],
        "ozone": row[6],
        "us_aqi": row[7],
    }


def _air_quality_daily_history_row_to_response(row):
    return {
        "observation_date": row[0],
        "average_pm10": row[1],
        "maximum_pm10": row[2],
        "average_pm2_5": row[3],
        "maximum_pm2_5": row[4],
        "average_carbon_monoxide": row[5],
        "average_nitrogen_dioxide": row[6],
        "average_sulphur_dioxide": row[7],
        "average_ozone": row[8],
        "average_us_aqi": row[9],
        "maximum_us_aqi": row[10],
    }


# ============================================================================
# Forecast transformation helpers
# ============================================================================


def _build_forecast_hourly(data):
    hourly = data.get("hourly", {})

    times = hourly.get("time", [])
    temperatures = hourly.get("temperature_2m", [])
    apparent_temperatures = hourly.get("apparent_temperature", [])
    precipitation_probabilities = hourly.get(
        "precipitation_probability",
        [],
    )
    weather_codes = hourly.get("weather_code", [])

    result = []

    for i, time in enumerate(times):
        result.append(
            {
                "time": time,
                "temperature_2m": (
                    temperatures[i]
                    if i < len(temperatures)
                    else None
                ),
                "apparent_temperature": (
                    apparent_temperatures[i]
                    if i < len(apparent_temperatures)
                    else None
                ),
                "precipitation_probability": (
                    precipitation_probabilities[i]
                    if i < len(precipitation_probabilities)
                    else None
                ),
                "weather_code": (
                    weather_codes[i]
                    if i < len(weather_codes)
                    else None
                ),
            }
        )

    return result


def _build_forecast_daily(data):
    daily = data.get("daily", {})

    times = daily.get("time", [])
    weather_codes = daily.get("weather_code", [])
    temperature_max = daily.get("temperature_2m_max", [])
    temperature_min = daily.get("temperature_2m_min", [])
    precipitation_probability = daily.get(
        "precipitation_probability_max",
        [],
    )

    result = []

    for i, time in enumerate(times):
        result.append(
            {
                "time": time,
                "weather_code": (
                    weather_codes[i]
                    if i < len(weather_codes)
                    else None
                ),
                "temperature_2m_max": (
                    temperature_max[i]
                    if i < len(temperature_max)
                    else None
                ),
                "temperature_2m_min": (
                    temperature_min[i]
                    if i < len(temperature_min)
                    else None
                ),
                "precipitation_probability_max": (
                    precipitation_probability[i]
                    if i < len(precipitation_probability)
                    else None
                ),
            }
        )

    return result


# ============================================================================
# System endpoints
# ============================================================================


@app.get("/")
def root():
    return {
        "message": "CityAir Metrics API",
    }


# ============================================================================
# City endpoints
# ============================================================================


@app.get(
    "/cities",
    response_model=list[CityResponse],
)
def cities():
    connection = get_connection()

    try:
        rows = get_cities(connection)

        return [
            _city_row_to_response(row)
            for row in rows
        ]

    finally:
        connection.close()


# ============================================================================
# Current weather endpoints
# ============================================================================


@app.get(
    "/weather/latest",
    response_model=list[WeatherResponse],
)
def latest_weather():
    connection = get_connection()

    try:
        rows = get_latest_weather_by_city(connection)

        return [
            _weather_row_to_response(row)
            for row in rows
        ]

    finally:
        connection.close()


# ============================================================================
# Current air-quality endpoints
# ============================================================================


@app.get(
    "/air-quality/latest",
    response_model=list[AirQualityResponse],
)
def latest_air_quality():
    connection = get_connection()

    try:
        rows = get_latest_air_quality_by_city(connection)

        return [
            _air_quality_row_to_response(row)
            for row in rows
        ]

    finally:
        connection.close()


# ============================================================================
# Combined analytics endpoint
# ============================================================================


@app.get(
    "/analytics",
    response_model=list[AnalyticsResponse],
)
def analytics():
    connection = get_connection()

    try:
        rows = get_latest_city_snapshot(connection)

        return [
            _analytics_row_to_response(row)
            for row in rows
        ]

    finally:
        connection.close()


# ============================================================================
# Historical endpoints
# ============================================================================


@app.get(
    "/weather/history/{city_id}",
)
def weather_history(
    city_id: int,
    period: str = Query(
        default="24h",
        description="History period: 24h, 7d, or 30d",
    ),
):
    if period not in VALID_HISTORY_PERIODS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported history period: {period}. "
                f"Expected one of: "
                f"{sorted(VALID_HISTORY_PERIODS)}"
            ),
        )

    connection = get_connection()

    try:
        rows = get_history_by_city(
            connection,
            city_id,
            metric="weather",
            period=period,
        )

        if period == "24h":
            return [
                _weather_history_row_to_response(row)
                for row in rows
            ]

        return [
            _weather_daily_history_row_to_response(row)
            for row in rows
        ]

    finally:
        connection.close()


@app.get(
    "/air-quality/history/{city_id}",
)
def air_quality_history(
    city_id: int,
    period: str = Query(
        default="24h",
        description="History period: 24h, 7d, or 30d",
    ),
):
    if period not in VALID_HISTORY_PERIODS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported history period: {period}. "
                f"Expected one of: "
                f"{sorted(VALID_HISTORY_PERIODS)}"
            ),
        )

    connection = get_connection()

    try:
        rows = get_history_by_city(
            connection,
            city_id,
            metric="air_quality",
            period=period,
        )

        if period == "24h":
            return [
                _air_quality_history_row_to_response(row)
                for row in rows
            ]

        return [
            _air_quality_daily_history_row_to_response(row)
            for row in rows
        ]

    finally:
        connection.close()


# ============================================================================
# Forecast endpoints
# ============================================================================


@app.get(
    "/weather/forecast/{city_id}",
    response_model=ForecastResponse,
)
def weather_forecast(city_id: int):
    latitude, longitude = _get_city_coordinates(city_id)

    data = fetch_forecast(
        latitude,
        longitude,
        days=5,
    )

    return {
        "hourly": _build_forecast_hourly(data),
        "daily": _build_forecast_daily(data),
    }


# ============================================================================
# Pipeline endpoints
# ============================================================================


@app.get(
    "/pipeline/status",
    response_model=PipelineStatusResponse,
)
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

        # run =
        # (
        #     id,
        #     started_at,
        #     completed_at,
        #     status,
        #     cities_processed,
        #     cities_failed,
        #     duration_seconds,
        #     error_message,
        # )

        status_str = run[3]

        return {
            "status": status_str,
            "is_active": status_str == "RUNNING",
            "started_at": run[1],
            "completed_at": run[2],
            "cities_processed": run[4],
            "cities_failed": run[5],
        }

    finally:
        connection.close()

# ============================================================================
# Dashboard endpoints
# ============================================================================

@app.get("/dashboard/summary")
def dashboard_summary():
    connection = get_connection()
    try:
        return get_dashboard_summary(connection)
    finally:
        connection.close()

@app.get("/dashboard/map")
def dashboard_map():
    connection = get_connection()
    try:
        return get_dashboard_map_data(connection)
    finally:
        connection.close()

@app.get("/dashboard/trends/{city_id}")
def dashboard_trends(
    city_id: int,
    metric: str = Query("aqi", description="aqi or temperature"),
    period: str = Query("24h", description="24h, 7d, or 30d")
):
    connection = get_connection()
    try:
        city = get_city(connection, city_id)
        if not city:
            raise HTTPException(status_code=404, detail="City not found")

        if metric not in ("aqi", "temperature"):
            raise HTTPException(status_code=400, detail="Invalid metric. Must be aqi or temperature.")
        if period not in ("24h", "7d", "30d"):
            raise HTTPException(status_code=400, detail="Invalid period. Must be 24h, 7d, or 30d.")

        return get_time_series_trends(connection, city_id, metric, period)
    finally:
        connection.close()

@app.get("/dashboard/changes")
def dashboard_changes(metric: str = Query("aqi", description="aqi")):
    connection = get_connection()
    try:
        if metric != "aqi":
            raise HTTPException(status_code=400, detail="Invalid metric. Only aqi is supported.")
        return get_biggest_changes(connection, metric)
    finally:
        connection.close()

@app.get("/dashboard/rankings")
def dashboard_rankings(
    metric: str = Query("aqi", description="aqi, pm2_5, or pm10"),
    period: str = Query("24h", description="24h, 7d, or 30d")
):
    connection = get_connection()
    try:
        if metric not in ("aqi", "pm2_5", "pm10"):
            raise HTTPException(status_code=400, detail="Invalid metric. Must be aqi, pm2_5, or pm10.")
        if period not in ("24h", "7d", "30d"):
            raise HTTPException(status_code=400, detail="Invalid period. Must be 24h, 7d, or 30d.")

        return get_city_rankings(connection, metric, period)
    finally:
        connection.close()

@app.get("/dashboard/pipeline")
def dashboard_pipeline():
    connection = get_connection()
    try:
        status = get_dashboard_pipeline_status(connection)
        if not status:
            return {
                "status": "UNKNOWN",
                "started_at": None,
                "completed_at": None,
                "duration_seconds": None,
                "cities_processed": 0,
                "cities_failed": 0,
                "error_message": None
            }
        return status
    finally:
        connection.close()
