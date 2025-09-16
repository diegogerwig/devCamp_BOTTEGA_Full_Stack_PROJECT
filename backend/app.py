from flask import Flask, jsonify, request, redirect
from flask_cors import CORS
import os
import sys
from datetime import datetime

app = Flask(__name__)

# CORS simple - permitir todo para empezar
CORS(app, origins=["*"])

# Configuración básica
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

# Intentar importar SQLAlchemy solo si está disponible
try:
    from flask_sqlalchemy import SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///timetracer.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db = SQLAlchemy(app)
    HAS_DATABASE = True
except Exception as e:
    print(f"Warning: Database not available: {e}")
    db = None
    HAS_DATABASE = False

# =================== MODELOS (solo si hay DB) ===================

if HAS_DATABASE:
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

# =================== DATOS MOCK (fallback) ===================

MOCK_USERS = [
    {
        'id': 1,
        'name': 'Admin TimeTracer',
        'email': 'admin@timetracer.com',
        'role': 'admin',
        'department': 'IT',
        'status': 'active',
        'created_at': '2024-01-01T00:00:00'
    },
    {
        'id': 2,
        'name': 'Juan Manager',
        'email': 'juan@company.com',
        'role': 'manager',
        'department': 'Operations',
        'status': 'active',
        'created_at': '2024-01-01T00:00:00'
    },
    {
        'id': 3,
        'name': 'María Worker',
        'email': 'maria@company.com',
        'role': 'worker',
        'department': 'Sales',
        'status': 'active',
        'created_at': '2024-01-01T00:00:00'
    },
    {
        'id': 4,
        'name': 'Carlos Developer',
        'email': 'carlos@company.com',
        'role': 'worker',
        'department': 'IT',
        'status': 'active',
        'created_at': '2024-01-01T00:00:00'
    }
]

MOCK_TIME_ENTRIES = [
    {
        'id': 1,
        'user_id': 1,
        'date': '2024-01-15',
        'check_in': '2024-01-15T09:00:00',
        'check_out': '2024-01-15T17:00:00',
        'total_hours': 8.0,
        'notes': 'Regular work day',
        'created_at': '2024-01-15T09:00:00'
    },
    {
        'id': 2,
        'user_id': 2,
        'date': '2024-01-15',
        'check_in': '2024-01-15T08:30:00',
        'check_out': '2024-01-15T16:30:00',
        'total_hours': 8.0,
        'notes': 'Management tasks',
        'created_at': '2024-01-15T08:30:00'
    }
]

# =================== RUTAS ===================

@app.route('/favicon.svg')
@app.route('/favicon.ico')
def favicon():
    return redirect('https://api.iconify.design/material-symbols:schedule-outline.svg?color=%23FFEB3B')

@app.route('/')
def home():
    return jsonify({
        'message': '🚀 TimeTracer API v2.0 - Simple & Robust',
        'status': 'success',
        'version': '2.0.0',
        'database': 'SQLite (Working)' if HAS_DATABASE else 'Mock Data (Fallback)',
        'python_version': f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}',
        'has_database': HAS_DATABASE,
        'endpoints': {
            'health': '/api/health',
            'users': '/api/users',
            'time_entries': '/api/time-entries',
            'status': '/api/status'
        }
    })

@app.route('/api/health')
def health_check():
    db_status = 'healthy'
    db_type = 'Unknown'
    
    if HAS_DATABASE:
        try:
            db.session.execute(db.text('SELECT 1'))
            db_status = 'healthy'
            db_type = 'SQLite'
        except Exception as e:
            db_status = f'error: {str(e)}'
            db_type = 'SQLite (error)'
    else:
        db_status = 'mock_data'
        db_type = 'Mock Data'
    
    return jsonify({
        'status': 'healthy',
        'database': db_status,
        'database_type': db_type,
        'message': 'TimeTracer backend - Simple & Robust',
        'environment': os.getenv('FLASK_ENV', 'production'),
        'python_version': f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}',
        'has_database': HAS_DATABASE,
        'server': 'Render'
    })

