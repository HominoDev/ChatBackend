# server/app.py
# Libs
from fastapi import FastAPI
import logging

# Local modules
from server.db.engine import engine
from server.api.routers.root import router as root_router
from server.api.routers.auth import router as auth_router
from server.api.routers.services import router as services_router

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)
logger.info(f"Database engine initialized {engine}")

# FastAPI application instance
def create_app() -> FastAPI:
    app = FastAPI()
    app.include_router(root_router)
    app.include_router(auth_router)
    app.include_router(services_router)
    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server.app:app", host="127.0.0.1", port=8000, reload=True)
