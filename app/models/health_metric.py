from datetime import datetime
from app import db


class HealthMetric(db.Model):
    __tablename__ = 'health_metrics'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    metric_type = db.Column(db.String(50), nullable=False)  # heart_rate, steps, sleep_hours, weight, blood_pressure
    value = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), nullable=False)  # bpm, count, hours, kg, mmHg

    recorded_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    source = db.Column(db.String(50), default='manual')  # manual, fitbit, apple_health, garmin

    # Optional context
    notes = db.Column(db.Text)
    metadata_json = db.Column(db.JSON)  # Additional context

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'metric_type': self.metric_type,
            'value': self.value,
            'unit': self.unit,
            'recorded_at': self.recorded_at.isoformat(),
            'source': self.source
        }