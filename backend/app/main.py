from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.rate_limit import limiter
from app.core.database import get_db
from app.routers import (races, skills, inducements, star_players, mercenaries, 
                         dungeon_bowl, leagues, seasons, teams, commissioner, auth,
                         players)

app = FastAPI(title="Blood Bowl League App", version="0.1.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.include_router(auth.router)
app.include_router(races.router)
app.include_router(skills.router)
app.include_router(inducements.router)
app.include_router(star_players.router)
app.include_router(mercenaries.router)
app.include_router(dungeon_bowl.router)
app.include_router(leagues.router)
app.include_router(seasons.router)
app.include_router(teams.router)
app.include_router(commissioner.router)
app.include_router(players.router)


@app.get('/health')
def health_check():
    return {"status": "ok"}

@app.get('/health/db')
def health_check_db(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "connected"}