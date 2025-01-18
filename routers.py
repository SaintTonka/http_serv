from datetime import datetime, timedelta
from aiohttp import web
from utils import load_data, receive_weather, generate_user_id, save_data

app = web.Application()
router = web.RouteTableDef()
data_store = load_data()

@router.post("/register")
async def register_user(request):
    try:
        data = await request.json()
        print(data)
        username = data.get("username")
        if not username:
            return web.json_response({"error": "Username is required"}, status=400)

        user_id = generate_user_id()
        data_store["users"][user_id] = {
            "username": username,
            "cities": {}
        }
        save_data(data_store)
        return web.json_response({"user_id": user_id})
    except Exception as e:
        return web.json_response({"error": str(e)}, status=400)

@router.get("/weather")
async def get(request):
    try:
        lat = request.query.get("lat")
        lon = request.query.get("lon")
        
        if not lat or not lon:
            return web.json_response({"error": "Latitude and longitude are required"}, status=400)

        try:
            lat = float(lat)
            lon = float(lon)
        except ValueError:
            return web.json_response({"error": "Latitude and longitude must be valid numbers"}, status=400)

        weather = await receive_weather(lat, lon)
        current_weather = weather.get("current_weather")

        if current_weather:
            return web.json_response({
                "temperature": current_weather.get("temperature"),
                "wind_speed": current_weather.get("windspeed"),
            })
        return web.json_response({"error": "Weather data not available"}, status=400)

    except Exception as e:
        return web.json_response({"error": str(e)}, status=400)
    
@router.post("/city")
async def add_city(request):
    try:
        data = await request.json()
        user_id = data.get("user_id")
        city_name = data.get("city_name")
        lat = data.get("latitude")
        lon = data.get("longitude")

        if not (user_id and city_name and lat and lon):
            return web.json_response({"error": "Not all attributes (user_id and city_name and lat and lon)"}, status=400)

        if user_id not in data_store["users"]:
            return web.json_response({"error": "Invalid user ID"}, status=400)

        data_store["users"][user_id]["cities"][city_name] = {
            "latitude": lat,
            "longitude": lon,
            "forecast": None,
            "last_updated": None
        }
        save_data(data_store)
        return web.json_response({"message": f"City {city_name} added for user {user_id}"})
    except Exception as e:
        return web.json_response({"error": str(e)}, status=400)
    
@router.get("/cities")
async def list_cities(request):
    try:
        user_id = request.query.get("user_id")
        if not user_id or user_id not in data_store["users"]:
            return web.json_response({"error": "Invalid user ID"}, status=400)

        cities = list(data_store["users"][user_id]["cities"].keys())
        return web.json_response({"cities": cities})
    except Exception as e:
        return web.json_response({"error": str(e)}, status=400)
        
@router.get("/city_weather")
async def city_weather(request):
    try:
        user_id = request.query.get("user_id")
        city_name = request.query.get("city_name")
        time = request.query.get("time")
        params = request.query.get("params", "").split(",")
        
        if not (user_id and city_name and time):
            return web.json_response({"error": "Not all attributes (user_id, city_name, time)"}, status=400)
        
        if user_id not in data_store["users"] or city_name not in data_store["users"][user_id]["cities"]:
            return web.json_response({"error": "City not found for the user"}, status=404)
        
        city_data = data_store["users"][user_id]["cities"][city_name]
        forecast = city_data.get("forecast")

        if not forecast or datetime.now() - datetime.fromisoformat(city_data["last_updated"]) > timedelta(minutes=15):
            weather = await receive_weather(
                float(city_data["latitude"]),
                float(city_data["longitude"]),
                hourly="temperature,windspeed" 
            )
            city_data["forecast"] = weather.get("hourly", {})
            city_data["last_updated"] = datetime.now().isoformat()
            save_data(data_store)

        hourly_forecast = city_data["forecast"]
        if not hourly_forecast or "time" not in hourly_forecast:
            return web.json_response({"error": "Weather data not available"}, status=404)

        if time not in hourly_forecast["time"]:
            return web.json_response({"error": f"Time {time} not found in forecast data"}, status=404)

        time_index = hourly_forecast["time"].index(time)
        result = {param: hourly_forecast[param][time_index] for param in params if param in hourly_forecast}
        return web.json_response(result)

    except Exception as e:
        return web.json_response({"error": str(e)}, status=400)