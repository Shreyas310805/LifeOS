from fastapi import APIRouter

router = APIRouter(prefix="/badges")

@router.get("/")
def badges():
    return [
        {"name": "Consistency", "criteria": "7 day streak"},
        {"name": "Fitness Starter", "criteria": "5000 steps"},
        {"name": "Task Master", "criteria": "20 tasks"}
    ]
