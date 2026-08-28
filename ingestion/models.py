from datetime import datetime
from pydantic import BaseModel, Field

#weather data
class WeatherObservation(BaseModel):
    city: str
    country: str

    latitude: float
    longitude: float

    observed_at: datetime

    temperature_c: float | None = None
    humidity_percent: float | None = Field(
        default=None,
        ge=0,
        le=100,
    )
    
    apparent_temperature_c: float | None = None

    precipitation_mm: float | None = Field(
        default=None,
        ge=0,
    )

    weather_code: int | None = None

    wind_speed_kmh: float | None = Field(
        default=None,
        ge=0,
    )

    wind_direction_degrees: float | None = Field(
        default=None,
        ge=0,
        le=360,
    )

#AQI data
class AirQualityObservation(BaseModel):
    city: str
    country: str

    latitude: float
    longitude: float

    observed_at: datetime

    pm10: float | None = Field(
        default=None,
        ge=0,
    )

    pm2_5: float | None = Field(
        default=None,
        ge=0,
    )

    carbon_monoxide: float | None = Field(
        default=None,
        ge=0,
    )

    nitrogen_dioxide: float | None = Field(
        default=None,
        ge=0,
    )

    sulphur_dioxide: float | None = Field(
        default=None,
        ge=0,
    )

    ozone: float | None = Field(
        default=None,
        ge=0,
    )

    us_aqi: float | None = Field(
        default=None,
        ge=0,
    )
