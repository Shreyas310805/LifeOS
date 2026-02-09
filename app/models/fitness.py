from datetime import datetime
from app import db


class Fitness(db.Model):
    __tablename__ = 'fitness_activities'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    activity_type = db.Column(db.String(100), nullable=False)  # running, cycling, yoga, weights
    duration_minutes = db.Column(db.Integer)
    calories_burned = db.Column(db.Integer)

    # Intensity
    intensity = db.Column(db.String(20))  # low, moderate, high
    heart_rate_avg = db.Column(db.Integer)
    heart_rate_max = db.Column(db.Integer)

    # Details
    distance_km = db.Column(db.Float)
    steps = db.Column(db.Integer)
    notes = db.Column(db.Text)

    # AI features
    ai_generated_plan = db.Column(db.Boolean, default=False)
    ai_form_feedback = db.Column(db.Text)  # AI analysis of form

    performed_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)