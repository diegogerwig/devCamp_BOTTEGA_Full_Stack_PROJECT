from flask import Flask, jsonify, request, redirect
from flask_cors import CORS
import os
import sys
from datetime import datetime

app = Flask(__name__)
CORS(app, origins=["*"])
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

# Detectar si tenemos PostgreSQL disponible
DATABASE_URL = os.getenv('DATABASE_URL')
HAS_POSTGRES = DATABASE_URL is not None

# Configurar SQLAlchemy
if HAS_POSTGRES:
    try:
        from flask_sqlalchemy import SQLAlchemy
        
        # Convertir postgres:// a postgresql:// si es necesario
        if DATABASE_URL.startswith('postgres://'):
            DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
        
        app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_pre_ping': True,
            'pool_recycle': 300,
            'connect_args': {
                'sslmode': 'require'
            }
        }
        
        db = SQLAlchemy(app)
        DATABASE_TYPE = 'PostgreSQL'
        print("✅ PostgreSQL configured successfully!")
        
    except Exception as e:
        print(f"❌ PostgreSQL setup failed: {e}")
        HAS_POSTGRES = False
        db = None

if not HAS_POSTGRES:
    try:
        from flask_sqlalchemy import SQLAlchemy
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///timetracer.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db = SQLAlchemy(app)
        DATABASE_TYPE = 'SQLite (Temporal)'
        print("⚠️ Using SQLite - Data may be lost on redeploy")
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        db = None
        DATABASE_TYPE = 'Mock Data'

# =================== MODELOS ===================

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

# Datos mock como fallback
MOCK_USERS = [
    {'id': 1, 'name': 'Admin TimeTracer', 'email': 'admin@timetracer.com', 'role': 'admin', 'department': 'IT', 'status': 'active', 'created_at': '2024-01-01T00:00:00'},
    {'id': 2, 'name': 'Juan Manager', 'email': 'juan@company.com', 'role': 'manager', 'department': 'Operations', 'status': 'active', 'created_at': '2024-01-01T00:00:00'},
    {'id': 3, 'name': 'María Worker', 'email': 'maria@company.com', 'role': 'worker', 'department': 'Sales', 'status': 'active', 'created_at': '2024-01-01T00:00:00'},
    {'id': 4, 'name': 'Carlos Developer', 'email': 'carlos@company.com', 'role': 'worker', 'department': 'IT', 'status': 'active', 'created_at': '2024-01-01T00:00:00'}
]

MOCK_TIME_ENTRIES = []

# =================== RUTAS ===================

@app.route('/')
def home():
    return jsonify({
        'message': f'🚀 TimeTracer API v2.0 with {DATABASE_TYPE}',
        'status': 'success',
        'version': '2.0.0',
        'database': DATABASE_TYPE,
        'persistent': HAS_POSTGRES,
        'python_version': f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}',
        'warning': None if HAS_POSTGRES else 'SQLite data may be lost on redeploy - Use PostgreSQL for persistence',
        'endpoints': {
            'health': '/api/health',
            'users': '/api/users',
            'time_entries': '/api/time-entries',
            'status': '/api/status'
        }
    })

@app.route('/api/health')
def health_check():
    db_status = 'unknown'
    
    if db:
        try:
            db.session.execute(db.text('SELECT 1'))
            db_status = 'healthy'
        except Exception as e:
            db_status = f'error: {str(e)}'
    else:
        db_status = 'mock_data'
    
    return jsonify({
        'status': 'healthy',
        'database': db_status,
        'database_type': DATABASE_TYPE,
        'persistent': HAS_POSTGRES,
        'message': 'TimeTracer backend running',
        'environment': os.getenv('FLASK_ENV', 'production'),
        'python_version': f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}',
        'warning': None if HAS_POSTGRES else 'Data may be lost - Configure PostgreSQL for persistence'
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
                    'persistent': HAS_POSTGRES,
                    'message': f'Users from {DATABASE_TYPE}'
                })
            except Exception as e:
                return jsonify({
                    'users': MOCK_USERS,
                    'total': len(MOCK_USERS),
                    'source': 'mock',
                    'persistent': False,
                    'message': f'Database error: {str(e)}'
                })
        else:
            return jsonify({
                'users': MOCK_USERS,
                'total': len(MOCK_USERS),
                'source': 'mock',
                'persistent': False,
                'message': 'Using mock data'
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
                    'persistent': HAS_POSTGRES
                }), 201
            except Exception as e:
                db.session.rollback()
                return jsonify({
                    'error': f'Database error: {str(e)}',
                    'message': 'Could not create user'
                }), 400
        else:
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
                'message': 'User created (mock - will be lost)',
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
                    'persistent': HAS_POSTGRES,
                    'message': f'Time entries from {DATABASE_TYPE}'
                })
            except Exception as e:
                return jsonify({
                    'time_entries': MOCK_TIME_ENTRIES,
                    'total': len(MOCK_TIME_ENTRIES),
                    'source': 'mock',
                    'persistent': False,
                    'message': f'Database error: {str(e)}'
                })
        else:
            return jsonify({
                'time_entries': MOCK_TIME_ENTRIES,
                'total': len(MOCK_TIME_ENTRIES),
                'source': 'mock',
                'persistent': False,
                'message': 'Using mock data'
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
                    'persistent': HAS_POSTGRES
                }), 201
            except Exception as e:
                db.session.rollback()
                return jsonify({
                    'error': f'Database error: {str(e)}',
                    'message': 'Could not create time entry'
                }), 400
        else:
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
                'message': 'Time entry created (mock - will be lost)',
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
            db_status = f'⚠️ Database error: {str(e)}'
    else:
        user_count = len(MOCK_USERS)
        entry_count = len(MOCK_TIME_ENTRIES)
        db_status = '⚠️ Using mock data'
    
    return jsonify({
        'backend': '✅ Backend Online',
        'database': db_status,
        'deploy': '✅ Render Deployment Successful',
        'cors': '✅ CORS Configured',
        'persistence_warning': None if HAS_POSTGRES else '⚠️ SQLite data may be lost - Configure PostgreSQL!',
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
            '🛡️ Robust error handling'
        ],
        'database_type': DATABASE_TYPE,
        'persistent': HAS_POSTGRES,
        'environment': os.getenv('FLASK_ENV', 'production'),
        'python_version': f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}'
    })

# =================== INICIALIZACIÓN ===================

def init_database():
    if not db:
        print("⚠️ No database available, using mock data")
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

# Inicializar
init_database()


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)