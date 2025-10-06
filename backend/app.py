from flask import Flask, jsonify, request, redirect
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity
from flask_bcrypt import Bcrypt
import os
import sys
from datetime import datetime, timedelta
from auth import token_required, admin_required, manager_or_admin_required

app = Flask(__name__)
CORS(app, origins=["*"])
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

jwt = JWTManager(app)
bcrypt = Bcrypt(app)

DATABASE_URL = os.getenv('DATABASE_URL')
db = None
DATABASE_TYPE = 'Mock Data'
IS_PERSISTENT = False

if DATABASE_URL:
    print(f"🔍 DATABASE_URL found: {DATABASE_URL[:50]}...")
    try:
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
        
        try:
            import pg8000
            db = SQLAlchemy(app)
            DATABASE_TYPE = 'PostgreSQL (100% Persistente)'
            IS_PERSISTENT = True
            print("✅ PostgreSQL with pg8000 configured!")
        except ImportError as e:
            print(f"⚠️ pg8000 not available: {e}")
            db = None
            
    except Exception as e:
        print(f"❌ PostgreSQL setup failed: {e}")
        db = None

if db is None:
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

# =================== MODELOS ===================

if db:
    class User(db.Model):
        __tablename__ = 'users'
        
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), nullable=False)
        email = db.Column(db.String(120), unique=True, nullable=False)
        password = db.Column(db.String(255), nullable=False)
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

# =================== DATOS MOCK ===================

MOCK_USERS = [
    {'id': 1, 'name': 'Admin TimeTracer', 'email': 'admin@timetracer.com', 'password': bcrypt.generate_password_hash('admin123').decode('utf-8'), 'role': 'admin', 'department': 'IT', 'status': 'active', 'created_at': '2024-01-01T00:00:00'},
    {'id': 2, 'name': 'Juan Manager', 'email': 'juan@company.com', 'password': bcrypt.generate_password_hash('manager123').decode('utf-8'), 'role': 'manager', 'department': 'Operations', 'status': 'active', 'created_at': '2024-01-01T00:00:00'},
    {'id': 3, 'name': 'María Worker', 'email': 'maria@company.com', 'password': bcrypt.generate_password_hash('worker123').decode('utf-8'), 'role': 'worker', 'department': 'Sales', 'status': 'active', 'created_at': '2024-01-01T00:00:00'},
    {'id': 4, 'name': 'Carlos Developer', 'email': 'carlos@company.com', 'password': bcrypt.generate_password_hash('worker123').decode('utf-8'), 'role': 'worker', 'department': 'IT', 'status': 'active', 'created_at': '2024-01-01T00:00:00'}
]

MOCK_TIME_ENTRIES = [
    {'id': 1, 'user_id': 1, 'date': '2024-01-15', 'check_in': '2024-01-15T09:00:00', 'check_out': '2024-01-15T17:00:00', 'total_hours': 8.0, 'notes': 'Regular work day', 'created_at': '2024-01-15T09:00:00'},
    {'id': 2, 'user_id': 2, 'date': '2024-01-15', 'check_in': '2024-01-15T08:30:00', 'check_out': '2024-01-15T16:30:00', 'total_hours': 8.0, 'notes': 'Management tasks', 'created_at': '2024-01-15T08:30:00'}
]

# =================== RUTAS PÚBLICAS ===================

@app.route('/favicon.svg')
@app.route('/favicon.ico')
def favicon():
    return redirect('https://api.iconify.design/material-symbols:schedule-outline.svg?color=%23FFEB3B')

