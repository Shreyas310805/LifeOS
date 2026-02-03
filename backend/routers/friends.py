from fastapi import APIRouter

router = APIRouter(prefix="/leaderboard")

mock_scores = [
    {"name": "User A", "points": 3200},
    {"name": "User B", "points": 2900},
    {"name": "You", "points": 2800}
]

@router.get("/")
def leaderboard():
    return sorted(mock_scores, key=lambda x: x["points"], reverse=True)
