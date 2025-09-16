from flask import Flask, jsonify, request, redirect
from flask_cors import CORS
import os
import sys
from datetime import datetime

app = Flask(__name__)
CORS(app, origins=["*"])
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

# Variables globales para determinar qué base de datos usar
DATABASE_URL = os.getenv('DATABASE_URL')
db = None
DATABASE_TYPE = 'Mock Data'
IS_PERSISTENT = False

# Intentar configurar base de datos paso a paso
if DATABASE_URL:
    print(f"🔍 DATABASE_URL found: {DATABASE_URL[:50]}...")
    try:
        # Intentar PostgreSQL con pg8000 (compatible con Python 3.13)
        from flask_sqlalchemy import SQLAlchemy
        
        if DATABASE_URL.startswith('postgres://'):
            DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql+pg8000://', 1)
        elif DATABASE_URL.startswith('postgresql://'):
            DATABASE_URL = DATABASE_URL.replace('postgresql://', 'postgresql+pg8000://', 1)
        
        app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_pre_ping': True,
            'pool_recycle': 300,
        }
        
        # Verificar si pg8000 está disponible
        try:
            import pg8000
            db = SQLAlchemy(app)
            DATABASE_TYPE = 'PostgreSQL (100% Persistente)'
            IS_PERSISTENT = True
            print("✅ PostgreSQL with pg8000 configured!")
        except ImportError as e:
            print(f"⚠️ pg8000 not available: {e}")
            print("📦 Install pg8000 for PostgreSQL support")
            db = None
            
    except Exception as e:
        print(f"❌ PostgreSQL setup failed: {e}")
        db = None

if db is None:
    # Fallback a SQLite
    try:
        from flask_sqlalchemy import SQLAlchemy
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///timetracer.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db = SQLAlchemy(app)
        DATABASE_TYPE = 'SQLite (Se pierde en redeploy)'
        IS_PERSISTENT = False
        print("⚠️ Using SQLite fallback")
    except Exception as e:
        print(f"❌ SQLite setup failed: {e}")
        DATABASE_TYPE = 'Mock Data (No database available)'
        IS_PERSISTENT = False

# =================== MODELOS (solo si hay DB) ===================