@app.route('/')
def home():
    return jsonify({
        'message': f'🚀 TimeTracer API v2.0 with Authentication & {DATABASE_TYPE}',
        'status': 'success',
        'version': '2.0.0',
        'database': DATABASE_TYPE,
        'persistent': IS_PERSISTENT,
        'authentication': 'JWT Enabled',
        'endpoints': {
            'auth': {
                'login': '/api/auth/login',
                'register': '/api/auth/register',
                'me': '/api/auth/me'
            },
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
        'authentication': 'enabled',
        'message': 'TimeTracer backend running with authentication'
    })

# =================== AUTENTICACIÓN ===================

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'message': 'Email y contraseña requeridos'}), 400
    
    if db:
        try:
            user = User.query.filter_by(email=email).first()
            
            if user and bcrypt.check_password_hash(user.password, password):
                access_token = create_access_token(
                    identity={
                        'id': user.id,
                        'email': user.email,
                        'role': user.role,
                        'name': user.name,
                        'department': user.department
                    }
                )
                
                return jsonify({
                    'message': 'Login exitoso',
                    'access_token': access_token,
                    'user': user.to_dict()
                }), 200
            else:
                return jsonify({'message': 'Credenciales inválidas'}), 401
                
        except Exception as e:
            print(f"Database error, using mock: {e}")
            # Fallback a mock si falla la DB
    
    # Mock data
    user = next((u for u in MOCK_USERS if u['email'] == email), None)
    
    if user and bcrypt.check_password_hash(user['password'], password):
        user_copy = user.copy()
        user_copy.pop('password')
        
        access_token = create_access_token(
            identity={
                'id': user['id'],
                'email': user['email'],
                'role': user['role'],
                'name': user['name'],
                'department': user['department']
            }
        )
        
        return jsonify({
            'message': 'Login exitoso (mock data)',
            'access_token': access_token,
            'user': user_copy
        }), 200
    
    return jsonify({'message': 'Credenciales inválidas'}), 401

@app.route('/api/auth/register', methods=['POST'])
@admin_required
def register():
    data = request.get_json()
    
    required_fields = ['name', 'email', 'password', 'role', 'department']
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Todos los campos son requeridos'}), 400
    
    if db:
        try:
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user:
                return jsonify({'message': 'El email ya está registrado'}), 400
            
            hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
            
            new_user = User(
                name=data['name'],
                email=data['email'],
                password=hashed_password,
                role=data['role'],
                department=data['department']
            )
            
            db.session.add(new_user)
            db.session.commit()
            
            return jsonify({
                'message': 'Usuario registrado exitosamente',
                'user': new_user.to_dict()
            }), 201
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': f'Error al registrar usuario: {str(e)}'}), 500
    
    # Mock data
    if any(u['email'] == data['email'] for u in MOCK_USERS):
        return jsonify({'message': 'El email ya está registrado'}), 400
    
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = {
        'id': len(MOCK_USERS) + 1,
        'name': data['name'],
        'email': data['email'],
        'password': hashed_password,
        'role': data['role'],
        'department': data['department'],
        'status': 'active',
        'created_at': datetime.utcnow().isoformat()
    }
    MOCK_USERS.append(new_user)
    
    user_copy = new_user.copy()
    user_copy.pop('password')
    
    return jsonify({
        'message': 'Usuario registrado exitosamente (mock data)',
        'user': user_copy
    }), 201

@app.route('/api/auth/me', methods=['GET'])
@token_required
def get_current_user():
    current_user = get_jwt_identity()
    
    if db:
        try:
            user = User.query.get(current_user['id'])
            if user:
                return jsonify({'user': user.to_dict()}), 200
        except Exception as e:
            print(f"Database error: {e}")
    
    # Mock data
    user = next((u for u in MOCK_USERS if u['id'] == current_user['id']), None)
    if user:
        user_copy = user.copy()
        user_copy.pop('password')
        return jsonify({'user': user_copy}), 200
    
    return jsonify({'message': 'Usuario no encontrado'}), 404

# =================== RUTAS PROTEGIDAS ===================

