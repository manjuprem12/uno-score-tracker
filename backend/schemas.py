from pydantic import BaseModel

class GameCreate(BaseModel):
    name: str

class PlayerCreate(BaseModel):
    name: str
    game_id: int

class ScoreCreate(BaseModel):
    player_id: int
    round: int
    score: int
