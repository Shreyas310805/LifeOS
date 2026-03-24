from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    # Profile
    full_name = db.Column(db.String(100))
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(20))
    height_cm = db.Column(db.Float)
    weight_kg = db.Column(db.Float)
    activity_level = db.Column(db.String(50))  # sedentary, light, moderate, active

    # Goals & Preferences (stored as JSON)
    goals = db.Column(db.JSON, default=list)  # ['weight_loss', 'better_sleep']
    dietary_preferences = db.Column(db.JSON, default=list)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    health_metrics = db.relationship('HealthMetric', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    tasks = db.relationship('Task', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    fitness_activities = db.relationship('Fitness', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    social_posts = db.relationship('Social', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    ai_insights = db.relationship('AIInsight', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_health_score(self):
        """Calculate overall health score based on recent metrics"""
        # Implementation for health scoring algorithm
        pass

    def __repr__(self):
        return f'<User {self.username}>'