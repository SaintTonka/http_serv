import aiohttp
import json
import os

DATA_FILE = "data_file.json"
API_URL = "https://api.open-meteo.com/v1/forecast"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"users": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def generate_user_id():
    data = load_data()
    return str(len(data["users"]) + 1)

async def receive_weather(lat: float, lon: float, **params):
    async with aiohttp.ClientSession() as session:
        async with session.get(API_URL, params={"latitude": lat, "longitude": lon, "current_weather": "true", **params}) as response:
            if response.status == 200:
                return await response.json()
            return {}