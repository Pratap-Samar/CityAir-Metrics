FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only the required directories and files
COPY api/ api/
COPY config/ config/
COPY database/ database/
COPY ingestion/ ingestion/
COPY processor/ processor/

# Run uvicorn
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
