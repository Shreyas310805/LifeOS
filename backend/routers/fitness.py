from fastapi import APIRouter
from backend.database import SessionLocal
from backend.models import FitnessLog

router = APIRouter(prefix="/fitness")

@router.post("/")
def log_fitness(steps: int, calories: int, workout: str):
    db = SessionLocal()
    log = FitnessLog(steps=steps, calories=calories, workout=workout)
    db.add(log)
    db.commit()
    return log

@router.get("/")
def get_logs():
    db = SessionLocal()
    return db.query(FitnessLog).all()