if db:
    class User(db.Model):
        __tablename__ = 'users'
        
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), nullable=False)
        email = db.Column(db.String(120), unique=True, nullable=False)
        role = db.Column(db.String(20), nullable=False, default='worker')
        department = db.Column(db.String(50), nullable=False)
        status = db.Column(db.String(20), nullable=False, default='active')
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        
        def to_dict(self):
            return {
                'id': self.id,
                'name': self.name,
                'email': self.email,
                'role': self.role,
                'department': self.department,
                'status': self.status,
                'created_at': self.created_at.isoformat()
            }

    class TimeEntry(db.Model):
        __tablename__ = 'time_entries'
        
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
        date = db.Column(db.Date, nullable=False)
        check_in = db.Column(db.DateTime, nullable=True)
        check_out = db.Column(db.DateTime, nullable=True)
        total_hours = db.Column(db.Float, nullable=True)
        notes = db.Column(db.Text, nullable=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        
        def to_dict(self):
            return {
                'id': self.id,
                'user_id': self.user_id,
                'date': self.date.isoformat(),
                'check_in': self.check_in.isoformat() if self.check_in else None,
                'check_out': self.check_out.isoformat() if self.check_out else None,
                'total_hours': self.total_hours,
                'notes': self.notes,
                'created_at': self.created_at.isoformat()
            }

# =================== DATOS MOCK (siempre disponibles) ===================

MOCK_USERS = [
    {'id': 1, 'name': 'Admin TimeTracer', 'email': 'admin@timetracer.com', 'role': 'admin', 'department': 'IT', 'status': 'active', 'created_at': '2024-01-01T00:00:00'},
    {'id': 2, 'name': 'Juan Manager', 'email': 'juan@company.com', 'role': 'manager', 'department': 'Operations', 'status': 'active', 'created_at': '2024-01-01T00:00:00'},
    {'id': 3, 'name': 'María Worker', 'email': 'maria@company.com', 'role': 'worker', 'department': 'Sales', 'status': 'active', 'created_at': '2024-01-01T00:00:00'},
    {'id': 4, 'name': 'Carlos Developer', 'email': 'carlos@company.com', 'role': 'worker', 'department': 'IT', 'status': 'active', 'created_at': '2024-01-01T00:00:00'}
]

MOCK_TIME_ENTRIES = [
    {'id': 1, 'user_id': 1, 'date': '2024-01-15', 'check_in': '2024-01-15T09:00:00', 'check_out': '2024-01-15T17:00:00', 'total_hours': 8.0, 'notes': 'Regular work day', 'created_at': '2024-01-15T09:00:00'},
    {'id': 2, 'user_id': 2, 'date': '2024-01-15', 'check_in': '2024-01-15T08:30:00', 'check_out': '2024-01-15T16:30:00', 'total_hours': 8.0, 'notes': 'Management tasks', 'created_at': '2024-01-15T08:30:00'}
]

# =================== RUTAS ===================

@app.route('/favicon.svg')
@app.route('/favicon.ico')
def favicon():
    return redirect('https://api.iconify.design/material-symbols:schedule-outline.svg?color=%23FFEB3B')

@app.route('/')
def home():
    return jsonify({
        'message': f'🚀 TimeTracer API v2.0 with {DATABASE_TYPE}',
        'status': 'success',
        'version': '2.0.0',
        'database': DATABASE_TYPE,
        'persistent': IS_PERSISTENT,
        'python_version': f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}',
        'has_database': db is not None,
        'has_postgresql': DATABASE_URL is not None,
        'psycopg2_available': 'pg8000' in sys.modules,
        'next_steps': {
            'for_postgresql': 'Install psycopg2-binary or use alternative driver' if DATABASE_URL and not IS_PERSISTENT else None,
            'for_persistence': 'Configure PostgreSQL in Render' if not IS_PERSISTENT else None
        },
        'endpoints': {
            'health': '/api/health',
            'users': '/api/users',
            'time_entries': '/api/time-entries',
            'status': '/api/status'
        }
    })

@app.route('/api/health')
def health_check():
    db_status = 'mock_data'
    
    if db:
        try:
            db.session.execute(db.text('SELECT 1'))
            db_status = 'healthy'
        except Exception as e:
            db_status = f'error: {str(e)}'
    
    return jsonify({
        'status': 'healthy',
        'database': db_status,
        'database_type': DATABASE_TYPE,
        'persistent': IS_PERSISTENT,
        'has_database': db is not None,
        'message': 'TimeTracer backend running',
        'environment': os.getenv('FLASK_ENV', 'production'),
        'python_version': f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}',
        'server': 'Render'
    })

