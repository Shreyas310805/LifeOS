from fastapi import APIRouter, HTTPException
from backend.database import SessionLocal
from backend.models import Task
from backend.ai import classify_task, generate_quiz

router = APIRouter(prefix="/tasks", tags=["Tasks"])

POINTS = {
    "easy": 5,
    "medium": 10,
    "hard": 20
}

@router.post("/")
def add_task(title: str):
    db = SessionLocal()

    # AI decides difficulty
    difficulty = classify_task(title)

    if difficulty not in POINTS:
        difficulty = "medium"  # fallback safety

    task = Task(
        title=title,
        difficulty=difficulty,
        completed=False,
        points=POINTS[difficulty]
    )

    db.add(task)
    db.commit()
    db.refresh(task)
    db.close()

    return task


@router.get("/")
def list_tasks():
    db = SessionLocal()
    tasks = db.query(Task).all()
    db.close()
    return tasks


@router.post("/{task_id}/complete")
def complete_task(task_id: int):
    db = SessionLocal()
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        db.close()
        raise HTTPException(status_code=404, detail="Task not found")

    task.completed = True
    db.commit()
    db.refresh(task)
    db.close()

    quiz = generate_quiz(task.title)

    return {
        "task": task,
        "verification": quiz
    }
