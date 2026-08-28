import os

import psycopg
from dotenv import load_dotenv


load_dotenv()


DATABASE_URL = (
    f"postgresql://{os.environ['POSTGRES_USER']}:"
    f"{os.environ['POSTGRES_PASSWORD']}@localhost:5432/"
    f"{os.environ['POSTGRES_DB']}"
)


def get_connection():
    return psycopg.connect(
        DATABASE_URL,
        connect_timeout=5,
    )