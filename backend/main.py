from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI
from backend.database import Base, engine
from backend.routers import tasks, fitness, friends, badges, health

Base.metadata.create_all(bind=engine)

app = FastAPI(title="LifeOS")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # hackathon-safe
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(tasks.router)
app.include_router(fitness.router)
app.include_router(friends.router)
app.include_router(badges.router)
app.include_router(health.router)
