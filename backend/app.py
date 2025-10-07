from flask import Flask, jsonify, request, redirect
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, get_jwt
from flask_bcrypt import Bcrypt
import os
import sys
from datetime import datetime, timedelta
from auth import token_required, admin_required, manager_or_admin_required

app = Flask(__name__)

# 🔧 CONFIGURACIÓN CORS MEJORADA
CORS(app, 
     origins=["*"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization"],
     supports_credentials=True,
     max_age=3600)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

jwt = JWTManager(app)
bcrypt = Bcrypt(app)

# Handler para preflight requests (OPTIONS)
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        response.headers.add('Access-Control-Max-Age', '3600')
        return response, 200

# Configuración de base de datos
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

# =================== FUNCIONES AUXILIARES PARA FECHAS ===================
def parse_datetime_string(datetime_str):
    """
    Parsea una fecha/hora que viene del frontend en hora local.
    El frontend envía: '2025-10-07T14:30:00.000'
    Lo parseamos como naive datetime (sin timezone info) para preservar la hora local
    """
    if not datetime_str:
        return None
    
    try:
        # Remover la Z si existe (indica UTC, pero nosotros queremos hora local)
        if datetime_str.endswith('Z'):
            datetime_str = datetime_str[:-1]
        
        # Parsear el datetime sin conversión de zona horaria
        if '.' in datetime_str:
            # Formato: 2025-10-07T14:30:00.000
            return datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S.%f')
        else:
            # Formato: 2025-10-07T14:30:00
            return datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S')
    except Exception as e:
        print(f"⚠️ Error parseando fecha '{datetime_str}': {e}")
        return None

def datetime_to_string(dt):
    """
    Convierte un objeto datetime a string en formato ISO sin conversión de zona horaria.
    Retorna: '2025-10-07T14:30:00.000'
    """
    if not dt:
        return None
    
    if isinstance(dt, str):
        return dt
    
    # Formatear sin la Z (que indicaría UTC)
    return dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]

# =================== MODELOS ===================
if db:
    class User(db.Model):
        __tablename__ = 'users'
        
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), nullable=False)
        email = db.Column(db.String(120), unique=True, nullable=False)
        users_password = db.Column('users_password', db.String(255), nullable=False)
        role = db.Column(db.String(20), nullable=False, default='worker')
        department = db.Column(db.String(50), nullable=False)
        status = db.Column(db.String(20), nullable=False, default='active')
        created_at = db.Column(db.DateTime, default=datetime.now)  # ✅ CAMBIADO: datetime.now en lugar de utcnow
        
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
        created_at = db.Column(db.DateTime, default=datetime.now)  # ✅ CAMBIADO: datetime.now en lugar de utcnow
        
        def to_dict(self):
            return {
                'id': self.id,
                'user_id': self.user_id,
                'date': self.date.isoformat(),
                'check_in': datetime_to_string(self.check_in),
                'check_out': datetime_to_string(self.check_out),
                'total_hours': self.total_hours,
                'notes': self.notes,
                'created_at': self.created_at.isoformat()
            }

# =================== DATOS MOCK ===================
MOCK_USERS = [
    {'id': 1, 'name': 'Admin TimeTracer', 'email': 'admin@timetracer.com', 'password': bcrypt.generate_password_hash('admin123').decode('utf-8'), 'role': 'admin', 'department': 'IT', 'status': 'active', 'created_at': '2024-01-01T00:00:00'},
    {'id': 2, 'name': 'Juan Manager', 'email': 'juan@company.com', 'password': bcrypt.generate_password_hash('manager123').decode('utf-8'), 'role': 'manager', 'department': 'Operations', 'status': 'active', 'created_at': '2024-01-01T00:00:00'},
    {'id': 3, 'name': 'María Worker', 'email': 'maria@company.com', 'password': bcrypt.generate_password_hash('worker123').decode('utf-8'), 'role': 'worker', 'department': 'Operations', 'status': 'active', 'created_at': '2024-01-01T00:00:00'},
]

MOCK_TIME_ENTRIES = []

