import requests
import yaml
import json
import os
import time
from datetime import datetime, timezone

# Load API credentials and config
with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

USERNAME = config["username"]
PASSWORD = config["password"]
LOCATIONS = config["locations"]
PARAMETERS = config["parameters"]
OUTPUT_FORMAT = config["output_format"]
INTERVAL = config["interval"]

BASE_URL = "https://api.meteomatics.com"

def fetch_weather(lat, lon, location_name):
    """Fetch weather data for a given location."""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    url = f"{BASE_URL}/{timestamp}/{PARAMETERS}/{lat},{lon}/{OUTPUT_FORMAT}"

    response = requests.get(url, auth=(USERNAME, PASSWORD))

    if response.status_code == 200:
        data = response.json()

        # Extracting weather parameters dynamically
        weather_data = {"timestamp": timestamp, "location": location_name, "latitude": lat, "longitude": lon}
        
        for item in data["data"]:
            param_name = item["parameter"]
            param_value = item["coordinates"][0]["dates"][0]["value"]
            weather_data[param_name] = param_value
        
        return weather_data
    else:
        print(f"⚠️ Error fetching data for {location_name}: {response.text}")
        return None

def save_data(data, filename="weather_data.json"):
    """Save weather data in a properly formatted JSON array."""
    if data:
        # Check if file exists and load existing data
        if os.path.exists(filename) and os.path.getsize(filename) > 0:
            with open(filename, "r", encoding="utf-8") as file:
                try:
                    existing_data = json.load(file)
                except json.JSONDecodeError:
                    existing_data = []  # In case of a corrupted file
        else:
            existing_data = []

        # Append new data
        existing_data.append(data)

        # Save updated data
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(existing_data, file, indent=4, ensure_ascii=False)  # Pretty print & UTF-8 encoding

if __name__ == "__main__":
    while True:
        for location in LOCATIONS:
            weather_data = fetch_weather(location["lat"], location["lon"], location["name"])
            if weather_data:
                print(f"✅ Data fetched: {weather_data}")
                save_data(weather_data)

        print(f"⏳ Waiting {INTERVAL} seconds before next fetch...")
        time.sleep(INTERVAL)
