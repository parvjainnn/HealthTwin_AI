"""Flask main application."""
import os
from flask import Flask, jsonify, redirect, render_template, request, url_for
from flask_login import LoginManager
from dotenv import load_dotenv
from .database import init_db, get_user_by_id

login_manager = LoginManager()


def _normalize_windows_path(path: str) -> str:
    """
    Convert extended Windows path prefixes (\\\\?\\) to normal absolute paths.
    Flask/Jinja template loaders can fail on extended prefix paths.
    """
    if os.name == 'nt' and path.startswith('\\\\?\\'):
        return path[4:]
    return path


def create_app():
    load_dotenv()
    base_dir = _normalize_windows_path(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    template_dir = _normalize_windows_path(os.path.join(base_dir, 'templates'))
    static_dir = _normalize_windows_path(os.path.join(base_dir, 'static_flask'))

    app = Flask(
        __name__,
        template_folder=template_dir,
        static_folder=static_dir
    )
    app.secret_key = os.environ.get('SECRET_KEY', 'healthtwin-secret-key-2024-change-in-production')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    app.config['PUBLIC_BASE_URL'] = os.environ.get('PUBLIC_BASE_URL', '').rstrip('/')
    app.config['PLAUSIBLE_DOMAIN'] = os.environ.get('PLAUSIBLE_DOMAIN', '').strip()
    app.config['PLAUSIBLE_SCRIPT_URL'] = os.environ.get('PLAUSIBLE_SCRIPT_URL', 'https://plausible.io/js/script.js').strip()

    @app.context_processor
    def inject_site_settings():
        """Expose deployment-safe URL and optional analytics settings to templates."""
        return {
            'site_url': app.config['PUBLIC_BASE_URL'] or request.url_root.rstrip('/'),
            'analytics_domain': app.config['PLAUSIBLE_DOMAIN'],
            'analytics_script_url': app.config['PLAUSIBLE_SCRIPT_URL'],
        }

    # Init DB
    init_db()

    # Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    @login_manager.unauthorized_handler
    def _unauthorized():
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Authentication required'}), 401
        return redirect(url_for(login_manager.login_view, next=request.url))

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

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('404.html'), 404

    @app.errorhandler(413)
    def request_too_large(error):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'The uploaded file is too large. Please choose a file smaller than 16 MB.'}), 413
        return render_template('upload_too_large.html'), 413

    return app
