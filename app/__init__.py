import os
from flask import Flask, redirect, url_for, render_template
from config import config_by_name, Config
from app.models import db, Admin, AppSetting
from app.routes import auth_bp, admin_bp, upload_bp, video_bp, api_bp

def create_app(config_name=None):
    """
    Application factory creating and configuring the Flask app instance.
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name['default']))

    # Ensure required static storage directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['QR_FOLDER'], exist_ok=True)

    # Initialize SQLAlchemy database
    db.init_app(app)

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(video_bp)
    app.register_blueprint(api_bp)

    # Root route redirect
    @app.route('/')
    def root_redirect():
        return redirect(url_for('admin.dashboard'))

    # Custom Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html', error=e), 404

    @app.errorhandler(413)
    def file_too_large(e):
        max_mb = app.config['MAX_CONTENT_LENGTH'] // (1024 * 1024)
        return render_template('errors/500.html', 
            error_title="File Too Large", 
            error_message=f"The selected file exceeds the maximum allowed upload size of {max_mb} MB."), 413

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html', error=e), 500

    # Auto-initialize database tables and default admin on startup
    with app.app_context():
        try:
            db.create_all()
            _init_default_admin(app)
        except Exception as e:
            app.logger.warning(f"Database table initialization notice: {e}")

    return app


def _init_default_admin(app):
    """Create default admin user if none exists in the database."""
    default_username = app.config.get('ADMIN_USERNAME', 'admin')
    default_password = app.config.get('ADMIN_PASSWORD', 'admin123')
    
    existing_admin = Admin.query.filter_by(username=default_username).first()
    if not existing_admin:
        admin = Admin(username=default_username)
        admin.set_password(default_password)
        db.session.add(admin)
        db.session.commit()
        app.logger.info(f"Default admin user '{default_username}' initialized successfully.")
