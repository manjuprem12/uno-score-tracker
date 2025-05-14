from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse

import models
import schemas
from database import SessionLocal, engine

# Create tables in the database
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 1. Create a new game
@app.post("/games/")
def create_game(game: schemas.GameCreate, db: Session = Depends(get_db)):
    db_game = models.Game(name=game.name)
    db.add(db_game)
    db.commit()
    db.refresh(db_game)
    return db_game

# 2. Add a new player to a game
@app.post("/players/")
def add_player(player: schemas.PlayerCreate, db: Session = Depends(get_db)):
    game = db.query(models.Game).filter(models.Game.id == player.game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    new_player = models.Player(name=player.name, game_id=player.game_id)
    db.add(new_player)
    db.commit()
    db.refresh(new_player)
    return new_player

# 3. Add a score for a player in a round
@app.post("/scores/")
def add_score(score: schemas.ScoreCreate, db: Session = Depends(get_db)):
    player = db.query(models.Player).filter(models.Player.id == score.player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    new_score = models.Score(player_id=score.player_id, round=score.round, score=score.score)
    db.add(new_score)
    db.commit()
    db.refresh(new_score)
    return new_score

# 4. Get scoreboard for a game
@app.get("/games/{game_id}/scoreboard")
def get_scoreboard(game_id: int, db: Session = Depends(get_db)):
    game = db.query(models.Game).filter(models.Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    players = db.query(models.Player).filter(models.Player.game_id == game_id).all()
    result = []

    for player in players:
        scores = db.query(models.Score).filter(models.Score.player_id == player.id).all()
        total = sum([s.score for s in scores])
        rounds = [{"round": s.round, "score": s.score} for s in scores]

        result.append({
            "player_id": player.id,
            "name": player.name,
            "total_score": total,
            "scores": rounds
        })

    return JSONResponse(content=result)
