import os

from dotenv import load_dotenv


load_dotenv()


POSTGRES_USER = os.environ["POSTGRES_USER"]
POSTGRES_PASSWORD = os.environ["POSTGRES_PASSWORD"]
POSTGRES_DB = os.environ["POSTGRES_DB"]


DATABASE_URL = (
    f"postgresql://{POSTGRES_USER}:"
    f"{POSTGRES_PASSWORD}@localhost:5432/"
    f"{POSTGRES_DB}"
)
WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"
AIR_QUALITY_API_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"

API_TIMEOUT_SECONDS = 30
API_MAX_RETRIES = 3