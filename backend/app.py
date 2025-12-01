"""
SmartBudget Backend Application
Main Flask application entry point
FIXED VERSION with enhanced CORS and logging
"""

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from .config import config
from utils.db_connection import db
from utils.logger import setup_logger, setup_request_logging, setup_error_logging
import os


def create_app(config_name=None):
    """
    Application factory pattern
    """
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    # Create Flask app
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # -------------------------------------------------------
    # ✅ FIXED: Enhanced CORS Configuration
    # -------------------------------------------------------
    # Get allowed origins from config
    allowed_origins = app.config.get('CORS_ORIGINS', [])
    
    # Parse origins if it's a string
    if isinstance(allowed_origins, str):
        allowed_origins = [origin.strip() for origin in allowed_origins.split(',')]
    
    # Configure CORS with proper settings
    CORS(app, 
         resources={
             r"/api/*": {
                 "origins": allowed_origins if allowed_origins else "*",
                 "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                 "allow_headers": [
                     "Content-Type", 
                     "Authorization",
                     "Access-Control-Allow-Credentials"
                 ],
                 "expose_headers": [
                     "Content-Type", 
                     "Authorization",
                     "X-RateLimit-Limit",
                     "X-RateLimit-Remaining",
                     "X-RateLimit-Reset"
                 ],
                 "supports_credentials": True,
                 "max_age": 3600
             }
         })

    # -------------------------------------------------------
    # ✅ NEW: Setup Logging
    # -------------------------------------------------------
    setup_logger(app)
    
    if not app.debug:
        setup_request_logging(app)
    
    setup_error_logging(app)
    
    app.logger.info('Application configured successfully')

    # -------------------------------------------------------
    # Initialize JWT
    # -------------------------------------------------------
    jwt = JWTManager(app)
    
    # JWT error handlers
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        app.logger.warning(f'Invalid token: {error}')
        return jsonify({
            'success': False,
            'error': 'Invalid token',
            'message': 'The token is invalid or malformed'
        }), 401
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        app.logger.warning('Expired token')
        return jsonify({
            'success': False,
            'error': 'Token expired',
            'message': 'The token has expired. Please login again'
        }), 401
    
    @jwt.unauthorized_loader
    def unauthorized_callback(error):
        app.logger.warning(f'Unauthorized access: {error}')
        return jsonify({
            'success': False,
            'error': 'Unauthorized',
            'message': 'Authentication is required'
        }), 401

    # -------------------------------------------------------
    # Initialize database connection
    # -------------------------------------------------------
    try:
        db.connect()
        app.logger.info('Database connected successfully')
    except Exception as e:
        app.logger.error(f'Failed to connect to database: {e}')
        return None

    # -------------------------------------------------------
    # Register Blueprints
    # -------------------------------------------------------
    from routes import (
        auth_routes,
        expense_routes,
        category_routes,
        alert_routes,
        savings_routes,
        ml_routes
    )

    app.register_blueprint(auth_routes.bp, url_prefix="/api/auth")
    app.register_blueprint(expense_routes.bp, url_prefix="/api/expenses")
    app.register_blueprint(category_routes.bp, url_prefix="/api/categories")
    app.register_blueprint(alert_routes.bp, url_prefix="/api/alerts")
    app.register_blueprint(savings_routes.bp, url_prefix="/api/savings")
    app.register_blueprint(ml_routes.bp, url_prefix="/api/ml")
    
    app.logger.info('All blueprints registered')

    # -------------------------------------------------------
    # Health Check
    # -------------------------------------------------------
    @app.route("/health", methods=["GET"])
    def health_check():
        """Comprehensive health check endpoint"""
        db_status = db.ping()
        health_info = db.health_check() if db_status else {}
        
        return jsonify({
            "status": "healthy" if db_status else "unhealthy",
            "database": "connected" if db_status else "disconnected",
            "version": "1.0.0",
            "environment": config_name,
            "details": health_info
        }), 200 if db_status else 503

    # -------------------------------------------------------
    # Root endpoint
    # -------------------------------------------------------
    @app.route("/", methods=["GET"])
    def index():
        """API information endpoint"""
        return jsonify({
            "message": "SmartBudget API",
            "version": "1.0.0",
            "environment": config_name,
            "endpoints": {
                "auth": "/api/auth",
                "expenses": "/api/expenses",
                "categories": "/api/categories",
                "alerts": "/api/alerts",
                "savings": "/api/savings",
                "ml": "/api/ml",
                "health": "/health"
            },
            "documentation": {
                "swagger": "/api/docs",
                "health": "/health"
            }
        })
    
    # -------------------------------------------------------
    # ✅ NEW: API Documentation Endpoint
    # -------------------------------------------------------
    @app.route("/api/docs", methods=["GET"])
    def api_docs():
        """Simple API documentation"""
        return jsonify({
            "name": "SmartBudget API",
            "version": "1.0.0",
            "description": "AI-powered expense tracking and budget management API",
            "base_url": f"http://{app.config['HOST']}:{app.config['PORT']}/api",
            "authentication": "JWT Bearer Token",
            "endpoints": {
                "Authentication": {
                    "POST /auth/register": "Register new user",
                    "POST /auth/login": "Login user",
                    "GET /auth/me": "Get current user profile",
                    "PUT /auth/me": "Update user profile"
                },
                "Expenses": {
                    "POST /expenses/": "Create expense",
                    "GET /expenses/": "List expenses with filters",
                    "GET /expenses/<id>": "Get expense by ID",
                    "PUT /expenses/<id>": "Update expense",
                    "DELETE /expenses/<id>": "Delete expense",
                    "GET /expenses/statistics": "Get expense statistics"
                },
                "Categories": {
                    "POST /categories/": "Create category",
                    "GET /categories/": "List categories",
                    "GET /categories/<id>": "Get category by ID",
                    "PUT /categories/<id>": "Update category",
                    "DELETE /categories/<id>": "Delete category"
                },
                "Savings Goals": {
                    "POST /savings/": "Create savings goal",
                    "GET /savings/": "List savings goals",
                    "GET /savings/<id>": "Get goal by ID",
                    "PUT /savings/<id>": "Update goal",
                    "DELETE /savings/<id>": "Delete goal",
                    "POST /savings/<id>/transaction": "Add/withdraw savings"
                },
                "ML & Insights": {
                    "GET /ml/forecast": "Get 30-day expense forecast",
                    "GET /ml/anomalies": "Detect spending anomalies",
                    "GET /ml/insights": "Get spending insights",
                    "GET /ml/financial-health": "Calculate financial health score"
                }
            }
        })
    
    # -------------------------------------------------------
    # ✅ NEW: Global Error Handlers
    # -------------------------------------------------------
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({
            'success': False,
            'error': 'Not Found',
            'message': 'The requested resource was not found'
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({
            'success': False,
            'error': 'Method Not Allowed',
            'message': 'The method is not allowed for this endpoint'
        }), 405
    
    @app.errorhandler(500)
    def internal_error(e):
        app.logger.error(f'Internal Server Error: {str(e)}')
        return jsonify({
            'success': False,
            'error': 'Internal Server Error',
            'message': 'An internal error occurred'
        }), 500
    
    # -------------------------------------------------------
    # ✅ NEW: Request/Response Hooks
    # -------------------------------------------------------
    @app.before_request
    def before_request():
        """Log and validate requests"""
        from flask import request
        
        # Log request if not health check
        if request.path != '/health':
            app.logger.debug(f'Request: {request.method} {request.path}')
    
    @app.after_request
    def after_request(response):
        """Add security headers to all responses"""
        # Security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Add server header
        response.headers['X-Powered-By'] = 'SmartBudget/1.0'
        
        return response
    
    # -------------------------------------------------------
    # ✅ NEW: Graceful Shutdown Handler
    # -------------------------------------------------------
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        """Clean up resources on shutdown"""
        if exception:
            app.logger.error(f'Application error: {exception}')

    app.logger.info('Application initialization complete')
    
    return app


if __name__ == "__main__":
    app = create_app()

    if app:
        print("🚀 Starting SmartBudget Backend...")
        print(f"📊 Database: {app.config['DB_NAME']}")
        print(f"🌐 Environment: {os.getenv('FLASK_ENV', 'development')}")
        print(f"🔗 Server: http://{app.config['HOST']}:{app.config['PORT']}")

        app.run(
            host=app.config["HOST"],
            port=app.config["PORT"],
            debug=app.config["DEBUG"]
        )
    else:
        print("❌ Failed to create application")