from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="cityair_hourly_ingestion",
    default_args=default_args,
    description="Orchestrates the CityAir Metrics ingestion pipeline.",
    schedule="@hourly",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["cityair"],
) as dag:

    run_ingestion = BashOperator(
        task_id="run_ingestion",
        bash_command="cd /opt/airflow && python -m ingestion.pipeline",
        execution_timeout=timedelta(minutes=15),
    )
