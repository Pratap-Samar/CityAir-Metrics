@echo off

cd /d "D:\Project\CityAir Metrics"

call ".venv\Scripts\activate.bat"

python -m ingestion.pipeline