# CityAir Metrics

CityAir Metrics is an end-to-end data engineering and application project that ingests weather and air-quality data from external APIs, validates and transforms the data, stores it in PostgreSQL, processes it through an analytics layer, and exposes the results through a FastAPI backend and React dashboard.

The project also incorporates DevOps practices including Docker-based infrastructure, automated testing, and GitHub Actions CI.

---

## What I've Built

- Python data ingestion pipeline for weather and air-quality data
- Open-Meteo API integration with request retries and timeouts
- Pydantic-based data models and validation
- PostgreSQL database with relational constraints and duplicate-safe upserts
- Pipeline execution tracking and failure handling
- SQL-based analytics layer
- FastAPI REST API
- React + TypeScript dashboard
- Automated tests with Pytest
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
                 ▼         ▼
               Python Ingestion
                   Pipeline
                      │
             Transform + Validate
                      │
                      ▼
                  PostgreSQL
                      │
                      ▼
                 Analytics Layer
                      │
                      ▼
                   FastAPI
                      │
                      ▼
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
| Frontend         | React, TypeScript, Vite, CSS           |
| Testing          | Pytest                                 |
| DevOps           | Docker, Docker Compose, GitHub Actions |
| CI               | GitHub Actions                         |
| Data Source      | Open-Meteo                             |

---

## Data Engineering

The core pipeline follows:

```text
API
 ↓
Extract
 ↓
Transform
 ↓
Validate
 ↓
Load
 ↓
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
```

The `/analytics` endpoint provides the frontend with a combined latest weather and air-quality snapshot for each city.

Interactive Swagger documentation is available at:

```text
http://localhost:8000/docs
```

---

## Frontend

The frontend is built with React, TypeScript, and Vite.

Current functionality:

- City selection
- Current temperature
- PM2.5
- US AQI
- Weather details
- Air-quality details
- Refreshing data from the API
- Responsive dashboard layout

The frontend consumes data from the FastAPI backend rather than accessing the database directly.

---

## DevOps

DevOps is part of the project's development workflow and infrastructure.

### Docker

PostgreSQL runs through Docker Compose, providing a reproducible local database environment.

```bash
docker compose up -d
```

### CI

GitHub Actions runs the automated test suite on repository pushes and pull requests.

The CI environment provisions PostgreSQL as a service, initializes the project schema, installs dependencies, and runs the tests.

```text
Git Push / Pull Request
          │
          ▼
    GitHub Actions
          │
          ▼
    Python Environment
          │
          ▼
    PostgreSQL Service
          │
          ▼
    Database Schema
          │
          ▼
        Pytest
```

This ensures that database-dependent tests are also validated in a clean CI environment.

---

## Testing

The project uses Pytest across the main application layers.

Tests currently cover:

- API clients
- Data transformation
- Data validation
- Pydantic models
- Database repositories
- Analytics
- Pipeline behavior
- FastAPI endpoints

Run the test suite with:

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
- [x] Data transformation
- [x] Data validation
- [x] Database repositories
- [x] Duplicate-safe observation storage
- [x] Pipeline execution tracking
- [x] Ingestion pipeline
- [x] Analytics layer
- [x] FastAPI application
- [x] API response models
- [x] CORS configuration
- [x] Automated tests
- [x] GitHub Actions CI
- [x] Docker-based PostgreSQL environment
- [x] React + TypeScript frontend
- [x] Frontend API integration
- [x] City selection
- [x] Current weather and air-quality dashboard

## Current Focus

The current development focus is the frontend/dashboard layer.

The next backend/frontend integration work will focus on exposing historical observations so that the dashboard can display actual time-series data.

## Upcoming

- [ ] Historical weather API endpoint
- [ ] Historical air-quality API endpoint
- [ ] Interactive temperature chart
- [ ] Interactive PM2.5 chart
- [ ] Additional dashboard analytics
- [ ] Frontend refinement and UX improvements

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

Backend:

```text
http://localhost:8000
```

Swagger:

```text
http://localhost:8000/docs
```

### Frontend

From the `frontend` directory:

```bash
npm install
npm run dev
```

Frontend:

```text
http://localhost:5173
```

---

## Project Structure

```text
CityAir Metrics/
│
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
