import pytest
from aiohttp import web
from routers import router
import json
from datetime import datetime, timedelta

@pytest.fixture(scope="function")
def clean_data_file():
    with open("data_file.json", "w") as f:
        json.dump({"users": {}}, f)

@pytest.fixture(scope="function")
async def client(aiohttp_client):
    app = web.Application()
    app.add_routes(router)
    return await aiohttp_client(app)

@pytest.mark.asyncio
async def test_register_user(client, clean_data_file):
    # Тест успешной регистрации пользователя
    response = await client.post("/register", json={"username": "test_user"})
    assert response.status == 200
    data = await response.json()
    assert "user_id" in data

    # Тест с отсутствующим username
    response = await client.post("/register", json={})
    assert response.status == 400
    data = await response.json()
    assert data["error"] == "Username is required"

@pytest.mark.asyncio
async def test_get_weather(client):
    # Тест успешного получения погоды
    response = await client.get("/weather?lat=55.7558&lon=37.6173")
    assert response.status == 200
    data = await response.json()
    assert "temperature" in data
    assert "wind_speed" in data

    # Тест с отсутствующими параметрами lat и lon
    response = await client.get("/weather")
    assert response.status == 400
    data = await response.json()
    assert data["error"] == "Latitude and longitude are required"

    # Тест с некорректными значениями lat и lon
    response = await client.get("/weather?lat=invalid&lon=invalid")
    assert response.status == 400
    data = await response.json()
    assert data["error"] == "Latitude and longitude must be valid numbers"

@pytest.mark.asyncio
async def test_add_city(client, clean_data_file):
    response = await client.post("/register", json={"username": "test_user"})
    user_id = (await response.json())["user_id"]

    # Тест успешного добавления города
    response = await client.post("/city", json={
        "user_id": user_id,
        "city_name": "Moscow",
        "latitude": 55.7558,
        "longitude": 37.6173
    })
    assert response.status == 200
    data = await response.json()
    assert data["message"] == "City Moscow added for user 1"

    # Тест с отсутствующими атрибутами
    response = await client.post("/city", json={})
    assert response.status == 400
    data = await response.json()
    assert data["error"] == "Not all attributes (user_id and city_name and lat and lon)"

    # Тест с неверным user_id
    response = await client.post("/city", json={
        "user_id": "999",
        "city_name": "Moscow",
        "latitude": 55.7558,
        "longitude": 37.6173
    })
    assert response.status == 400
    data = await response.json()
    assert data["error"] == "Invalid user ID"

@pytest.mark.asyncio
async def test_list_cities(client, clean_data_file):
    response = await client.post("/register", json={"username": "test_user"})
    user_id = (await response.json())["user_id"]
    await client.post("/city", json={
        "user_id": user_id,
        "city_name": "Moscow",
        "latitude": 55.7558,
        "longitude": 37.6173
    })

    # Тест успешного получения списка городов
    response = await client.get(f"/cities?user_id={user_id}")
    assert response.status == 200
    data = await response.json()
    assert data["cities"] == ["Moscow"]

    # Тест с неверным user_id
    response = await client.get("/cities?user_id=999")
    assert response.status == 400
    data = await response.json()
    assert data["error"] == "Invalid user ID"

@pytest.mark.asyncio
async def test_city_weather(client, clean_data_file):
    response = await client.post("/register", json={"username": "test_user"})
    user_id = (await response.json())["user_id"]
    await client.post("/city", json={
        "user_id": user_id,
        "city_name": "Moscow",
        "latitude": 55.7558,
        "longitude": 37.6173
    })

    time = datetime.now().strftime("%Y-%m-%dT%H:00") 

    # Тест успешного получения погоды для города
    response = await client.get(f"/city_weather?user_id={user_id}&city_name=Moscow&time={time}&params=temperature,windspeed")
    assert response.status == 200
    data = await response.json()
    assert "temperature" in data
    assert "windspeed" in data

    # Тест с неверным временем
    response = await client.get(f"/city_weather?user_id={user_id}&city_name=Moscow&time=2023-10-01T99:99&params=temperature,windspeed")
    assert response.status == 404
    data = await response.json()
    assert "error" in data

    # Тест с неверным city_name
    response = await client.get(f"/city_weather?user_id={user_id}&city_name=Unknown&time={time}&params=temperature,windspeed")
    assert response.status == 404
    data = await response.json()
    assert data["error"] == "City not found for the user"