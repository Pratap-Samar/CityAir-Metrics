from weather_client import fetch_weather

data = fetch_weather(28.6139,77.2090)

print(data)
print("==================CURRENT=================")
print(data["current"])