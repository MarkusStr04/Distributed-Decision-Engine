from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Decision
from pydantic import BaseModel
import redis
import json
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

# connection to Redis, same port and host as in worker.py
r = redis.Redis(host=os.getenv("REDIS_HOST"), port=int(os.getenv("REDIS_PORT")), decode_responses=True)

# data structure for incoming requests, using pydantic for validation
class UserData(BaseModel):
    income: int
    age: int
    debt: int

# receives a request, pushes the job to the Redis queue and responds immediately
# worker is responsible for processing the job and saving the result in Postgres
@app.post("/decision")
def make_decision(data: UserData):
    job = json.dumps(data.model_dump())  # converts pydantic model to JSON string
    r.lpush("decision_queue", job)       # pushes the job to the Redis queue
    return {"status": "queued"}

# returns all decisions from the database, ordered by creation time
# db is injected using FastAPI's dependency injection system, which ensures proper session management
@app.get("/decisions")
def get_decisions(db: Session = Depends(get_db)):
    decisions = db.query(Decision).order_by(Decision.created_at.desc()).all()
    return decisions

# returns a single decision by ID
# returns an error if the ID does not exist
@app.get("/decisions/{id}")
def get_decision(id: int, db: Session = Depends(get_db)):
    decision = db.query(Decision).filter(Decision.id == id).first()
    if not decision:
        return {"error": "Decision not found"}
    return decision