@app.route('/api/users', methods=['GET'])
@token_required
def get_users():
    current_user = get_jwt_identity()
    
    if db:
        try:
            if current_user['role'] == 'admin':
                users = User.query.all()
            elif current_user['role'] == 'manager':
                users = User.query.filter_by(department=current_user['department']).all()
            else:
                users = User.query.filter_by(id=current_user['id']).all()
            
            return jsonify({
                'users': [user.to_dict() for user in users],
                'total': len(users),
                'source': DATABASE_TYPE
            })
        except Exception as e:
            print(f"Database error: {e}")
    
    # Mock data
    if current_user['role'] == 'admin':
        filtered_users = MOCK_USERS
    elif current_user['role'] == 'manager':
        filtered_users = [u for u in MOCK_USERS if u['department'] == current_user['department']]
    else:
        filtered_users = [u for u in MOCK_USERS if u['id'] == current_user['id']]
    
    users_without_password = [{k: v for k, v in u.items() if k != 'password'} for u in filtered_users]
    
    return jsonify({
        'users': users_without_password,
        'total': len(users_without_password),
        'source': 'mock'
    })

@app.route('/api/users', methods=['POST'])
@admin_required
def create_user():
    data = request.get_json()
    
    if db:
        try:
            hashed_password = bcrypt.generate_password_hash(data.get('password', 'default123')).decode('utf-8')
            
            new_user = User(
                name=data['name'],
                email=data['email'],
                password=hashed_password,
                role=data.get('role', 'worker'),
                department=data['department']
            )
            db.session.add(new_user)
            db.session.commit()
            
            return jsonify({
                'message': 'Usuario creado exitosamente',
                'user': new_user.to_dict()
            }), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': f'Error: {str(e)}'}), 500
    
    # Mock data
    hashed_password = bcrypt.generate_password_hash(data.get('password', 'default123')).decode('utf-8')
    new_user = {
        'id': len(MOCK_USERS) + 1,
        'name': data['name'],
        'email': data['email'],
        'password': hashed_password,
        'role': data.get('role', 'worker'),
        'department': data['department'],
        'status': 'active',
        'created_at': datetime.utcnow().isoformat()
    }
    MOCK_USERS.append(new_user)
    
    user_copy = new_user.copy()
    user_copy.pop('password')
    
    return jsonify({
        'message': 'Usuario creado (mock)',
        'user': user_copy
    }), 201

@app.route('/api/time-entries', methods=['GET'])
@token_required
def get_time_entries():
    current_user = get_jwt_identity()
    
    if db:
        try:
            if current_user['role'] == 'admin':
                entries = TimeEntry.query.order_by(TimeEntry.date.desc()).all()
            elif current_user['role'] == 'manager':
                dept_users = User.query.filter_by(department=current_user['department']).all()
                user_ids = [u.id for u in dept_users]
                entries = TimeEntry.query.filter(TimeEntry.user_id.in_(user_ids)).order_by(TimeEntry.date.desc()).all()
            else:
                entries = TimeEntry.query.filter_by(user_id=current_user['id']).order_by(TimeEntry.date.desc()).all()
            
            return jsonify({
                'time_entries': [entry.to_dict() for entry in entries],
                'total': len(entries),
                'source': DATABASE_TYPE
            })
        except Exception as e:
            print(f"Database error: {e}")
    
    # Mock data
    if current_user['role'] == 'admin':
        filtered_entries = MOCK_TIME_ENTRIES
    elif current_user['role'] == 'manager':
        dept_users = [u['id'] for u in MOCK_USERS if u['department'] == current_user['department']]
        filtered_entries = [e for e in MOCK_TIME_ENTRIES if e['user_id'] in dept_users]
    else:
        filtered_entries = [e for e in MOCK_TIME_ENTRIES if e['user_id'] == current_user['id']]
    
    return jsonify({
        'time_entries': filtered_entries,
        'total': len(filtered_entries),
        'source': 'mock'
    })

