from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.config import Settings, settings
from app.core.rate_limit import limiter
from app.core.database import get_db
from app.routers import (auth, commissioner, dungeon_bowl, inducements, leagues, mercenaries,
                         players, races, seasons, skills, star_players, teams)

ROUTERS = [auth, races, skills, inducements, star_players, mercenaries, dungeon_bowl,
           leagues, seasons, teams, commissioner, players]

def create_app(config: Settings) -> FastAPI:
    docs_off = config.is_production
    app = FastAPI(
        title="Blood Bowl League App",
        version="0.1.0",
        docs_url=None if docs_off else "/docs",
        redoc_url=None if docs_off else "/redoc",
        openapi_url=None if docs_off else "/openapi.json",
    )

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origins,
        allow_methods=["GET", "POST", "PATCH", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
    )

    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        if config.is_production:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
        return response

    for module in ROUTERS:
        app.include_router(module.router)

    @app.get('/health')
    def health_check():
        return {"status": "ok"}

    @app.get('/health/db')
    def health_check_db(db: Session = Depends(get_db)):
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    
    return app


app = create_app(settings)