@app.route('/api/users', methods=['GET', 'POST'])
def handle_users():
    if request.method == 'GET':
        if HAS_DATABASE:
            try:
                users = User.query.all()
                return jsonify({
                    'users': [user.to_dict() for user in users],
                    'total': len(users),
                    'source': 'database',
                    'message': 'Users retrieved from SQLite database'
                })
            except Exception as e:
                # Fallback to mock data
                return jsonify({
                    'users': MOCK_USERS,
                    'total': len(MOCK_USERS),
                    'source': 'mock',
                    'message': f'Database error, using mock data: {str(e)}'
                })
        else:
            return jsonify({
                'users': MOCK_USERS,
                'total': len(MOCK_USERS),
                'source': 'mock',
                'message': 'Using mock data (database not available)'
            })
    
    elif request.method == 'POST':
        data = request.get_json()
        
        if HAS_DATABASE:
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
                    'message': 'User created successfully in database',
                    'user': new_user.to_dict(),
                    'source': 'database'
                }), 201
            except Exception as e:
                db.session.rollback()
                return jsonify({
                    'error': f'Database error: {str(e)}',
                    'message': 'Could not create user in database'
                }), 400
        else:
            # Mock creation
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
                'message': 'User created successfully (mock)',
                'user': new_user,
                'source': 'mock'
            }), 201

@app.route('/api/time-entries', methods=['GET', 'POST'])
def handle_time_entries():
    if request.method == 'GET':
        if HAS_DATABASE:
            try:
                entries = TimeEntry.query.order_by(TimeEntry.date.desc()).all()
                return jsonify({
                    'time_entries': [entry.to_dict() for entry in entries],
                    'total': len(entries),
                    'source': 'database',
                    'message': 'Time entries retrieved from SQLite database'
                })
            except Exception as e:
                return jsonify({
                    'time_entries': MOCK_TIME_ENTRIES,
                    'total': len(MOCK_TIME_ENTRIES),
                    'source': 'mock',
                    'message': f'Database error, using mock data: {str(e)}'
                })
        else:
            return jsonify({
                'time_entries': MOCK_TIME_ENTRIES,
                'total': len(MOCK_TIME_ENTRIES),
                'source': 'mock',
                'message': 'Using mock data (database not available)'
            })
    
    elif request.method == 'POST':
        data = request.get_json()
        
        if HAS_DATABASE:
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
                    'message': 'Time entry created successfully in database',
                    'time_entry': new_entry.to_dict(),
                    'source': 'database'
                }), 201
            except Exception as e:
                db.session.rollback()
                return jsonify({
                    'error': f'Database error: {str(e)}',
                    'message': 'Could not create time entry in database'
                }), 400
        else:
            # Mock creation
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
                'message': 'Time entry created successfully (mock)',
                'time_entry': new_entry,
                'source': 'mock'
            }), 201

@app.route('/api/status')
def get_status():
    user_count = 0
    entry_count = 0
    db_status = 'Unknown'
    
    if HAS_DATABASE:
        try:
            db.session.execute(db.text('SELECT 1'))
            user_count = User.query.count()
            entry_count = TimeEntry.query.count()
            db_status = '✅ SQLite Connected & Ready'
        except Exception as e:
            user_count = len(MOCK_USERS)
            entry_count = len(MOCK_TIME_ENTRIES)
            db_status = f'⚠️ Database error, using mock data: {str(e)}'
    else:
        user_count = len(MOCK_USERS)
        entry_count = len(MOCK_TIME_ENTRIES)
        db_status = '✅ Mock Data Ready (Database not available)'
    
    return jsonify({
        'backend': '✅ Backend Online (Simple & Robust)',
        'database': db_status,
        'deploy': '✅ Render Deployment Successful',
        'cors': '✅ CORS Configured',
        'statistics': {
            'users': user_count,
            'time_entries': entry_count,
            'absences': 0
        },
        'features': [
            '🗄️ SQLite Database Integration' if HAS_DATABASE else '📝 Mock Data Fallback',
            '📊 Real User & Time Entry Management',
            '🔐 CORS configured for frontend',
            '👥 User Management (CRUD)',
            '⏰ Time Entry Tracking',
            f'🐍 Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} Compatible',
            '📡 Deployed on Render infrastructure',
            '🛡️ Robust error handling with fallbacks'
        ],
        'database_type': 'SQLite' if HAS_DATABASE else 'Mock Data',
        'environment': os.getenv('FLASK_ENV', 'production'),
        'python_version': f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}',
        'has_database': HAS_DATABASE
    })

# =================== INICIALIZACIÓN ===================

def init_database():
    """Inicializar base de datos solo si está disponible"""
    if not HAS_DATABASE:
        print("⚠️ Database not available, using mock data")
        return
    
    try:
        with app.app_context():
            db.create_all()
            
            # Crear datos de ejemplo solo si no hay usuarios
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
                print("✅ Sample users created in database!")
                
        print("✅ Database initialized successfully!")
    except Exception as e:
        print(f"⚠️ Database initialization failed: {e}")
        print("Will use mock data as fallback")

# Inicializar la base de datos al cargar el módulo
init_database()

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'message': 'Something went wrong, but the server is still running',
        'fallback': 'Mock data available'
    }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)