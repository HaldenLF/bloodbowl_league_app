# bloodbowl_league_app
A fantasy football league application for the game of Bloodbowl


## Set up
   docker compose up -d
   cd backend
   alembic upgrade head
   python -m scripts.import_all
   - importer expects file labled "BB - Database.xlsx" in backend/data
   uvicorn app.main:app --reload --port 9000

