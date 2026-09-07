# CityAir Metrics

CityAir Metrics is a data-engineering and full-stack application that monitors, processes, and visualizes air quality and weather conditions across India's state capitals.

Features include:

- SQL-based analytics layer
- FastAPI REST API
- React + TypeScript dashboard with Recharts and Leaflet Map
- Seamless Light/Dark Mode UI with dynamic theme-switching
- Automated tests with Pytest and isolated Test Databases
- Dockerized PostgreSQL development environment
- GitHub Actions CI with a PostgreSQL service
- Frontend-to-backend integration through REST APIs

---

## Architecture

```text
                Open-Meteo APIs
                /           \
               /             \
          Weather         Air Quality
               \             /
                \           /
                 ↓         ↓
               Python Ingestion
                   Pipeline
                      ↓
             Transform + Validate
                      ↓
                      ↓
                  PostgreSQL
                      ↓
                      ↓
                 Analytics Layer
                      ↓
                      ↓
                   FastAPI
                      ↓
                      ↓
               React + TypeScript
                   Dashboard
```

---

## Tech Stack

| Area             | Technologies                           |
| ---------------- | -------------------------------------- |
| Data Engineering | Python, Requests, Pydantic             |
| Database         | PostgreSQL 16, Psycopg                 |
| Backend          | FastAPI, Uvicorn                       |
| Frontend         | React, TypeScript, Vite, CSS, Leaflet, Recharts |
| Testing          | Pytest, python-dotenv                  |
| DevOps           | Docker, Docker Compose, GitHub Actions |
| CI               | GitHub Actions                         |
| Data Source      | Open-Meteo                             |

---

## Data Engineering

The core pipeline follows:

```text
API
 ↳
Extract
 ↳
Transform
 ↳
Validate
 ↳
Load
 ↳
Analytics
```

The pipeline processes weather and air-quality observations for configured cities.

It includes:

- API request handling
- Transformation into application models
- Data validation
- Database upserts
- Transaction handling
- Per-city failure handling
- Pipeline execution tracking
- Timestamp/freshness validation

The database uses uniqueness constraints together with upsert logic to make repeated pipeline executions safe.

---

## Database

PostgreSQL currently contains four main tables:

```text
cities
weather_observations
air_quality_observations
pipeline_runs
```

The schema separates city metadata, weather observations, air-quality observations, and pipeline execution metadata.

This allows the ingestion layer and analytics layer to operate independently while maintaining relational integrity.

---

## Analytics

The analytics layer provides SQL-based processing over the stored observations.

Current functionality includes:

- Latest weather by city
- Latest air quality by city
- Average weather metrics
- Average air-quality metrics
- Temperature trends
- PM2.5 trends
- Combined city snapshots

The analytics layer is kept separate from the ingestion pipeline so that data collection and analytical processing remain independently testable.

---

## Backend API

FastAPI exposes the processed data to the frontend.

### Current endpoints

```text
GET /
GET /cities
GET /weather/latest
GET /air-quality/latest
GET /analytics
GET /dashboard/map
GET /pipeline/runs
```

The `/dashboard/map` endpoint provides a streamlined list of cities strictly mapped for the interactive map. The API gracefully handles fetching historical trends and tracking the success of background ingestion scripts.

Interactive Swagger documentation is available at:

```text
http://localhost:8000/docs
```

---

## Frontend

The frontend is built with React, TypeScript, and Vite. It is highly responsive and adapts to 100vh constraints to prevent scrolling on the main view.

Current functionality:

- **Interactive Map**: Built with React-Leaflet and customized CARTO tiles that intelligently adapt between Light/Dark mode.
- **Dynamic Charting**: Recharts-powered area graphs displaying India's Temperature and AQI trends seamlessly filtered by 24H, 7D, or 30D intervals.
- **City Panel Details**: Auto-updating weather (temperature, humidity, precipitation, wind) and AQI metrics with dynamic color-coded indicator badges.
- **Pipeline Monitoring**: Real-time status list of backend Open-Meteo data ingestion tasks.
- **Theme Switching**: Dedicated Dark/Light mode toggle that updates CSS variables and map-rendering tiles immediately.
- **Kolkata Time Clock**: A live, globally-synced clock widget set exactly to `Asia/Kolkata` timezone.

---

## DevOps

DevOps is part of the project's development workflow and infrastructure.

### Docker

PostgreSQL runs through Docker Compose, providing a reproducible local database environment.

```bash
docker compose up -d
```

### CI & Isolated Testing

GitHub Actions runs the automated test suite on repository pushes and pull requests.

The CI environment provisions PostgreSQL as a service, initializes the project schema, installs dependencies, and runs the tests.

Locally, the project explicitly isolates development and test environments by spinning up a secondary `cityair_test` database. This prevents `pytest` from mutating or polluting the local `cityair` development dashboard.

```bash
python -m pytest
```

---

# Development Progress

The project is being developed incrementally, with each major layer being implemented and verified before moving to the next.

## Completed

- [x] Project structure and Python environment
- [x] PostgreSQL database setup
- [x] Database schema
- [x] Weather API client
- [x] Air-quality API client
- [x] Data models
- [x] Data validation
- [x] Database repositories
- [x] Pipeline execution tracking
- [x] Ingestion pipeline
- [x] Analytics layer
- [x] FastAPI application
- [x] API response models
- [x] CORS configuration
- [x] Automated tests
- [x] Database Isolation for Pytest
- [x] GitHub Actions CI
- [x] React + TypeScript frontend
- [x] Interactive Leaflet Map
- [x] Dark/Light Mode Theming
- [x] Interactive Temperature / PM2.5 charts
- [x] Pipeline Status Monitoring
- [x] Frontend Refinement and UX Improvements

## Upcoming

- [ ] Further expansion of Analytics features (e.g. Compare / Rankings)
- [ ] Automated Pipeline Cron Jobs
- [ ] Add more granular historical data fetching directly to frontend charts

The roadmap will evolve as the project develops.

---

## Running Locally

### Backend

Create and activate the Python environment:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start PostgreSQL:

```bash
docker compose up -d
```

Run the ingestion pipeline:

```bash
python -m ingestion.pipeline
```

Start FastAPI:

```bash
uvicorn api.main:app --reload
```

Backend: `http://localhost:8000`  
Swagger: `http://localhost:8000/docs`

### Frontend

From the `frontend` directory:

```bash
npm install
npm run dev
```

Frontend: `http://localhost:5173`

---

## Project Structure

```text
CityAir Metrics/
├── api/                    # FastAPI application
├── config/                 # Configuration
├── database/               # Schema, connection and repositories
├── ingestion/              # API clients, models, validation and pipeline
├── processor/              # Analytics
├── tests/                  # Automated tests
├── frontend/               # React + TypeScript dashboard
├── docker/                 # Docker-related files
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── docker-compose.yml
├── requirements.txt
├── run_pipeline.bat
└── README.md
```
