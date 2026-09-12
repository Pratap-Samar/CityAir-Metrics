import psycopg
from psycopg_pool import ConnectionPool

from config.settings import (
    DATABASE_URL,
    DB_POOL_MIN_SIZE,
    DB_POOL_MAX_SIZE,
)

pool = None

def init_pool():
    global pool
    pool = ConnectionPool(
        conninfo=DATABASE_URL,
        min_size=DB_POOL_MIN_SIZE,
        max_size=DB_POOL_MAX_SIZE,
        open=True,
        kwargs={"connect_timeout": 5}
    )

def close_pool():
    global pool
    if pool is not None:
        pool.close()

def get_db():
    if pool is None:
        raise RuntimeError("Database pool is not initialized")
    with pool.connection() as conn:
        yield conn

def get_connection():
    return psycopg.connect(
        DATABASE_URL,
        connect_timeout=5,
    )