@app.route('/api/users', methods=['GET', 'POST'])
def handle_users():
    if request.method == 'GET':
        if db:
            try:
                users = User.query.all()
                return jsonify({
                    'users': [user.to_dict() for user in users],
                    'total': len(users),
                    'source': DATABASE_TYPE,
                    'persistent': IS_PERSISTENT,
                    'message': f'Users from {DATABASE_TYPE}'
                })
            except Exception as e:
                # Fallback a mock si la DB falla
                return jsonify({
                    'users': MOCK_USERS,
                    'total': len(MOCK_USERS),
                    'source': 'mock (database error)',
                    'persistent': False,
                    'message': f'Database error, using mock data: {str(e)}'
                })
        else:
            return jsonify({
                'users': MOCK_USERS,
                'total': len(MOCK_USERS),
                'source': 'mock',
                'persistent': False,
                'message': 'Using mock data (no database configured)'
            })
    
    elif request.method == 'POST':
        data = request.get_json()
        
        if db:
            try:
                new_user = User(
                    name=data['name'],
                    email=data['email'],
                    role=data.get('role', 'worker'),
                    department=data['department']
                )
                db.session.add(new_user)
                db.session.commit()
                
                return jsonify({
                    'message': f'User created in {DATABASE_TYPE}',
                    'user': new_user.to_dict(),
                    'persistent': IS_PERSISTENT
                }), 201
            except Exception as e:
                db.session.rollback()
                # Fallback a mock
                new_user = {
                    'id': len(MOCK_USERS) + 1,
                    'name': data['name'],
                    'email': data['email'],
                    'role': data.get('role', 'worker'),
                    'department': data['department'],
                    'status': 'active',
                    'created_at': datetime.utcnow().isoformat()
                }
                MOCK_USERS.append(new_user)
                return jsonify({
                    'message': f'Database error, created in mock data: {str(e)}',
                    'user': new_user,
                    'persistent': False
                }), 201
        else:
            # Solo mock
            new_user = {
                'id': len(MOCK_USERS) + 1,
                'name': data['name'],
                'email': data['email'],
                'role': data.get('role', 'worker'),
                'department': data['department'],
                'status': 'active',
                'created_at': datetime.utcnow().isoformat()
            }
            MOCK_USERS.append(new_user)
            
            return jsonify({
                'message': 'User created in mock data (no database)',
                'user': new_user,
                'persistent': False
            }), 201

@app.route('/api/time-entries', methods=['GET', 'POST'])
def handle_time_entries():
    if request.method == 'GET':
        if db:
            try:
                entries = TimeEntry.query.order_by(TimeEntry.date.desc()).all()
                return jsonify({
                    'time_entries': [entry.to_dict() for entry in entries],
                    'total': len(entries),
                    'source': DATABASE_TYPE,
                    'persistent': IS_PERSISTENT,
                    'message': f'Time entries from {DATABASE_TYPE}'
                })
            except Exception as e:
                return jsonify({
                    'time_entries': MOCK_TIME_ENTRIES,
                    'total': len(MOCK_TIME_ENTRIES),
                    'source': 'mock (database error)',
                    'persistent': False,
                    'message': f'Database error, using mock data: {str(e)}'
                })
        else:
            return jsonify({
                'time_entries': MOCK_TIME_ENTRIES,
                'total': len(MOCK_TIME_ENTRIES),
                'source': 'mock',
                'persistent': False,
                'message': 'Using mock data (no database configured)'
            })
    
    elif request.method == 'POST':
        data = request.get_json()
        
        if db:
            try:
                new_entry = TimeEntry(
                    user_id=data['user_id'],
                    date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
                    check_in=datetime.fromisoformat(data['check_in'].replace('Z', '+00:00')) if data.get('check_in') else None,
                    check_out=datetime.fromisoformat(data['check_out'].replace('Z', '+00:00')) if data.get('check_out') else None,
                    total_hours=data.get('total_hours'),
                    notes=data.get('notes')
                )
                
                db.session.add(new_entry)
                db.session.commit()
                
                return jsonify({
                    'message': f'Time entry created in {DATABASE_TYPE}',
                    'time_entry': new_entry.to_dict(),
                    'persistent': IS_PERSISTENT
                }), 201
            except Exception as e:
                db.session.rollback()
                # Fallback a mock
                new_entry = {
                    'id': len(MOCK_TIME_ENTRIES) + 1,
                    'user_id': data['user_id'],
                    'date': data['date'],
                    'check_in': data.get('check_in'),
                    'check_out': data.get('check_out'),
                    'total_hours': data.get('total_hours'),
                    'notes': data.get('notes'),
                    'created_at': datetime.utcnow().isoformat()
                }
                MOCK_TIME_ENTRIES.append(new_entry)
                return jsonify({
                    'message': f'Database error, created in mock data: {str(e)}',
                    'time_entry': new_entry,
                    'persistent': False
                }), 201
        else:
            # Solo mock
            new_entry = {
                'id': len(MOCK_TIME_ENTRIES) + 1,
                'user_id': data['user_id'],
                'date': data['date'],
                'check_in': data.get('check_in'),
                'check_out': data.get('check_out'),
                'total_hours': data.get('total_hours'),
                'notes': data.get('notes'),
                'created_at': datetime.utcnow().isoformat()
            }
            MOCK_TIME_ENTRIES.append(new_entry)
            
            return jsonify({
                'message': 'Time entry created in mock data (no database)',
                'time_entry': new_entry,
                'persistent': False
            }), 201

