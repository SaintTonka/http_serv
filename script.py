from aiohttp import web
from routers import router

PORT = 8000

app = web.Application()
app.add_routes(router)

if __name__ == "__main__":
    try:
        web.run_app(app, port=PORT)
    except Exception as e:
        print(f"Server failed to start: {e}")