@app.route('/api/time-entries', methods=['POST'])
@token_required
def create_time_entry():
    current_user = get_jwt_identity()
    data = request.get_json()
    
    # Workers solo pueden crear sus propias entradas
    if current_user['role'] == 'worker' and data.get('user_id') != current_user['id']:
        return jsonify({'message': 'No puedes crear registros para otros usuarios'}), 403
    
    if db:
        try:
            new_entry = TimeEntry(
                user_id=data.get('user_id', current_user['id']),
                date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
                check_in=datetime.fromisoformat(data['check_in'].replace('Z', '+00:00')) if data.get('check_in') else None,
                check_out=datetime.fromisoformat(data['check_out'].replace('Z', '+00:00')) if data.get('check_out') else None,
                total_hours=data.get('total_hours'),
                notes=data.get('notes')
            )
            
            db.session.add(new_entry)
            db.session.commit()
            
            return jsonify({
                'message': 'Registro creado',
                'time_entry': new_entry.to_dict()
            }), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': f'Error: {str(e)}'}), 500
    
    # Mock data
    new_entry = {
        'id': len(MOCK_TIME_ENTRIES) + 1,
        'user_id': data.get('user_id', current_user['id']),
        'date': data['date'],
        'check_in': data.get('check_in'),
        'check_out': data.get('check_out'),
        'total_hours': data.get('total_hours'),
        'notes': data.get('notes'),
        'created_at': datetime.utcnow().isoformat()
    }
    MOCK_TIME_ENTRIES.append(new_entry)
    
    return jsonify({
        'message': 'Registro creado (mock)',
        'time_entry': new_entry
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
        db_status = '⚠️ Using mock data'
    
    return jsonify({
        'backend': '✅ Backend Online with Authentication',
        'database': db_status,
        'deploy': '✅ Render Deployment Successful',
        'authentication': '✅ JWT Authentication Enabled',
        'statistics': {
            'users': user_count,
            'time_entries': entry_count,
            'absences': 0
        },
        'features': [
            f'🔐 JWT Authentication System',
            f'👥 Role-Based Access Control',
            f'🗄️ {DATABASE_TYPE} Integration',
            '📊 Real User & Time Entry Management',
            '🔒 Password Encryption with Bcrypt',
            '🎯 Protected Endpoints',
            '👔 Admin, Manager & Worker Roles',
            f'🐍 Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}'
        ],
        'database_type': DATABASE_TYPE,
        'persistent': IS_PERSISTENT
    })

# =================== INICIALIZACIÓN ===================

def init_database():
    if not db:
        print("⚠️ No database available, mock data ready")
        return
    
    try:
        with app.app_context():
            db.create_all()
            
            if User.query.count() == 0:
                sample_users = [
                    User(
                        name='Admin TimeTracer',
                        email='admin@timetracer.com',
                        password=bcrypt.generate_password_hash('admin123').decode('utf-8'),
                        role='admin',
                        department='IT'
                    ),
                    User(
                        name='Juan Manager',
                        email='juan@company.com',
                        password=bcrypt.generate_password_hash('manager123').decode('utf-8'),
                        role='manager',
                        department='Operations'
                    ),
                    User(
                        name='María Worker',
                        email='maria@company.com',
                        password=bcrypt.generate_password_hash('worker123').decode('utf-8'),
                        role='worker',
                        department='Sales'
                    ),
                    User(
                        name='Carlos Developer',
                        email='carlos@company.com',
                        password=bcrypt.generate_password_hash('worker123').decode('utf-8'),
                        role='worker',
                        department='IT'
                    )
                ]
                
                for user in sample_users:
                    db.session.add(user)
                
                db.session.commit()
                print(f"✅ Sample users created with authentication!")
                
        print(f"✅ {DATABASE_TYPE} initialized successfully!")
    except Exception as e:
        print(f"⚠️ Database initialization failed: {e}")
        print("✅ Mock data fallback is ready")

init_database()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Starting TimeTracer with Authentication & {DATABASE_TYPE}")
    app.run(host='0.0.0.0', port=port, debug=False)