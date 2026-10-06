FROM apache/airflow:2.10.2-python3.11

USER root
# Install any system dependencies if needed (none strictly needed for now)

USER airflow
# Copy requirements but only install what's needed for ingestion to minimize conflicts
# We need requests, psycopg, psycopg_pool, pydantic, python-dotenv
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir "requests==2.32.5" "pydantic==2.11.7" "python-dotenv" "psycopg[binary]" "psycopg_pool"
