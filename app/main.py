from fastapi import FastAPI
from app.fetch_data import init_db, fetch_standings, get_standings_from_db

app = FastAPI(title="Pit Wall API")

@app.on_event("startup")
def startup():
    init_db()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/standings/{season}")
def standings(season: str = "current"):
    rows = get_standings_from_db(season)
    if not rows:
        fetch_standings(season)
        rows = get_standings_from_db(season)
    return [
        {"position": r[0], "driver": r[1], "constructor": r[2], "points": r[3]}
        for r in rows
    ]

@app.post("/refresh/{season}")
def refresh(season: str = "current"):
    rows = fetch_standings(season)
    return {"refreshed": len(rows)}