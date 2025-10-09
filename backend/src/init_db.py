"""
Database initialization and migration script for TimeTracer
This script handles database setup, schema validation, and automatic migrations
"""

import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

def get_database_url():
    """Get and validate DATABASE_URL from environment"""
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL environment variable not found")
        return None
    
    # Fix Render.com PostgreSQL URL format
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql+pg8000://', 1)
    elif DATABASE_URL.startswith('postgresql://'):
        DATABASE_URL = DATABASE_URL.replace('postgresql://', 'postgresql+pg8000://', 1)
    
    return DATABASE_URL

def create_app_for_db():
    """Create minimal Flask app for database operations"""
    app = Flask(__name__)
    
    DATABASE_URL = get_database_url()
    if not DATABASE_URL:
        return None, None
    
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    db = SQLAlchemy(app)
    return app, db

def check_column_exists(db, table_name, column_name):
    """Check if a column exists in a table"""
    try:
        result = db.session.execute(db.text(f"""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = '{table_name}' 
            AND column_name = '{column_name}'
        """))
        return result.fetchone() is not None
    except Exception as e:
        print(f"⚠️ Error checking column '{column_name}': {e}")
        return False

def migrate_password_column(app, db):
    """Migrate 'password' column to 'users_password' if needed"""
    with app.app_context():
        try:
            print("🔄 Checking password column migration...")
            
            has_users_password = check_column_exists(db, 'users', 'users_password')
            
            if not has_users_password:
                print("⚠️ Column 'users_password' does not exist")
                
                has_password = check_column_exists(db, 'users', 'password')
                
                if has_password:
                    print("✅ Renaming 'password' to 'users_password'...")
                    db.session.execute(db.text(
                        "ALTER TABLE users RENAME COLUMN password TO users_password"
                    ))
                    db.session.commit()
                    print("✅ Migration completed successfully!")
                else:
                    print("⚠️ Creating new column 'users_password'...")
                    db.session.execute(db.text(
                        "ALTER TABLE users ADD COLUMN users_password VARCHAR(255)"
                    ))
                    db.session.commit()
                    print("✅ Column created!")
            else:
                print("✅ Column 'users_password' already exists correctly")
                
        except Exception as e:
            print(f"❌ Error in migration: {e}")
            db.session.rollback()
            raise

def verify_tables(app, db):
    """Verify that required tables exist"""
    with app.app_context():
        try:
            print("\n🔍 Verifying database tables...")
            
            # Check if users table exists
            result = db.session.execute(db.text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'users'
            """))
            
            if not result.fetchone():
                print("❌ Table 'users' does not exist!")
                return False
            else:
                print("✅ Table 'users' exists")
            
            # Check if time_entries table exists
            result = db.session.execute(db.text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'time_entries'
            """))
            
            if not result.fetchone():
                print("❌ Table 'time_entries' does not exist!")
                return False
            else:
                print("✅ Table 'time_entries' exists")
            
            return True
            
        except Exception as e:
            print(f"❌ Error verifying tables: {e}")
            return False

def create_default_admin(app, db):
    """Create default admin user if no users exist"""
    with app.app_context():
        try:
            # Import here to avoid circular imports
            from data.mock_data import get_mock_users
            
            # Check if any users exist
            result = db.session.execute(db.text("SELECT COUNT(*) FROM users"))
            user_count = result.scalar()
            
            if user_count == 0:
                print("\n📝 No users found. Creating default admin...")
                
                bcrypt = Bcrypt()
                mock_users = get_mock_users()
                admin_user = mock_users[0]  # First user is always admin
                
                # Get password from environment or use default
                admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
                hashed_password = bcrypt.generate_password_hash(admin_password).decode('utf-8')
                
                db.session.execute(db.text("""
                    INSERT INTO users (name, email, users_password, role, department, status, created_at)
                    VALUES (:name, :email, :password, :role, :department, :status, NOW())
                """), {
                    'name': admin_user['name'],
                    'email': admin_user['email'],
                    'password': hashed_password,
                    'role': admin_user['role'],
                    'department': admin_user['department'],
                    'status': admin_user['status']
                })
                
                db.session.commit()
                print(f"✅ Admin user created: {admin_user['email']}")
                print(f"   Password: {admin_password}")
                print("   ⚠️ CHANGE THIS PASSWORD AFTER FIRST LOGIN!")
            else:
                print(f"\n✅ Database has {user_count} users")
                
        except Exception as e:
            print(f"❌ Error creating default admin: {e}")
            db.session.rollback()

def init_database(app=None, db=None):
    """Main initialization function"""
    print("\n" + "="*60)
    print("🚀 TimeTracer Database Initialization")
    print("="*60)
    
    # Create app and db if not provided
    if app is None or db is None:
        app, db = create_app_for_db()
        if app is None:
            print("❌ Could not create database connection")
            return False
    
    try:
        # Test database connection
        print("\n📊 Testing database connection...")
        with app.app_context():
            db.session.execute(db.text('SELECT 1'))
            print("✅ Database connection successful!")
        
        # Verify tables
        if not verify_tables(app, db):
            print("\n❌ Database tables are missing!")
            print("   Run database migrations or create tables manually")
            return False
        
        # Migrate password column
        migrate_password_column(app, db)
        
        # Create default admin if needed
        create_default_admin(app, db)
        
        print("\n" + "="*60)
        print("✅ Database initialization completed successfully!")
        print("="*60 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Database initialization failed: {e}")
        print("="*60 + "\n")
        return False

if __name__ == '__main__':
    print("Running database initialization as standalone script...")
    success = init_database()
    sys.exit(0 if success else 1)