# =================== RUTAS PÚBLICAS ===================
@app.route('/favicon.svg')
@app.route('/favicon.ico')
def favicon():
    return redirect('https://api.iconify.design/material-symbols:schedule-outline.svg?color=%23FFEB3B')

@app.route('/')
def home():
    # Initialize db_info structure
    db_info = {}
    
    if db:
        try:
            # Verify connection
            db.session.execute(db.text('SELECT 1'))
            
            # Get real-time statistics
            try:
                # Users by role (ordered by hierarchy)
                admins = User.query.filter_by(role='admin').count()
                managers = User.query.filter_by(role='manager').count()
                workers = User.query.filter_by(role='worker').count()
                total_users = admins + managers + workers
                
                # Time entries stats
                total_entries = TimeEntry.query.count()
                open_entries = TimeEntry.query.filter_by(check_out=None).count()
                closed_entries = total_entries - open_entries
                
                # Total hours worked
                total_hours_result = db.session.execute(
                    db.text("SELECT COALESCE(SUM(total_hours), 0) FROM time_entries WHERE total_hours IS NOT NULL")
                ).scalar()
                total_hours = float(total_hours_result) if total_hours_result else 0.0
                
                # Last database change - check multiple timestamps
                last_changes = []
                
                # Most recent user creation
                last_user_change = db.session.execute(
                    db.text("SELECT MAX(created_at) FROM users")
                ).scalar()
                if last_user_change:
                    last_changes.append(last_user_change)
                
                # Most recent time entry creation
                last_entry_creation = db.session.execute(
                    db.text("SELECT MAX(created_at) FROM time_entries")
                ).scalar()
                if last_entry_creation:
                    last_changes.append(last_entry_creation)
                
                # Most recent check-in
                last_check_in = db.session.execute(
                    db.text("SELECT MAX(check_in) FROM time_entries WHERE check_in IS NOT NULL")
                ).scalar()
                if last_check_in:
                    last_changes.append(last_check_in)
                
                # Most recent check-out
                last_check_out = db.session.execute(
                    db.text("SELECT MAX(check_out) FROM time_entries WHERE check_out IS NOT NULL")
                ).scalar()
                if last_check_out:
                    last_changes.append(last_check_out)
                
                # Get the most recent of all timestamps
                last_change = max(last_changes) if last_changes else None
                
                # Build db_info in exact order
                db_info['type'] = DATABASE_TYPE
                db_info['persistent'] = IS_PERSISTENT
                db_info['status'] = 'connected'
                db_info['users'] = {
                    'total': total_users,
                    'admin': admins,
                    'manager': managers,
                    'worker': workers
                }
                db_info['time_entries'] = {
                    'total': total_entries,
                    'open': open_entries,
                    'closed': closed_entries,
                    'total_hours_worked': round(total_hours, 2)
                }
                if last_change:
                    db_info['last_database_change'] = last_change.isoformat()
                
            except Exception as e:
                print(f"Error getting statistics: {e}")
                db_info['type'] = DATABASE_TYPE
                db_info['persistent'] = IS_PERSISTENT
                db_info['status'] = 'error'
                db_info['error'] = str(e)
            
        except Exception as e:
            print(f"Error connecting to database: {e}")
            db_info['type'] = DATABASE_TYPE
            db_info['persistent'] = IS_PERSISTENT
            db_info['status'] = 'disconnected'
            db_info['error'] = str(e)
    else:
        db_info['type'] = DATABASE_TYPE
        db_info['persistent'] = IS_PERSISTENT
        db_info['status'] = 'disconnected'
    
    # Get the base URL from the request
    base_url = request.url_root.rstrip('/')
    
    # Build response manually to control order
    import json
    from flask import Response
    
    response_dict = {
        'app': 'TimeTracer API',
        'status': 'online',
        'database': db_info,
        'endpoints': {
            'status': f'{base_url}/api/status',
            'health': f'{base_url}/api/health',
            'login': f'POST {base_url}/api/auth/login',
            'users': f'{base_url}/api/users',
            'time_entries': f'{base_url}/api/time-entries'
        }
    }
    
    # Use json.dumps with ensure_ascii=False to preserve order
    json_str = json.dumps(response_dict, ensure_ascii=False, indent=2)
    
    return Response(json_str, mimetype='application/json')

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
        'persistent': IS_PERSISTENT
    })

