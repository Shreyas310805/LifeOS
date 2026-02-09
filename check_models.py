from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    """User model for authentication and profile"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    # Profile information
    full_name = db.Column(db.String(150))
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(20))
    height = db.Column(db.Float)  # in cm
    profile_image = db.Column(db.String(255))

    # Preferences
    timezone = db.Column(db.String(50), default='UTC')
    units = db.Column(db.String(20), default='metric')  # metric or imperial

    # Account status
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    email_verified = db.Column(db.Boolean, default=False)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    # Relationships
    health_metrics = db.relationship('HealthMetric', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    goals = db.relationship('Goal', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    workouts = db.relationship('Workout', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    meals = db.relationship('Meal', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    sleep_records = db.relationship('SleepRecord', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    water_intake = db.relationship('WaterIntake', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    mood_entries = db.relationship('MoodEntry', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        """Hash and set the user's password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if provided password matches the hash"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class HealthMetric(db.Model):
    """Track daily health metrics like weight, blood pressure, etc."""
    __tablename__ = 'health_metrics'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    # Metrics
    weight = db.Column(db.Float)  # in kg
    body_fat_percentage = db.Column(db.Float)
    muscle_mass = db.Column(db.Float)
    bmi = db.Column(db.Float)

    # Vital signs
    heart_rate = db.Column(db.Integer)  # bpm
    blood_pressure_systolic = db.Column(db.Integer)
    blood_pressure_diastolic = db.Column(db.Integer)
    blood_sugar = db.Column(db.Float)  # mg/dL

    # Additional metrics
    steps = db.Column(db.Integer)
    calories_burned = db.Column(db.Integer)

    # Notes
    notes = db.Column(db.Text)

    # Timestamps
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<HealthMetric {self.id} - User {self.user_id}>'


class Goal(db.Model):
    """User goals for health and fitness"""
    __tablename__ = 'goals'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))  # fitness, nutrition, sleep, mental_health, etc.

    # Goal details
    target_value = db.Column(db.Float)
    current_value = db.Column(db.Float)
    unit = db.Column(db.String(20))

    # Timeline
    start_date = db.Column(db.Date, nullable=False)
    target_date = db.Column(db.Date)
    completed_date = db.Column(db.Date)

    # Status
    status = db.Column(db.String(20), default='active')  # active, completed, abandoned
    priority = db.Column(db.String(20), default='medium')  # low, medium, high

    # Tracking
    progress_percentage = db.Column(db.Float, default=0.0)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Goal {self.title}>'


class Workout(db.Model):
    """Track workout sessions"""
    __tablename__ = 'workouts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    title = db.Column(db.String(200), nullable=False)
    workout_type = db.Column(db.String(50))  # cardio, strength, flexibility, sports, etc.
    duration = db.Column(db.Integer)  # in minutes

    # Metrics
    calories_burned = db.Column(db.Integer)
    distance = db.Column(db.Float)  # in km
    intensity = db.Column(db.String(20))  # low, moderate, high

    # Details
    exercises = db.Column(db.JSON)  # Store exercise details as JSON
    notes = db.Column(db.Text)

    # Rating
    difficulty_rating = db.Column(db.Integer)  # 1-10
    satisfaction_rating = db.Column(db.Integer)  # 1-10

    # Timestamps
    workout_date = db.Column(db.DateTime, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Workout {self.title}>'


class Meal(db.Model):
    """Track meals and nutrition"""
    __tablename__ = 'meals'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    meal_type = db.Column(db.String(50), nullable=False)  # breakfast, lunch, dinner, snack
    meal_name = db.Column(db.String(200))

    # Nutrition info
    calories = db.Column(db.Integer)
    protein = db.Column(db.Float)  # in grams
    carbohydrates = db.Column(db.Float)  # in grams
    fats = db.Column(db.Float)  # in grams
    fiber = db.Column(db.Float)  # in grams

    # Details
    ingredients = db.Column(db.JSON)  # List of ingredients
    recipe = db.Column(db.Text)
    photo_url = db.Column(db.String(255))
    notes = db.Column(db.Text)

    # Timestamps
    meal_time = db.Column(db.DateTime, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Meal {self.meal_type} - {self.meal_name}>'


class SleepRecord(db.Model):
    """Track sleep patterns"""
    __tablename__ = 'sleep_records'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    sleep_start = db.Column(db.DateTime, nullable=False)
    sleep_end = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Float)  # in hours

    # Sleep quality
    quality_rating = db.Column(db.Integer)  # 1-10
    deep_sleep_minutes = db.Column(db.Integer)
    light_sleep_minutes = db.Column(db.Integer)
    rem_sleep_minutes = db.Column(db.Integer)
    awake_minutes = db.Column(db.Integer)

    # Additional info
    notes = db.Column(db.Text)
    interrupted = db.Column(db.Boolean, default=False)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<SleepRecord {self.sleep_start.date()}>'


class WaterIntake(db.Model):
    """Track daily water intake"""
    __tablename__ = 'water_intake'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    amount = db.Column(db.Float, nullable=False)  # in ml

    # Timestamps
    intake_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<WaterIntake {self.amount}ml>'


class MoodEntry(db.Model):
    """Track mood and mental health"""
    __tablename__ = 'mood_entries'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    mood = db.Column(db.String(50), nullable=False)  # happy, sad, anxious, energetic, etc.
    energy_level = db.Column(db.Integer)  # 1-10
    stress_level = db.Column(db.Integer)  # 1-10

    # Activities and factors
    activities = db.Column(db.JSON)  # List of activities done
    factors = db.Column(db.JSON)  # Factors affecting mood

    # Notes
    notes = db.Column(db.Text)

    # Timestamps
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<MoodEntry {self.mood}>'


class AIRecommendation(db.Model):
    """Store AI-generated recommendations"""
    __tablename__ = 'ai_recommendations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    recommendation_type = db.Column(db.String(50), nullable=False)  # workout, meal, sleep, etc.
    title = db.Column(db.String(200))
    content = db.Column(db.Text, nullable=False)

    # Metadata
    based_on_data = db.Column(db.JSON)  # What data was used to generate this
    confidence_score = db.Column(db.Float)

    # Status
    is_read = db.Column(db.Boolean, default=False)
    is_followed = db.Column(db.Boolean, default=False)
    user_feedback = db.Column(db.Text)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)

    def __repr__(self):
        return f'<AIRecommendation {self.recommendation_type}>'