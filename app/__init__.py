from flask import Flask
from flask_login import LoginManager
from flask_cors import CORS
from config import config
import firebase_admin
from firebase_admin import credentials, firestore

login_manager = LoginManager()
cors = CORS()

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    if not firebase_admin._apps:
        cred = credentials.Certificate(app.config['FIREBASE_CREDENTIALS'])
        firebase_admin.initialize_app(cred)
    
    app.config['db'] = firestore.client()

    login_manager.init_app(app)
    cors.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

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

    return app

@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.get(user_id)