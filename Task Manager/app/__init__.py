from flask import Flask,render_template
from .config import Config
from .extensions import db, migrate, session_interface
from flask_wtf.csrf import CSRFProtect
from werkzeug.exceptions import HTTPException

def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request_error(error):
        return render_template('errors/400.html'), 400

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('errors/500.html'), 500

    @app.errorhandler(Exception)
    def handle_exception(error):
        # Pass through HTTP errors
        if isinstance(error, HTTPException):
            return error
        
        # Handle non-HTTP exceptions
        app.logger.error(f"Unexpected error: {str(error)}")
        return render_template('errors/500.html'), 500

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    csrf = CSRFProtect(app)
    # Mandatory: Set secret_key and session_cookie_name BEFORE initializing Flask-Session
    app.secret_key = app.config['SECRET_KEY']
    app.session_cookie_name = 'flask_session'  # <<-- Correct way to set cookie name

    # Initialize SQLAlchemy first
    db.init_app(app)
    migrate.init_app(app, db)

    # Configure Flask-Session
    app.config.update(
        SESSION_TYPE="sqlalchemy",
        SESSION_SQLALCHEMY=db,
        SESSION_SQLALCHEMY_TABLE="sessions",
        SESSION_PERMANENT=True,
        PERMANENT_SESSION_LIFETIME=3600,
    )

    # Initialize Flask-Session AFTER db
    session_interface.init_app(app)

    # Register blueprints
    from .routes.auth_routes import auth_bp
    from .routes.task_routes import task_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(task_bp)

    register_error_handlers(app)
    return app