import psycopg


from config.settings import DATABASE_URL


def get_connection():
    return psycopg.connect(
        DATABASE_URL,
        connect_timeout=5,
    )