import os
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

POSTGRES_USER = os.environ.get("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "postgres")
POSTGRES_DB = os.environ.get("POSTGRES_DB", "postgres")
POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.environ.get("POSTGRES_PORT", "5432")

base_url = os.environ.get(
    "DATABASE_URL",
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

# Enforce Asia/Kolkata timezone on all database connections
tz_option = urllib.parse.quote("-c timezone=Asia/Kolkata")
if "?" in base_url:
    DATABASE_URL = f"{base_url}&options={tz_option}"
else:
    DATABASE_URL = f"{base_url}?options={tz_option}"

DB_POOL_MIN_SIZE = int(os.environ.get("DB_POOL_MIN_SIZE", "5"))
DB_POOL_MAX_SIZE = int(os.environ.get("DB_POOL_MAX_SIZE", "20"))

WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"
AIR_QUALITY_API_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"

API_TIMEOUT_SECONDS = 30
API_MAX_RETRIES = 3