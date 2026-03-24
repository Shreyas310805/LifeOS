from datetime import datetime
from app import db


class SleepSession(db.Model):
    __tablename__ = 'sleep_sessions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    sleep_start = db.Column(db.DateTime, nullable=False)
    sleep_end = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Integer)

    sleep_quality = db.Column(db.Integer)  # 1-10
    deep_sleep_minutes = db.Column(db.Integer)
    light_sleep_minutes = db.Column(db.Integer)
    rem_sleep_minutes = db.Column(db.Integer)
    awake_minutes = db.Column(db.Integer)

    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)