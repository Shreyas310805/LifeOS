from fastapi import APIRouter
from backend.database import SessionLocal
from backend.models import Medication

router = APIRouter(prefix="/health")

@router.post("/medication")
def add_medication(name: str, schedule: str):
    db = SessionLocal()
    med = Medication(name=name, schedule=schedule)
    db.add(med)
    db.commit()
    return med

@router.get("/medication")
def list_medications():
    db = SessionLocal()
    return db.query(Medication).all()
