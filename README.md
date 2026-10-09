# CityAir Metrics

CityAir Metrics is an environmental monitoring and data-engineering platform focused on India's 36 state and union territory capitals. It integrates hourly weather and air quality (AQI) data ingestion, an analytics layer, RESTful API services, and a responsive React dashboard. The system is fully containerized using Docker, relies on PostgreSQL for persistent storage, and uses Apache Airflow for pipeline orchestration, with continuous integration driven by GitHub Actions.


**Backend & Data Engineering**






![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Docker Compose](https://img.shields.io/badge/Docker%20Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)
![Apache Airflow](https://img.shields.io/badge/Apache%20Airflow-017CEE?style=for-the-badge&logo=apacheairflow&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![pytest](https://img.shields.io/badge/pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white)

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React, TypeScript, Vite |
| **Backend** | FastAPI, Python |
| **Database** | PostgreSQL |
| **Data Ingestion** | Python, Open-Meteo |
| **Orchestration** | Apache Airflow |
| **Reverse Proxy** | Nginx |
| **Containers** | Docker, Docker Compose |
| **Testing** | Pytest |
| **CI** | GitHub Actions |

## Features

- **Extensive Coverage**: Monitors 36 Indian state and UT capitals.
- **Automated Ingestion**: Scheduled hourly retrieval of weather and air-quality data.
- **Historical Observations**: Persists time-series data to track environmental shifts over time.
- **Interactive Dashboard**: Visualizes national AQI mapping and top-level summary metrics.
- **City Reports**: Provides localized current conditions and a 5-day weather forecast.
- **AQI Rankings**: Highlights the best and worst cities by air quality over daily, weekly, and monthly periods.
- **City Comparison**: Allows side-by-side environmental analysis for up to 4 cities simultaneously.
- **Trend Analysis**: Visualizes multi-day trends in air quality and temperature.
- **Pipeline Monitoring**: Exposes pipeline execution status and metadata natively in the dashboard.
- **Responsive Frontend**: Seamless layout scaling from desktop to mobile screens with Light/Dark mode.
- **Application Backbone**: Powered by FastAPI, PostgreSQL, and orchestrated via Apache Airflow in Docker.

## Architecture

```mermaid
flowchart TD
    subgraph External
        OM[Open-Meteo APIs]
    end

    subgraph Orchestration
        Airflow[Apache Airflow DAG]
    end

    subgraph Data Engineering
        PI[Python Ingestion Pipeline]
        DB[(PostgreSQL)]
    end

    subgraph Application
        API[FastAPI Backend]
        Nginx[Nginx Reverse Proxy]
        React[React + TypeScript UI]
    end

    Airflow -- Triggers Hourly --> PI
    OM -- JSON Responses --> PI
    PI -- Persists Data --> DB
    API -- Queries --> DB
    Nginx -- Proxies /api --> API
    Nginx -- Serves --> React
    React -- API Calls --> Nginx
```

*Continuous Integration (CI) is implemented separately via **GitHub Actions**, automatically testing the backend against a disposable PostgreSQL service.*

## Screenshots

### Dashboard
![CityAir Metrics Dashboard](images/Screenshot%202026-10-06%20230635.png)

### City Report
![City Report](images/Screen%20Shot%202026-10-06%20at%2023.04.55.png)

### Rankings
![Rankings](images/Screenshot%202026-10-06%20230704.png)

### Compare Cities
![Compare Cities](images/Screen%20Shot%202026-10-06%20at%2023.06.07.png)

### Data Pipeline
![Data Pipeline](images/Screenshot%202026-10-06%20230652.png)

## Project Structure

```text
cityair-metrics/
├── api/             # FastAPI backend implementation (routes, models)
├── config/          # Centralized configuration and environment loading
├── dags/            # Apache Airflow DAG definitions
├── database/        # PostgreSQL connection pool and query repositories
├── docker/          # Dockerfiles for frontend, backend, and airflow
├── frontend/        # React + TypeScript single-page application
├── ingestion/       # Python data pipeline for Open-Meteo integration
├── processor/       # Data transformation and normalization logic
├── tests/           # Pytest integration and unit test suite
└── .github/         # GitHub Actions workflows for continuous integration
```

## Data Pipeline

CityAir Metrics relies on a data extraction, processing, and persistence pipeline:

1. **Airflow** triggers the hourly execution DAG.
2. The DAG invokes the modular **Python ingestion pipeline** (`ingestion.pipeline`).
3. The ingestion layer fetches raw weather and air-quality data from **Open-Meteo**.
4. The processor normalizes the data and persists it reliably into **PostgreSQL**.
5. The **FastAPI** backend exposes processed analytics through REST endpoints.
6. The **React** frontend dynamically renders dashboards, forecasts, rankings, and trends based on API responses.

## Airflow Orchestration

Apache Airflow is responsible for scheduling and orchestrating the existing ingestion logic.

**DAG configuration (`cityair_hourly_ingestion`):**
- **Schedule:** `@hourly`
- **Catchup:** `False`
- **Concurrency:** `max_active_runs=1`
- **Resilience:** 2 retries with a 5-minute delay.
- **Timeout:** 15 minutes execution timeout.
- **Execution:** Invokes `python -m ingestion.pipeline`.

## Docker Architecture

The entire stack is orchestrated via `docker-compose.yml`, deploying the following core services:

- **postgres**: The persistent database engine (PostgreSQL 16).
- **backend**: The FastAPI application serving REST endpoints.
- **frontend**: The Nginx web server acting as a reverse proxy for `/api` requests and serving the React bundle.
- **airflow-init**: A bootstrapper for database migrations and Airflow user creation.
- **airflow-scheduler**: Manages time-based DAG execution.
- **airflow-webserver**: Exposes the Airflow UI on port 8080.

## API Endpoints

The FastAPI backend routes requests internally, which Nginx proxies globally under the `/api` path. Major endpoints include:

- `GET /dashboard/summary`: High-level aggregated statistics.
- `GET /weather/forecast/{city_id}`: 5-day weather forecast data.
- `GET /cities`: List of the 36 monitored locations.
- `GET /dashboard/rankings?metric=aqi`: Best and worst city classifications.
- `GET /pipeline/runs`: Execution metadata for the data pipeline.

## Local Development

### Prerequisites
- [Git](https://git-scm.com/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- Node.js (for isolated frontend development, optional)
- Python 3.10+ (for isolated backend development, optional)

### Environment Configuration
The project requires a `.env` file at the repository root. This file is strictly for local development and is ignored by Git.

Create a `.env` file with the following placeholders:

```env
# PostgreSQL Configuration
POSTGRES_USER=your_dev_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=cityair

# Airflow Configuration
AIRFLOW_DB_PASSWORD=your_airflow_db_password
AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://your_dev_user:your_secure_password@postgres/cityair
AIRFLOW_UID=50000

# Backend Configuration
CORS_ORIGINS=http://localhost:5173,http://localhost
```

### Launching the Stack

Once your `.env` is configured, start the entire ecosystem using Docker Compose:

```bash
# Build and start all services in detached mode
docker compose up -d --build

# Check the status of the containers
docker compose ps
```

Access the application at `http://localhost`. The FastAPI documentation is available internally at `http://localhost:8000/docs`, and the Airflow UI at `http://localhost:8080`.

## Testing

Documented testing commands can be executed against the current repository state:

```bash
python -m pytest tests/

cd frontend
npm run lint
npm run build
cd ..

docker compose config
docker compose build
```

## Configuration and Security

- **.env File**: `.env` is local-only and ignored by Git.
- **Environment Variables**: Configuration is supplied through environment variables.
- **CORS**: CORS is configurable.
- **Secrets**: Secrets should not be committed.
- **Port Exposure**: PostgreSQL and Airflow should not be publicly exposed in a production deployment.

## Deployment Status

- Dockerized deployment is implemented.
- Local Docker Compose deployment is verified.
- Public cloud deployment has NOT yet been completed.
- Oracle Cloud Always Free is being evaluated as a future deployment target.
- No permanent public demo URL should be claimed yet.
- GitHub Actions currently provides CI, not deployment/CD.

## Engineering Highlights

- Dockerized multi-service architecture
- PostgreSQL persistence
- Airflow hourly orchestration
- Python ingestion pipeline
- FastAPI service layer
- React/TypeScript frontend
- Nginx reverse proxy
- GitHub Actions CI
- automated backend/frontend/Docker/Airflow validation
- 36-city master data

## Current Status

- [x] React dashboard
- [x] FastAPI backend
- [x] PostgreSQL
- [x] Weather/AQI ingestion
- [x] 36-city master data
- [x] Airflow hourly orchestration
- [x] Docker Compose
- [x] Nginx
- [x] GitHub Actions CI
- [x] Responsive frontend
- [ ] Public cloud deployment
- [ ] CI/CD deployment automation
