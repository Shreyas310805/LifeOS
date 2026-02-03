from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from backend.database import Base

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    difficulty = Column(String)
    completed = Column(Boolean, default=False)
    points = Column(Integer)

class FitnessLog(Base):
    __tablename__ = "fitness"
    id = Column(Integer, primary_key=True)
    steps = Column(Integer)
    calories = Column(Integer)
    workout = Column(String)

class Badge(Base):
    __tablename__ = "badges"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)

class Medication(Base):
    __tablename__ = "medications"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    schedule = Column(String)
