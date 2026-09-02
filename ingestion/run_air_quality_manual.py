from ingestion.air_quality_client import fetch_air_quality


data = fetch_air_quality(
    28.6139,
    77.2090,
)

print(data)
print(data["current"])