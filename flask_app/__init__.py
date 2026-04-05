"""Flask main application."""
import os
from flask import Flask
from flask_login import LoginManager
from dotenv import load_dotenv
from .database import init_db, get_user_by_id

login_manager = LoginManager()


def create_app():
    load_dotenv()
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    app = Flask(
        __name__,
        template_folder=os.path.join(base_dir, 'templates'),
        static_folder=os.path.join(base_dir, 'static_flask')
    )
    app.secret_key = os.environ.get('SECRET_KEY', 'healthtwin-secret-key-2024-change-in-production')

    # Init DB
    init_db()

    # Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    from .user_model import User

    @login_manager.user_loader
    def load_user(user_id):
        data = get_user_by_id(int(user_id))
        if data:
            return User(data)
        return None

    # Register blueprints
    from .auth import auth_bp
    from .health import health_bp
    from .predictions import pred_bp
    from .chatbot import chat_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(pred_bp)
    app.register_blueprint(chat_bp)

    return app
