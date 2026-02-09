from datetime import datetime
from app import db


class AIInsight(db.Model):
    __tablename__ = 'ai_insights'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    category = db.Column(db.String(50), nullable=False)  # nutrition, fitness, sleep, mental_health
    insight_type = db.Column(db.String(50))  # recommendation, prediction, anomaly, achievement

    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)

    # AI metadata
    confidence_score = db.Column(db.Float)  # 0.0 to 1.0
    model_version = db.Column(db.String(50))

    # User interaction
    is_read = db.Column(db.Boolean, default=False)
    is_applied = db.Column(db.Boolean, default=False)
    dismissed = db.Column(db.Boolean, default=False)

    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)