# server/app.py
# Libs
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import logging
import os

# Local modules
from server.db.engine import engine
from server.runtime.lifespan import lifespan
from server.api.routers.root     import router as root_router
from server.api.routers.auth     import router as auth_router
from server.api.routers.services import router as services_router
from server.api.routers.ws       import router as ws_router

# Logging configuration
LOG_FORMAT = ("%(asctime)s ""%(levelname)s ""%(name)s ""%(message)s")
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt="%Y-%m-%d %H:%M:%S")
log = logging.getLogger("app")
log.info("database engine initialized", extra={"engine": str(engine)})

# Security configuration
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
ENV = os.getenv("ENV", "development")

# FastAPI application instance
def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    
    # Security middleware: CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )
    
    # Security middleware: Trusted Host
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1"] + (os.getenv("ALLOWED_HOSTS", "").split(",") if os.getenv("ALLOWED_HOSTS") else [])
    )
    
    # Add security headers
    @app.middleware("http")
    async def add_security_headers(request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        if ENV == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response
    
    app.include_router(root_router)
    app.include_router(auth_router)
    app.include_router(services_router)
    app.include_router(ws_router)
    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server.app:app", host="127.0.0.1", port=8000, reload=True)
