"""
Database connection utility for MongoDB
"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import os
from dotenv import load_dotenv

load_dotenv()


class Database:
    """MongoDB database connection manager"""
    
    _instance = None
    _client = None
    _db = None
    
    def __new__(cls):
        """Singleton pattern for database connection"""
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize database connection"""
        if self._client is None:
            self.connect()
    
    def connect(self):
        """Establish connection to MongoDB"""
        try:
            mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/smartbudget')
            db_name = os.getenv('DB_NAME', 'smartbudget')
            
            # Create MongoDB client
            self._client = MongoClient(
                mongo_uri,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000,
                socketTimeoutMS=10000
            )
            
            # Test connection
            self._client.server_info()
            
            # Get database
            self._db = self._client[db_name]
            
            print(f"✅ Connected to MongoDB: {db_name}")
            
            # Create indexes
            self._create_indexes()
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            print(f"❌ Failed to connect to MongoDB: {e}")
            raise
        except Exception as e:
            print(f"❌ Unexpected error connecting to MongoDB: {e}")
            raise
    
    def _create_indexes(self):
        """Create database indexes for better performance"""
        try:
            # Users collection indexes
            self._db.users.create_index('email', unique=True)
            self._db.users.create_index('created_at')
            
            # Expenses collection indexes
            self._db.expenses.create_index([('user_id', 1), ('date', -1)])
            self._db.expenses.create_index('category')
            self._db.expenses.create_index('payment_type')
            self._db.expenses.create_index('created_at')
            
            # Categories collection indexes
            self._db.categories.create_index([('user_id', 1), ('name', 1)], unique=True)
            
            # Alerts collection indexes
            self._db.alerts.create_index([('user_id', 1), ('created_at', -1)])
            self._db.alerts.create_index('is_read')
            self._db.alerts.create_index('alert_type')
            
            # Savings goals collection indexes
            self._db.savings_goals.create_index([('user_id', 1), ('status', 1)])
            self._db.savings_goals.create_index('deadline')
            
            print("✅ Database indexes created")
            
        except Exception as e:
            print(f"⚠️ Warning: Could not create indexes: {e}")
    
    def get_db(self):
        """Get database instance"""
        if self._db is None:
            self.connect()
        return self._db
    
    def get_collection(self, collection_name):
        """Get a specific collection"""
        return self._db[collection_name]
    
    def close(self):
        """Close database connection"""
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
            print("✅ MongoDB connection closed")
    
    def ping(self):
        """Test database connection"""
        try:
            self._client.admin.command('ping')
            return True
        except Exception as e:
            print(f"❌ Database ping failed: {e}")
            return False
    
    def health_check(self):
        """Get database health information"""
        try:
            if not self._client or not self._db:
                return {
                    'status': 'disconnected',
                    'message': 'Database not connected'
                }
            
            # Test connection
            self._client.admin.command('ping')
            
            # Get server info
            server_info = self._client.server_info()
            
            return {
                'status': 'healthy',
                'database': self._db.name,
                'mongodb_version': server_info.get('version', 'unknown'),
                'connection': 'active'
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    def drop_database(self):
        """Drop the entire database (use with caution!)"""
        if self._client and self._db:
            self._client.drop_database(self._db.name)
            print(f"⚠️ Database '{self._db.name}' dropped")
    
    def get_stats(self):
        """Get database statistics"""
        try:
            stats = self._db.command('dbStats')
            return {
                'database': self._db.name,
                'collections': stats.get('collections', 0),
                'data_size': f"{stats.get('dataSize', 0) / 1024 / 1024:.2f} MB",
                'storage_size': f"{stats.get('storageSize', 0) / 1024 / 1024:.2f} MB",
                'indexes': stats.get('indexes', 0),
                'objects': stats.get('objects', 0)
            }
        except Exception as e:
            print(f"❌ Failed to get database stats: {e}")
            return {}


# Singleton instance
db = Database()


def get_db():
    """Helper function to get database instance"""
    return db.get_db()


def get_collection(collection_name):
    """Helper function to get collection"""
    return db.get_collection(collection_name)


# Collection getters for convenience
def get_users_collection():
    return get_collection('users')


def get_expenses_collection():
    return get_collection('expenses')


def get_categories_collection():
    return get_collection('categories')


def get_alerts_collection():
    return get_collection('alerts')


def get_savings_goals_collection():
    return get_collection('savings_goals')