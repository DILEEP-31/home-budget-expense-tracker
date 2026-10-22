"""
Application factory for Home Budget tracker.
Follows Flask application factory pattern.
"""
from flask import Flask
from flask_wtf.csrf import CSRFProtect
from app.config import Config

csrf = CSRFProtect()


def create_app(config_class=Config):
    """
    Creates and configures an instance of the Flask application.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize CSRF Protection
    csrf.init_app(app)

    # Register Blueprints
    from app.routes.main import main_bp
    from app.auth.routes import auth_bp
    from app.routes.budgets import budgets_bp
    from app.routes.api import api_bp
    from app.routes.reports import reports_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(budgets_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(reports_bp)

    # Context processor to provide auth state and global variables to all templates
    @app.context_processor
    def inject_globals():
        from flask import session
        return {
            'current_user_id': session.get('user_id'),
            'current_user_name': session.get('user_name'),
            'current_user_email': session.get('user_email'),
            'currency_symbol': app.config.get('CURRENCY_SYMBOL', '₹')
        }

    # Register Custom Jinja Template Filters
    from app.utils import format_currency as fc, format_date as fd

    @app.template_filter('currency')
    def jinja_format_currency(amount):
        return fc(amount, symbol=app.config.get('CURRENCY_SYMBOL', '₹'))

    @app.template_filter('date')
    def jinja_format_date(val):
        return fd(val)

    # Register Error Handlers
    from flask import render_template

    @app.errorhandler(400)
    def bad_request_error(error):
        # Handles CSRF validation failures and malformed requests
        return render_template('errors/400.html', message=str(error.description if hasattr(error, 'description') else "Bad Request")), 400

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('errors/500.html'), 500

    return app
