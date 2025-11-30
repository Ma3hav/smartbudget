"""
Application Runner - Start the SmartBudget backend server
"""

from app import create_app
import os

if __name__ == '__main__':
    app = create_app()
    
    if app:
        print("=" * 60)
        print("🚀 SmartBudget Backend Server")
        print("=" * 60)
        print(f"📊 Database: {app.config['DB_NAME']}")
        print(f"🌐 Environment: {os.getenv('FLASK_ENV', 'development')}")
        print(f"🔗 Server: http://{app.config['HOST']}:{app.config['PORT']}")
        print(f"📝 API Docs: http://{app.config['HOST']}:{app.config['PORT']}/")
        print("=" * 60)
        print("Press CTRL+C to stop the server")
        print("=" * 60)
        
        app.run(
            host=app.config['HOST'],
            port=app.config['PORT'],
            debug=app.config['DEBUG']
        )
    else:
        print("❌ Failed to create application")
        print("Please check your configuration and database connection")