@app.route('/api/status', methods=['GET', 'OPTIONS'])
def get_status():
    """Ruta pública de status - NO requiere autenticación"""
    user_count = entry_count = 0
    
    if db:
        try:
            db.session.execute(db.text('SELECT 1'))
            user_count = User.query.count()
            entry_count = TimeEntry.query.count()
            db_status = f'✅ {DATABASE_TYPE} Connected'
        except Exception as e:
            user_count = len(MOCK_USERS)
            entry_count = len(MOCK_TIME_ENTRIES)
            db_status = f'⚠️ Using mock data'
    else:
        user_count = len(MOCK_USERS)
        entry_count = len(MOCK_TIME_ENTRIES)
        db_status = '⚠️ Using mock data'
    
    return jsonify({
        'backend': '✅ Online',
        'database': db_status,
        'statistics': {
            'users': user_count,
            'time_entries': entry_count,
            'absences': 0
        },
        'database_type': DATABASE_TYPE,
        'persistent': IS_PERSISTENT,
        'features': [
            'Gestión de usuarios con roles (Admin, Manager, Worker)',
            'Registro de jornadas laborales con entrada/salida',
            'Control de permisos por roles',
            'Dashboard personalizado por rol',
            'Gestión de equipos por departamento',
            'Edición y eliminación de registros (permisos)',
            'Edición de usuarios por Admin',
            'Sistema de autenticación JWT',
            'Base de datos persistente (PostgreSQL)',
            'Manejo de horas en zona horaria local',
            'Múltiples registros por día',
            'Validación de registros abiertos'
        ]
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
            
            if user and bcrypt.check_password_hash(user.users_password, password):
                access_token = create_access_token(
                    identity=str(user.id),
                    additional_claims={
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
            print(f"Database error in login: {e}")
    
    # Mock fallback
    user = next((u for u in MOCK_USERS if u['email'] == email), None)
    
    if user and bcrypt.check_password_hash(user['password'], password):
        user_copy = user.copy()
        user_copy.pop('password')
        
        access_token = create_access_token(
            identity=str(user['id']),
            additional_claims={
                'email': user['email'],
                'role': user['role'],
                'name': user['name'],
                'department': user['department']
            }
        )
        
        return jsonify({
            'message': 'Login exitoso (mock)',
            'access_token': access_token,
            'user': user_copy
        }), 200
    
    return jsonify({'message': 'Credenciales inválidas'}), 401

@app.route('/api/auth/me', methods=['GET'])
@token_required
def get_current_user():
    user_id = get_jwt_identity()
    claims = get_jwt()
    
    if db:
        try:
            user = User.query.get(int(user_id))
            if user:
                return jsonify({'user': user.to_dict()}), 200
        except Exception as e:
            print(f"Database error: {e}")
    
    # Mock fallback
    user_data = {
        'id': int(user_id),
        'email': claims.get('email'),
        'role': claims.get('role'),
        'name': claims.get('name'),
        'department': claims.get('department'),
        'status': 'active'
    }
    
    return jsonify({'user': user_data}), 200

# =================== GESTIÓN DE USUARIOS ===================
@app.route('/api/users', methods=['GET'])
@token_required
def get_users():
    claims = get_jwt()
    user_role = claims.get('role')
    user_dept = claims.get('department')
    user_id = int(get_jwt_identity())
    
    if db:
        try:
            if user_role == 'admin':
                users = User.query.all()
            elif user_role == 'manager':
                users = User.query.filter_by(department=user_dept).all()
            else:
                users = User.query.filter_by(id=user_id).all()
            
            return jsonify({
                'users': [user.to_dict() for user in users],
                'total': len(users),
                'source': DATABASE_TYPE
            })
        except Exception as e:
            print(f"Database error: {e}")
    
    # Mock fallback
    if user_role == 'admin':
        filtered_users = MOCK_USERS
    elif user_role == 'manager':
        filtered_users = [u for u in MOCK_USERS if u['department'] == user_dept]
    else:
        filtered_users = [u for u in MOCK_USERS if u['id'] == user_id]
    
    users_without_password = [{k: v for k, v in u.items() if k != 'password'} for u in filtered_users]
    
    return jsonify({
        'users': users_without_password,
        'total': len(users_without_password),
        'source': 'mock'
    })

@app.route('/api/users', methods=['POST'])
@admin_required
def create_user():
    try:
        claims = get_jwt()
        user_role = claims.get('role')
        data = request.get_json()
        
        required_fields = ['name', 'email', 'password', 'department']
        if not all(field in data for field in required_fields):
            return jsonify({'message': 'Todos los campos son requeridos'}), 400
        
        new_user_role = data.get('role', 'worker')
        
        if user_role != 'admin':
            return jsonify({'message': 'Solo los administradores pueden crear usuarios'}), 403
        
        if new_user_role not in ['worker', 'manager', 'admin']:
            return jsonify({'message': 'Rol no válido'}), 400
        
        if db:
            try:
                existing = User.query.filter_by(email=data['email']).first()
                if existing:
                    return jsonify({'message': 'El email ya está registrado'}), 400
                
                hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
                
                new_user = User(
                    name=data['name'],
                    email=data['email'],
                    users_password=hashed_password,
                    role=new_user_role,
                    department=data['department'],
                    status='active'
                )
                
                db.session.add(new_user)
                db.session.commit()
                
                return jsonify({
                    'message': 'Usuario creado exitosamente',
                    'user': new_user.to_dict()
                }), 201
                
            except Exception as e:
                db.session.rollback()
                return jsonify({'message': f'Error en base de datos: {str(e)}'}), 500
        
        # Mock fallback
        if any(u['email'] == data['email'] for u in MOCK_USERS):
            return jsonify({'message': 'El email ya está registrado'}), 400
        
        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        new_user = {
            'id': len(MOCK_USERS) + 1,
            'name': data['name'],
            'email': data['email'],
            'password': hashed_password,
            'role': new_user_role,
            'department': data['department'],
            'status': 'active',
            'created_at': datetime.now().isoformat()
        }
        MOCK_USERS.append(new_user)
        
        user_copy = new_user.copy()
        user_copy.pop('password')
        
        return jsonify({
            'message': 'Usuario creado (mock)',
            'user': user_copy
        }), 201
        
    except Exception as e:
        return jsonify({'message': f'Error del servidor: {str(e)}'}), 500

@app.route('/api/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    try:
        data = request.get_json()
        current_user_id = int(get_jwt_identity())
        
        if user_id == current_user_id:
            return jsonify({'message': 'No puedes editar tu propio usuario'}), 403
        
        if db:
            try:
                user = User.query.get(user_id)
                if not user:
                    return jsonify({'message': 'Usuario no encontrado'}), 404
                
                if 'name' in data:
                    user.name = data['name']
                if 'email' in data:
                    existing = User.query.filter(User.email == data['email'], User.id != user_id).first()
                    if existing:
                        return jsonify({'message': 'El email ya está en uso'}), 400
                    user.email = data['email']
                if 'role' in data:
                    user.role = data['role']
                if 'department' in data:
                    user.department = data['department']
                if 'status' in data:
                    user.status = data['status']
                
                if 'password' in data and data['password']:
                    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
                    user.users_password = hashed_password
                
                db.session.commit()
                
                return jsonify({
                    'message': 'Usuario actualizado exitosamente',
                    'user': user.to_dict()
                }), 200
                
            except Exception as e:
                db.session.rollback()
                return jsonify({'message': f'Error en base de datos: {str(e)}'}), 500
        
        # Mock fallback
        user = next((u for u in MOCK_USERS if u['id'] == user_id), None)
        if not user:
            return jsonify({'message': 'Usuario no encontrado'}), 404
        
        if 'name' in data:
            user['name'] = data['name']
        if 'email' in data:
            if any(u['email'] == data['email'] and u['id'] != user_id for u in MOCK_USERS):
                return jsonify({'message': 'El email ya está en uso'}), 400
            user['email'] = data['email']
        if 'role' in data:
            user['role'] = data['role']
        if 'department' in data:
            user['department'] = data['department']
        if 'status' in data:
            user['status'] = data['status']
        if 'password' in data and data['password']:
            hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
            user['password'] = hashed_password
        
        user_copy = user.copy()
        user_copy.pop('password', None)
        
        return jsonify({
            'message': 'Usuario actualizado (mock)',
            'user': user_copy
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error del servidor: {str(e)}'}), 500

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    current_user_id = int(get_jwt_identity())
    
    if user_id == current_user_id:
        return jsonify({'message': 'No puedes eliminar tu propio usuario'}), 403
    
    if db:
        try:
            user = User.query.get(user_id)
            if not user:
                return jsonify({'message': 'Usuario no encontrado'}), 404
            
            TimeEntry.query.filter_by(user_id=user_id).delete()
            db.session.delete(user)
            db.session.commit()
            
            return jsonify({'message': 'Usuario eliminado exitosamente'}), 200
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': f'Error: {str(e)}'}), 500
    
    # Mock fallback
    user = next((u for u in MOCK_USERS if u['id'] == user_id), None)
    if not user:
        return jsonify({'message': 'Usuario no encontrado'}), 404
    
    global MOCK_TIME_ENTRIES
    MOCK_TIME_ENTRIES = [e for e in MOCK_TIME_ENTRIES if e['user_id'] != user_id]
    MOCK_USERS.remove(user)
    
    return jsonify({'message': 'Usuario eliminado (mock)'}), 200

# =================== REGISTROS DE TIEMPO ===================
@app.route('/api/time-entries', methods=['GET'])
@token_required
def get_time_entries():
    claims = get_jwt()
    user_role = claims.get('role')
    user_dept = claims.get('department')
    user_id = int(get_jwt_identity())
    
    if db:
        try:
            if user_role == 'admin':
                entries = TimeEntry.query.order_by(TimeEntry.check_in.desc()).all()
            elif user_role == 'manager':
                dept_users = User.query.filter_by(department=user_dept).all()
                user_ids = [u.id for u in dept_users]
                entries = TimeEntry.query.filter(TimeEntry.user_id.in_(user_ids)).order_by(TimeEntry.check_in.desc()).all()
            else:
                entries = TimeEntry.query.filter_by(user_id=user_id).order_by(TimeEntry.check_in.desc()).all()
            
            return jsonify({
                'time_entries': [entry.to_dict() for entry in entries],
                'total': len(entries),
                'source': DATABASE_TYPE
            })
        except Exception as e:
            print(f"Database error: {e}")
    
    # Mock fallback
    if user_role == 'admin':
        filtered_entries = MOCK_TIME_ENTRIES
    elif user_role == 'manager':
        dept_users = [u['id'] for u in MOCK_USERS if u['department'] == user_dept]
        filtered_entries = [e for e in MOCK_TIME_ENTRIES if e['user_id'] in dept_users]
    else:
        filtered_entries = [e for e in MOCK_TIME_ENTRIES if e['user_id'] == user_id]
    
    return jsonify({
        'time_entries': filtered_entries,
        'total': len(filtered_entries),
        'source': 'mock'
    })

@app.route('/api/time-entries', methods=['POST'])
@token_required
def create_time_entry():
    claims = get_jwt()
    user_role = claims.get('role')
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    if 'date' not in data or 'check_in' not in data:
        return jsonify({'message': 'Fecha y hora de entrada son requeridos'}), 400
    
    target_user_id = data.get('user_id', user_id)
    
    # Validar permisos
    if user_role == 'worker' and target_user_id != user_id:
        return jsonify({'message': 'No puedes crear registros para otros usuarios'}), 403
    
    if db:
        try:
            entry_date_str = data['date']
            if isinstance(entry_date_str, str):
                entry_date = datetime.strptime(entry_date_str, '%Y-%m-%d').date()
            else:
                entry_date = entry_date_str
            
            check_in = parse_datetime_string(data['check_in'])
            check_out = parse_datetime_string(data.get('check_out')) if data.get('check_out') else None
            
            if not check_in:
                return jsonify({'message': 'Formato de fecha/hora de entrada inválido'}), 400
            
            # 🔒 VALIDACIÓN: Verificar si el usuario tiene un registro abierto
            if not check_out:
                open_entry = TimeEntry.query.filter_by(
                    user_id=target_user_id,
                    check_out=None
                ).first()
                
                if open_entry:
                    return jsonify({
                        'message': f'Ya existe un registro abierto desde el {open_entry.date}. Debes cerrarlo antes de abrir uno nuevo.',
                        'open_entry': open_entry.to_dict()
                    }), 400
            
            # ✅ MODIFICADO: Buscar registro por ID exacto para actualización
            # O buscar registro abierto en la misma fecha para actualización
            existing = None
            if 'entry_id' in data:
                # Si viene un entry_id, actualizar ese registro específico
                existing = TimeEntry.query.get(data['entry_id'])
            else:
                # Si no hay entry_id, buscar registro abierto en la misma fecha
                existing = TimeEntry.query.filter_by(
                    user_id=target_user_id,
                    date=entry_date,
                    check_out=None
                ).first()
            
            if existing:
                # Actualizar registro existente
                existing.check_in = check_in
                existing.check_out = check_out
                existing.total_hours = data.get('total_hours')
                existing.notes = data.get('notes')
                db.session.commit()
                
                return jsonify({
                    'message': 'Registro actualizado',
                    'time_entry': existing.to_dict()
                }), 200
            else:
                # ✅ MODIFICADO: Siempre crear nuevo registro (no buscar por fecha)
                new_entry = TimeEntry(
                    user_id=target_user_id,
                    date=entry_date,
                    check_in=check_in,
                    check_out=check_out,
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
            print(f"❌ Error in time entry: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'message': f'Error: {str(e)}'}), 500
   
    # Mock fallback con validación de registro abierto
    if not data.get('check_out'):
        open_entry = next((e for e in MOCK_TIME_ENTRIES if e['user_id'] == target_user_id and e['check_out'] is None), None)
        if open_entry:
            return jsonify({
                'message': f'Ya existe un registro abierto desde el {open_entry["date"]}. Debes cerrarlo antes de abrir uno nuevo.',
                'open_entry': open_entry
            }), 400
    
    existing_index = None
    for i, entry in enumerate(MOCK_TIME_ENTRIES):
        if entry['user_id'] == target_user_id and entry['date'] == data['date']:
            existing_index = i
            break
    
    if existing_index is not None:
        MOCK_TIME_ENTRIES[existing_index].update({
            'check_in': data.get('check_in'),
            'check_out': data.get('check_out'),
            'total_hours': data.get('total_hours'),
            'notes': data.get('notes')
        })
        return jsonify({
            'message': 'Registro actualizado (mock)',
            'time_entry': MOCK_TIME_ENTRIES[existing_index]
        }), 200
    else:
        new_entry = {
            'id': len(MOCK_TIME_ENTRIES) + 1,
            'user_id': target_user_id,
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

@app.route('/api/time-entries/<int:entry_id>', methods=['PUT'])
@manager_or_admin_required
def update_time_entry(entry_id):
    claims = get_jwt()
    user_role = claims.get('role')
    user_dept = claims.get('department')
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    if db:
        try:
            entry = TimeEntry.query.get(entry_id)
            if not entry:
                return jsonify({'message': 'Registro no encontrado'}), 404
            
            entry_owner = User.query.get(entry.user_id)
            
            # Validar permisos
            if user_role == 'manager':
                if entry.user_id == user_id:
                    return jsonify({'message': 'No puedes editar tus propios registros'}), 403
                if entry_owner.department != user_dept:
                    return jsonify({'message': 'No tienes permiso'}), 403
            
            # Actualizar con parsing correcto de fechas
            if 'check_in' in data:
                entry.check_in = parse_datetime_string(data['check_in'])
            if 'check_out' in data:
                entry.check_out = parse_datetime_string(data['check_out']) if data['check_out'] else None
            if 'total_hours' in data:
                entry.total_hours = data['total_hours']
            if 'notes' in data:
                entry.notes = data['notes']
            
            db.session.commit()
            
            return jsonify({
                'message': 'Registro actualizado',
                'time_entry': entry.to_dict()
            }), 200
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': f'Error: {str(e)}'}), 500
    
    # Mock fallback
    entry = next((e for e in MOCK_TIME_ENTRIES if e['id'] == entry_id), None)
    if not entry:
        return jsonify({'message': 'Registro no encontrado'}), 404
    
    entry_owner = next((u for u in MOCK_USERS if u['id'] == entry['user_id']), None)
    
    if user_role == 'manager':
        if entry['user_id'] == user_id:
            return jsonify({'message': 'No puedes editar tus propios registros'}), 403
        if entry_owner['department'] != user_dept:
            return jsonify({'message': 'No tienes permiso'}), 403
    
    if 'check_in' in data:
        entry['check_in'] = data['check_in']
    if 'check_out' in data:
        entry['check_out'] = data['check_out']
    if 'total_hours' in data:
        entry['total_hours'] = data['total_hours']
    if 'notes' in data:
        entry['notes'] = data['notes']
    
    return jsonify({
        'message': 'Registro actualizado (mock)',
        'time_entry': entry
    }), 200

@app.route('/api/time-entries/<int:entry_id>', methods=['DELETE'])
@manager_or_admin_required
def delete_time_entry(entry_id):
    claims = get_jwt()
    user_role = claims.get('role')
    user_dept = claims.get('department')
    user_id = int(get_jwt_identity())
    
    if db:
        try:
            entry = TimeEntry.query.get(entry_id)
            if not entry:
                return jsonify({'message': 'Registro no encontrado'}), 404
            
            entry_owner = User.query.get(entry.user_id)
            
            if user_role == 'manager':
                if entry.user_id == user_id:
                    return jsonify({'message': 'No puedes eliminar tus propios registros'}), 403
                if entry_owner.department != user_dept:
                    return jsonify({'message': 'No tienes permiso'}), 403
            
            db.session.delete(entry)
            db.session.commit()
            
            return jsonify({'message': 'Registro eliminado'}), 200
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': f'Error: {str(e)}'}), 500
    
    # Mock fallback
    entry = next((e for e in MOCK_TIME_ENTRIES if e['id'] == entry_id), None)
    if not entry:
        return jsonify({'message': 'Registro no encontrado'}), 404
    
    entry_owner = next((u for u in MOCK_USERS if u['id'] == entry['user_id']), None)
    
    if user_role == 'manager':
        if entry['user_id'] == user_id:
            return jsonify({'message': 'No puedes eliminar tus propios registros'}), 403
        if entry_owner['department'] != user_dept:
            return jsonify({'message': 'No tienes permiso'}), 403
    
    MOCK_TIME_ENTRIES.remove(entry)
    return jsonify({'message': 'Registro eliminado (mock)'}), 200

# =================== INICIALIZACIÓN ===================
def init_database():
    if not db:
        print("⚠️ No database, using mock data")
        return
    
    try:
        with app.app_context():
            print("🔄 Verificando estructura de base de datos...")
            try:
                result = db.session.execute(db.text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'users' 
                    AND column_name = 'users_password'
                """))
                has_users_password = result.fetchone() is not None
                
                if not has_users_password:
                    print("⚠️  Columna 'users_password' no existe, verificando alternativas...")
                    
                    result = db.session.execute(db.text("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = 'users' 
                        AND column_name = 'password'
                    """))
                    has_password = result.fetchone() is not None
                    
                    if has_password:
                        print("✅ Renombrando 'password' a 'users_password'...")
                        db.session.execute(db.text("ALTER TABLE users RENAME COLUMN password TO users_password"))
                        db.session.commit()
                        print("✅ Migración completada!")
                    else:
                        print("⚠️  Creando columna 'users_password'...")
                        db.session.execute(db.text("ALTER TABLE users ADD COLUMN users_password VARCHAR(255)"))
                        db.session.commit()
                        print("✅ Columna creada!")
                else:
                    print("✅ La columna 'users_password' existe correctamente")
                    
            except Exception as e:
                print(f"⚠️ Error en migración automática: {e}")
                
            print(f"✅ Using existing {DATABASE_TYPE} tables")
                
    except Exception as e:
        print(f"⚠️ Database init info: {e}")

init_database()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Starting TimeTracer with {DATABASE_TYPE}")
    app.run(host='0.0.0.0', port=port, debug=False)