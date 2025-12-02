"""
Database Initialization Script
Creates default data and indexes
"""

from app import create_app
from utils.db_connection import db
from models.user_model import User
from models.category_model import Category
from bson import ObjectId
import os

def init_database():
    """Initialize database with default data"""
    print("🔧 Initializing SmartBudget Database...")
    
    app = create_app()
    
    if not app:
        print("❌ Failed to create app")
        return
    
    with app.app_context():
        try:
            # Test connection
            if not db.ping():
                print("❌ Cannot connect to database")
                return
            
            print("✅ Database connection successful")
            
            # Create indexes
            print("📊 Creating indexes...")
            db._create_indexes()
            
            # Get collections
            users = db.get_collection('users')
            categories = db.get_collection('categories')
            expenses = db.get_collection('expenses')
            
            # Check if admin user exists
            admin_email = "admin@smartbudget.com"
            existing_admin = users.find_one({'email': admin_email})
            
            if not existing_admin:
                print(f"👤 Creating admin user: {admin_email}")
                admin = User(
                    email=admin_email,
                    name="Admin User"
                )
                admin.set_password("Admin@123")
                admin.profile = {
                    'monthly_income': 5000,
                    'monthly_budget': 3000,
                    'currency': 'USD',
                    'timezone': 'UTC'
                }
                users.insert_one(admin.to_mongo())
                print("✅ Admin user created")
                print(f"   Email: {admin_email}")
                print("   Password: Admin@123")
            else:
                print("ℹ️  Admin user already exists")
            
            # Create demo user
            demo_email = "demo@smartbudget.com"
            existing_demo = users.find_one({'email': demo_email})
            
            if not existing_demo:
                print(f"👤 Creating demo user: {demo_email}")
                demo_user = User(
                    email=demo_email,
                    name="Demo User"
                )
                demo_user.set_password("Demo@123")
                demo_user.profile = {
                    'monthly_income': 4000,
                    'monthly_budget': 2500,
                    'currency': 'USD',
                    'timezone': 'UTC'
                }
                result = users.insert_one(demo_user.to_mongo())
                demo_user_id = result.inserted_id
                print("✅ Demo user created")
                print(f"   Email: {demo_email}")
                print("   Password: Demo@123")
                
                # Create default categories for demo user
                print("📁 Creating default categories for demo user...")
                default_categories = [
                    {'name': 'Food', 'icon': 'utensils', 'color': '#D2042D'},
                    {'name': 'Transport', 'icon': 'car', 'color': '#8B0000'},
                    {'name': 'Shopping', 'icon': 'shopping-bag', 'color': '#A52A2A'},
                    {'name': 'Bills', 'icon': 'file-text', 'color': '#C41E3A'},
                    {'name': 'Entertainment', 'icon': 'film', 'color': '#DC143C'},
                    {'name': 'Healthcare', 'icon': 'heart', 'color': '#B22222'},
                    {'name': 'Other', 'icon': 'more-horizontal', 'color': '#8B0000'}
                ]
                
                for cat_data in default_categories:
                    category = Category(
                        user_id=demo_user_id,
                        name=cat_data['name'],
                        icon=cat_data['icon'],
                        color=cat_data['color'],
                        is_default=True
                    )
                    categories.insert_one(category.to_mongo())
                
                print("✅ Default categories created")
            else:
                print("ℹ️  Demo user already exists")
            
            # Display stats
            print("\n📊 Database Statistics:")
            stats = db.get_stats()
            for key, value in stats.items():
                print(f"   {key}: {value}")
            
            print("\n" + "=" * 60)
            print("✅ Database initialization complete!")
            print("=" * 60)
            
        except Exception as e:
            print(f"❌ Error initializing database: {e}")

if __name__ == '__main__':
    init_database()