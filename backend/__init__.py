"""
Database Initialization Script
Creates default data and indexes
"""

import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from backend.app import create_app
from backend.utils.db_connection import db
from backend.models.user_model import User
from backend.models.category_model import Category
from bson import ObjectId


def init_database():
    """Initialize database with default data"""
    print("=" * 60)
    print("🔧 Initializing SmartBudget Database...")
    print("=" * 60)
    
    try:
        app = create_app()
        
        if not app:
            print("❌ Failed to create app")
            return False
        
        with app.app_context():
            try:
                # Test connection
                if not db.ping():
                    print("❌ Cannot connect to database")
                    print("Please check your MONGO_URI in .env file")
                    return False
                
                print("✅ Database connection successful")
                
                # Create indexes
                print("\n📊 Creating indexes...")
                db._create_indexes()
                print("✅ Indexes created")
                
                # Get collections
                users = db.get_collection('users')
                categories = db.get_collection('categories')
                expenses = db.get_collection('expenses')
                
                # ========================================
                # CREATE ADMIN USER
                # ========================================
                admin_email = "admin@smartbudget.com"
                existing_admin = users.find_one({'email': admin_email})
                
                if not existing_admin:
                    print(f"\n👤 Creating admin user: {admin_email}")
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
                    print(f"   📧 Email: {admin_email}")
                    print("   🔑 Password: Admin@123")
                else:
                    print(f"\nℹ️  Admin user already exists: {admin_email}")
                
                # ========================================
                # CREATE DEMO USER
                # ========================================
                demo_email = "demo@smartbudget.com"
                existing_demo = users.find_one({'email': demo_email})
                
                if not existing_demo:
                    print(f"\n👤 Creating demo user: {demo_email}")
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
                    print(f"   📧 Email: {demo_email}")
                    print("   🔑 Password: Demo@123")
                    
                    # Create default categories for demo user
                    print("\n📁 Creating default categories for demo user...")
                    default_categories = [
                        {'name': 'Food', 'icon': 'utensils', 'color': '#D2042D', 'budget_limit': 500},
                        {'name': 'Transport', 'icon': 'car', 'color': '#8B0000', 'budget_limit': 300},
                        {'name': 'Shopping', 'icon': 'shopping-bag', 'color': '#A52A2A', 'budget_limit': 400},
                        {'name': 'Bills', 'icon': 'file-text', 'color': '#C41E3A', 'budget_limit': 600},
                        {'name': 'Entertainment', 'icon': 'film', 'color': '#DC143C', 'budget_limit': 200},
                        {'name': 'Healthcare', 'icon': 'heart', 'color': '#B22222', 'budget_limit': 300},
                        {'name': 'Other', 'icon': 'more-horizontal', 'color': '#8B0000', 'budget_limit': 200}
                    ]
                    
                    for cat_data in default_categories:
                        category = Category(
                            user_id=demo_user_id,
                            name=cat_data['name'],
                            icon=cat_data['icon'],
                            color=cat_data['color'],
                            budget_limit=cat_data.get('budget_limit'),
                            is_default=True
                        )
                        categories.insert_one(category.to_mongo())
                    
                    print(f"✅ Created {len(default_categories)} default categories")
                else:
                    print(f"\nℹ️  Demo user already exists: {demo_email}")
                
                # ========================================
                # DISPLAY DATABASE STATISTICS
                # ========================================
                print("\n" + "=" * 60)
                print("📊 Database Statistics:")
                print("=" * 60)
                
                stats = db.get_stats()
                if stats:
                    for key, value in stats.items():
                        print(f"   {key}: {value}")
                
                # Count documents
                user_count = users.count_documents({})
                category_count = categories.count_documents({})
                expense_count = expenses.count_documents({})
                
                print(f"\n   📊 Collections Summary:")
                print(f"   - Users: {user_count}")
                print(f"   - Categories: {category_count}")
                print(f"   - Expenses: {expense_count}")
                
                print("\n" + "=" * 60)
                print("✅ Database initialization complete!")
                print("=" * 60)
                print("\n🚀 You can now:")
                print("   1. Start the backend server: python run.py")
                print("   2. Login with:")
                print("      - Admin: admin@smartbudget.com / Admin@123")
                print("      - Demo: demo@smartbudget.com / Demo@123")
                print("=" * 60)
                
                return True
                
            except Exception as e:
                print(f"\n❌ Error during initialization: {e}")
                import traceback
                traceback.print_exc()
                return False
                
    except Exception as e:
        print(f"\n❌ Error creating app: {e}")
        import traceback
        traceback.print_exc()
        return False


def reset_database():
    """Reset database - WARNING: Deletes all data!"""
    print("=" * 60)
    print("⚠️  WARNING: RESET DATABASE")
    print("=" * 60)
    print("This will delete ALL data from the database!")
    
    response = input("Are you sure you want to continue? (type 'YES' to confirm): ")
    
    if response != 'YES':
        print("❌ Reset cancelled")
        return False
    
    try:
        app = create_app()
        
        if not app:
            print("❌ Failed to create app")
            return False
        
        with app.app_context():
            # Test connection
            if not db.ping():
                print("❌ Cannot connect to database")
                return False
            
            print("\n🗑️  Dropping database...")
            db.drop_database()
            print("✅ Database dropped")
            
            print("\n🔧 Re-initializing database...")
            return init_database()
            
    except Exception as e:
        print(f"\n❌ Error resetting database: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_database_status():
    """Check database connection and status"""
    print("=" * 60)
    print("🔍 Checking Database Status...")
    print("=" * 60)
    
    try:
        app = create_app()
        
        if not app:
            print("❌ Failed to create app")
            return False
        
        with app.app_context():
            # Test connection
            if not db.ping():
                print("❌ Cannot connect to database")
                print("\n💡 Troubleshooting:")
                print("   1. Check if MongoDB is running")
                print("   2. Verify MONGO_URI in .env file")
                print("   3. Check network connectivity")
                return False
            
            print("✅ Database connection successful")
            
            # Get health check info
            health = db.health_check()
            print("\n📊 Database Health:")
            for key, value in health.items():
                print(f"   {key}: {value}")
            
            # Get collections
            users = db.get_collection('users')
            categories = db.get_collection('categories')
            expenses = db.get_collection('expenses')
            
            # Count documents
            user_count = users.count_documents({})
            category_count = categories.count_documents({})
            expense_count = expenses.count_documents({})
            
            print(f"\n📊 Collections:")
            print(f"   - Users: {user_count}")
            print(f"   - Categories: {category_count}")
            print(f"   - Expenses: {expense_count}")
            
            print("\n" + "=" * 60)
            print("✅ Database is operational")
            print("=" * 60)
            
            return True
            
    except Exception as e:
        print(f"\n❌ Error checking database: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    # Check command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'reset':
            success = reset_database()
        elif command == 'status':
            success = check_database_status()
        elif command == 'init':
            success = init_database()
        else:
            print("=" * 60)
            print("SmartBudget Database Initialization Tool")
            print("=" * 60)
            print("\nUsage:")
            print("   python backend/init_db.py [command]")
            print("\nCommands:")
            print("   init     - Initialize database with default data (default)")
            print("   reset    - Reset database (WARNING: Deletes all data)")
            print("   status   - Check database connection and status")
            print("\nExamples:")
            print("   python backend/init_db.py")
            print("   python backend/init_db.py init")
            print("   python backend/init_db.py status")
            print("   python backend/init_db.py reset")
            print("=" * 60)
            sys.exit(0)
    else:
        # Default: initialize database
        success = init_database()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)