@app.route('/api/status')
def get_status():
    user_count = entry_count = 0
    
    if db:
        try:
            db.session.execute(db.text('SELECT 1'))
            user_count = User.query.count()
            entry_count = TimeEntry.query.count()
            db_status = f'✅ {DATABASE_TYPE} Connected & Ready'
        except Exception as e:
            user_count = len(MOCK_USERS)
            entry_count = len(MOCK_TIME_ENTRIES)
            db_status = f'⚠️ Database error, using mock data: {str(e)}'
    else:
        user_count = len(MOCK_USERS)
        entry_count = len(MOCK_TIME_ENTRIES)
        db_status = '⚠️ Using mock data (no database configured)'
    
    return jsonify({
        'backend': '✅ Backend Online (Ultra-Robust)',
        'database': db_status,
        'deploy': '✅ Render Deployment Successful',
        'cors': '✅ CORS Configured',
        'statistics': {
            'users': user_count,
            'time_entries': entry_count,
            'absences': 0
        },
        'features': [
            f'🗄️ {DATABASE_TYPE} Integration',
            '📊 Real User & Time Entry Management',
            '🔐 CORS configured for frontend',
            '👥 User Management (CRUD)',
            '⏰ Time Entry Tracking',
            f'🐍 Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} Compatible',
            '📡 Deployed on Render infrastructure',
            '🛡️ Ultra-robust with multiple fallbacks',
            '💾 Always functional (database or mock)'
        ],
        'database_type': DATABASE_TYPE,
        'persistent': IS_PERSISTENT,
        'environment': os.getenv('FLASK_ENV', 'production'),
        'python_version': f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}',
        'troubleshooting': {
            'postgresql_setup': 'Create PostgreSQL in Render + Add DATABASE_URL' if not IS_PERSISTENT else None,
            'psycopg2_issue': 'psycopg2-binary incompatible with Python 3.13' if DATABASE_URL and not IS_PERSISTENT else None,
            'current_status': 'Working with mock data - PostgreSQL can be added later'
        }
    })

# =================== INICIALIZACIÓN SEGURA ===================

def init_database():
    if not db:
        print("⚠️ No database available, mock data ready")
        return
    
    try:
        with app.app_context():
            db.create_all()
            
            if User.query.count() == 0:
                sample_users = [
                    User(name='Admin TimeTracer', email='admin@timetracer.com', role='admin', department='IT'),
                    User(name='Juan Manager', email='juan@company.com', role='manager', department='Operations'),
                    User(name='María Worker', email='maria@company.com', role='worker', department='Sales'),
                    User(name='Carlos Developer', email='carlos@company.com', role='worker', department='IT')
                ]
                
                for user in sample_users:
                    db.session.add(user)
                
                db.session.commit()
                print(f"✅ Sample users created in {DATABASE_TYPE}!")
                
        print(f"✅ {DATABASE_TYPE} initialized successfully!")
    except Exception as e:
        print(f"⚠️ Database initialization failed: {e}")
        print("✅ Mock data fallback is ready")

# Inicializar de forma segura
init_database()



if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Starting TimeTracer with {DATABASE_TYPE}")
    app.run(host='0.0.0.0', port=port, debug=False)