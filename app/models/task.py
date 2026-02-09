from datetime import datetime
from app import db


class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))  # health, fitness, work, personal

    # Task properties
    priority = db.Column(db.String(20), default='medium')  # low, medium, high
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed

    # Scheduling
    due_date = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)

    # AI features
    ai_suggested = db.Column(db.Boolean, default=False)
    ai_priority_score = db.Column(db.Float)  # 0-1 score from AI

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def mark_complete(self):
        self.status = 'completed'
        self.completed_at = datetime.utcnow()