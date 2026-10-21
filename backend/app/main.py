from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db
from app.routers import races, skills, inducements, star_players, mercenaries, dungeon_bowl

app = FastAPI(title="Blood Bowl League App", version="0.1.0")
app.include_router(races.router)
app.include_router(skills.router)
app.include_router(inducements.router)
app.include_router(star_players.router)
app.include_router(mercenaries.router)
app.include_router(dungeon_bowl.router)

@app.get('/health')
def health_check():
    return {"status": "ok"}

@app.get('/health/db')
def health_check_db(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "connected"}