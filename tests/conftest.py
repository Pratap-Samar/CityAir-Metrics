import os
import psycopg
import pytest
from psycopg.errors import DuplicateDatabase
from dotenv import load_dotenv

# 1. Locate the project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 2. Explicitly load the project's .env file
dotenv_path = os.path.join(project_root, ".env")
load_dotenv(dotenv_path)

# 3. Override POSTGRES_DB for the test environment
os.environ["POSTGRES_DB"] = "cityair_test"

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """
    Creates and initializes the cityair_test database before tests run.
    This guarantees complete isolation from the production 'cityair' database.
    """
    # Use credentials from the environment (loaded via dotenv) without hardcoding defaults
    user = os.environ["POSTGRES_USER"]
    password = os.environ["POSTGRES_PASSWORD"]
    db = os.environ["POSTGRES_DB"]
    
    # Connect to the default 'postgres' database to create the test DB
    default_db_url = f"postgresql://{user}:{password}@localhost:5432/postgres"
    with psycopg.connect(default_db_url, autocommit=True) as conn:
        with conn.cursor() as cur:
            try:
                # db is known to be 'cityair_test', safe to interpolate
                cur.execute(f"CREATE DATABASE {db};")
            except DuplicateDatabase:
                pass
                
    # Connect to the test database and initialize a clean schema
    test_db_url = f"postgresql://{user}:{password}@localhost:5432/{db}"
    schema_path = os.path.join(project_root, "database", "schema.sql")
    
    with open(schema_path, "r") as f:
        schema_sql = f.read()
        
    with psycopg.connect(test_db_url) as conn:
        with conn.cursor() as cur:
            cur.execute("DROP SCHEMA public CASCADE;")
            cur.execute("CREATE SCHEMA public;")
            cur.execute(schema_sql)
        conn.commit()
