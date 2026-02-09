from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_cors import CORS
from config import config

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
cors = CORS()


def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    # Register blueprints
    from app.routes import auth, dashboard, tasks, fitness, social, health, nutrition, sleep, ai_chat

    app.register_blueprint(auth.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(tasks.bp, url_prefix='/tasks')
    app.register_blueprint(fitness.bp, url_prefix='/fitness')
    app.register_blueprint(social.bp, url_prefix='/social')
    app.register_blueprint(health.bp, url_prefix='/health')
    app.register_blueprint(nutrition.bp, url_prefix='/nutrition')
    app.register_blueprint(sleep.bp, url_prefix='/sleep')
    app.register_blueprint(ai_chat.bp, url_prefix='/ai')

    # Create tables
    with app.app_context():
        db.create_all()

    return app


# THIS IS THE CRITICAL FIX - Add user_loader callback
@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))