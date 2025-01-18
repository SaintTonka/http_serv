# Тестовое задание для стажера на позицию «Программист на языке Python»
1 step:
pip install -r requirements.txt
Build:
python3 script.py Linux
python script.py Win
Running tests
pytest tests/test.py -v

# МЕТОДЫ АПИ

1. Регистрация пользователя
Регистрирует нового пользователя.
URL: /register
Метод: POST

Тело запроса (JSON):
{
  "username": "your_username"
}

Успешный ответ:
{
  "user_id": "1"
}

Ошибки:
400 Bad Request: Если username не указан.

2. Получение текущей погоды
Возвращает текущую погоду по координатам.
URL: /weather
Метод: GET
Параметры запроса:
lat (float): Широта.
lon (float): Долгота.

Пример запроса:
GET /weather?lat=55.7558&lon=37.6173

Успешный ответ:
{
  "temperature": 15.0,
  "wind_speed": 5.0
}

Ошибки:
400 Bad Request: Если lat или lon не указаны или некорректны.

3. Добавление города для пользователя
Добавляет город для отслеживания погоды.
URL: /city
Метод: POST
Тело запроса (JSON):
{
  "user_id": "1",
  "city_name": "Moscow",
  "latitude": 55.7558,
  "longitude": 37.6173
}

Успешный ответ:
{
  "message": "City Moscow added for user 1"
}

Ошибки:
400 Bad Request: Если не указаны все обязательные параметры.
400 Bad Request: Если user_id не существует.

4. Получение списка городов пользователя
Возвращает список городов, добавленных пользователем.
URL: /cities
Метод: GET
Параметры запроса:
user_id (str): Идентификатор пользователя.
Пример запроса
GET /cities?user_id=1

Успешный ответ:
{
  "cities": ["Moscow"]
}

Ошибки:
400 Bad Request: Если user_id не указан или не существует.

5. Получение прогноза погоды для города
Возвращает прогноз погоды для указанного города и времени.
URL: /city_weather
Метод: GET
Параметры запроса:
user_id (str): Идентификатор пользователя.
city_name (str): Название города.
time (str): Время в формате YYYY-MM-DDTHH:MM.
params (str): Список параметров через запятую (например, temperature,windspeed).

Пример запроса:
GET /city_weather?user_id=1&city_name=Moscow&time=2025-01-17T12:00&params=temperature,windspeed

Успешный ответ:
{
  "temperature": 15.0,
  "windspeed": 5.0
}

Ошибки:
400 Bad Request: Если не указаны все обязательные параметры.
404 Not Found: Если город не найден или время отсутствует в прогнозе.
