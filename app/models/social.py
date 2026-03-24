from datetime import datetime
from app import db


class Social(db.Model):
    __tablename__ = 'social_posts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    content = db.Column(db.Text, nullable=False)
    post_type = db.Column(db.String(50), default='update')  # achievement, challenge, milestone

    # Engagement
    likes_count = db.Column(db.Integer, default=0)
    comments_count = db.Column(db.Integer, default=0)

    # Sharing achievements
    achievement_data = db.Column(db.JSON)  # {metric: 'steps', value: 10000, date: '2024-01-01'}

    created_at = db.Column(db.DateTime, default=datetime.utcnow)