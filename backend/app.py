"""
SmartBudget Backend Application
Main Flask application entry point
"""

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import config
from utils.db_connection import db
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
    # ✅ FIXED: Enable CORS so frontend (127.0.0.1:5500) can access backend
    # -------------------------------------------------------
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

    # Initialize JWT
    jwt = JWTManager(app)

    # Initialize database connection
    try:
        db.connect()
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
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

    # -------------------------------------------------------
    # Health Check
    # -------------------------------------------------------
    @app.route("/health", methods=["GET"])
    def health_check():
        db_status = db.ping()
        return jsonify({
            "status": "healthy" if db_status else "unhealthy",
            "database": "connected" if db_status else "disconnected",
            "version": "1.0.0"
        }), 200

    # Root endpoint
    @app.route("/", methods=["GET"])
    def index():
        return jsonify({
            "message": "SmartBudget API",
            "version": "1.0.0",
            "endpoints": {
                "auth": "/api/auth",
                "expenses": "/api/expenses",
                "categories": "/api/categories",
                "alerts": "/api/alerts",
                "savings": "/api/savings",
                "ml": "/api/ml",
                "health": "/health"
            }
        })

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
