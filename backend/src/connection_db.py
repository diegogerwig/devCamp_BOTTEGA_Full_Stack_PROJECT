import os
from flask_sqlalchemy import SQLAlchemy

# Global database instance
db = None
User = None
TimeEntry = None
DATABASE_TYPE = 'Mock Data'
IS_PERSISTENT = False

def init_database_connection(app):
    """Initialize database connection and models"""
    global db, User, TimeEntry, DATABASE_TYPE, IS_PERSISTENT
    
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    if not DATABASE_URL:
        print("⚠️ No DATABASE_URL found, using mock data")
        return None, None, None, 'Mock Data', False
    
    print(f"🔍 DATABASE_URL found: {DATABASE_URL[:50]}...")
    
    try:
        # Transform postgres:// to postgresql+pg8000://
        if DATABASE_URL.startswith('postgres://'):
            DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql+pg8000://', 1)
        elif DATABASE_URL.startswith('postgresql://'):
            DATABASE_URL = DATABASE_URL.replace('postgresql://', 'postgresql+pg8000://', 1)
        
        # Configure Flask-SQLAlchemy
        app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_pre_ping': True,
            'pool_recycle': 300,
        }
        
        # Try to import pg8000 and initialize database
        try:
            import pg8000
            db = SQLAlchemy(app)
            
            # Initialize models
            from src.models import init_models
            User, TimeEntry = init_models(db)
            
            DATABASE_TYPE = 'PostgreSQL'
            IS_PERSISTENT = True
            app.DATABASE_TYPE = DATABASE_TYPE
            
            print("✅ PostgreSQL with pg8000 configured!")
            
            return db, User, TimeEntry, DATABASE_TYPE, IS_PERSISTENT
            
        except ImportError as e:
            print(f"⚠️ pg8000 not available: {e}")
            return None, None, None, 'Mock Data', False
            
    except Exception as e:
        print(f"❌ PostgreSQL setup failed: {e}")
        return None, None, None, 'Mock Data', False

def get_database_info():
    """Returns current database configuration"""
    return {
        'db': db,
        'User': User,
        'TimeEntry': TimeEntry,
        'DATABASE_TYPE': DATABASE_TYPE,
        'IS_PERSISTENT': IS_PERSISTENT
    }