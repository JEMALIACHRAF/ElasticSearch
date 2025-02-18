import requests
import yaml
import json
import time
from datetime import datetime, timezone
from kafka import KafkaProducer

# Load API credentials and config
with open("../data_ingestion/config.yaml", "r") as file:
    config = yaml.safe_load(file)

USERNAME = config["username"]
PASSWORD = config["password"]
LOCATIONS = config["locations"]
PARAMETERS = config["parameters"]
OUTPUT_FORMAT = config["output_format"]
INTERVAL = config["interval"]

BASE_URL = "https://api.meteomatics.com"

# Set up Kafka producer
producer = KafkaProducer(
    bootstrap_servers="localhost:9093",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)
print("✅ Kafka fonctionne !")
def fetch_weather(lat, lon, location_name):
    """Fetch weather data for a given location."""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    url = f"{BASE_URL}/{timestamp}/{PARAMETERS}/{lat},{lon}/{OUTPUT_FORMAT}"

    response = requests.get(url, auth=(USERNAME, PASSWORD))

    if response.status_code == 200:
        data = response.json()

        # Extract weather parameters dynamically
        weather_data = {"timestamp": timestamp, "location": location_name, "latitude": lat, "longitude": lon}
        
        for item in data["data"]:
            param_name = item["parameter"]
            param_value = item["coordinates"][0]["dates"][0]["value"]
            weather_data[param_name] = param_value
        
        return weather_data
    else:
        print(f"⚠️ Error fetching data for {location_name}: {response.text}")
        return None

def send_to_kafka(data):
    """Send weather data to Kafka topic."""
    if data:
        producer.send("weather_data", value=data)
        print(f"📡 Sent to Kafka: {data}")

if __name__ == "__main__":
    while True:
        for location in LOCATIONS:
            weather_data = fetch_weather(location["lat"], location["lon"], location["name"])
            if weather_data:
                send_to_kafka(weather_data)

        print(f"⏳ Waiting {INTERVAL} seconds before next fetch...")
        time.sleep(INTERVAL)
