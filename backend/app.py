from flask import Flask, jsonify, request, redirect
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
from flask_bcrypt import Bcrypt
import os
import sys
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)
CORS(app, origins=["*"])
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-dev-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

jwt = JWTManager(app)
bcrypt = Bcrypt(app)

# Configuración de base de datos (mantén tu lógica existente)
DATABASE_URL = os.getenv('DATABASE_URL')
db = None
DATABASE_TYPE = 'Mock Data'
IS_PERSISTENT = False

if DATABASE_URL:
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
        except ImportError:
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
        DATABASE_TYPE = 'Mock Data'
        IS_PERSISTENT = False

# =================== MODELOS ACTUALIZADOS ===================

if db:
    class User(db.Model):
        __tablename__ = 'users'
        
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(50), unique=True, nullable=False)
        password_hash = db.Column(db.String(255), nullable=False)
        name = db.Column(db.String(100), nullable=False)
        email = db.Column(db.String(120), unique=True, nullable=False)
        role = db.Column(db.String(20), nullable=False, default='user')  # admin, manager, user
        department = db.Column(db.String(50), nullable=False)
        status = db.Column(db.String(20), nullable=False, default='active')
        manager_name = db.Column(db.String(100), nullable=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        
        def set_password(self, password):
            self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
            
        def check_password(self, password):
            return bcrypt.check_password_hash(self.password_hash, password)
        
        def to_dict(self):
            return {
                'id': self.id,
                'username': self.username,
                'name': self.name,
                'email': self.email,
                'role': self.role,
                'department': self.department,
                'status': self.status,
                'manager_name': self.manager_name,
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

# =================== DECORADORES DE AUTORIZACIÓN ===================

def role_required(*roles):
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):
            claims = get_jwt()
            user_role = claims.get('role')
            
            if user_role not in roles:
                return jsonify({'error': 'Acceso denegado'}), 403
            
            return fn(*args, **kwargs)
        return decorator
    return wrapper

# =================== RUTAS DE AUTENTICACIÓN ===================

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Usuario y contraseña requeridos'}), 400
    
    if db:
        try:
            user = User.query.filter_by(username=username).first()
            
            if user and user.check_password(password):
                additional_claims = {
                    'role': user.role,
                    'name': user.name,
                    'email': user.email
                }
                
                access_token = create_access_token(
                    identity=user.id,
                    additional_claims=additional_claims
                )
                
                return jsonify({
                    'token': access_token,
                    'user': user.to_dict()
                }), 200
            else:
                return jsonify({'error': 'Credenciales inválidas'}), 401
                
        except Exception as e:
            return jsonify({'error': f'Error de base de datos: {str(e)}'}), 500
    else:
        return jsonify({'error': 'Base de datos no disponible'}), 503

@app.route('/api/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    
    if db:
        try:
            user = User.query.get(user_id)
            if user:
                return jsonify(user.to_dict()), 200
            else:
                return jsonify({'error': 'Usuario no encontrado'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Base de datos no disponible'}), 503

# =================== RUTAS PROTEGIDAS ===================

@app.route('/api/users', methods=['GET'])
@role_required('admin')
def get_all_users():
    """Solo admin puede ver todos los usuarios"""
    if db:
        try:
            users = User.query.all()
            return jsonify({
                'users': [user.to_dict() for user in users],
                'total': len(users)
            }), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Base de datos no disponible'}), 503

@app.route('/api/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Usuario puede ver su propia info, admin puede ver cualquiera"""
    current_user_id = get_jwt_identity()
    claims = get_jwt()
    user_role = claims.get('role')
    
    # Admin puede ver cualquier usuario, otros solo a sí mismos
    if user_role != 'admin' and current_user_id != user_id:
        return jsonify({'error': 'Acceso denegado'}), 403
    
    if db:
        try:
            user = User.query.get(user_id)
            if user:
                return jsonify(user.to_dict()), 200
            else:
                return jsonify({'error': 'Usuario no encontrado'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Base de datos no disponible'}), 503

@app.route('/api/time-entries', methods=['GET'])
@jwt_required()
def get_time_entries():
    """Usuarios ven sus registros, managers ven su equipo, admin ve todos"""
    current_user_id = get_jwt_identity()
    claims = get_jwt()
    user_role = claims.get('role')
    
    if db:
        try:
            if user_role == 'admin':
                # Admin ve todos los registros
                entries = TimeEntry.query.order_by(TimeEntry.date.desc()).all()
            elif user_role == 'manager':
                # Manager ve registros de su equipo
                current_user = User.query.get(current_user_id)
                team_users = User.query.filter_by(manager_name=current_user.name).all()
                team_ids = [u.id for u in team_users] + [current_user_id]
                entries = TimeEntry.query.filter(TimeEntry.user_id.in_(team_ids)).order_by(TimeEntry.date.desc()).all()
            else:
                # User solo ve sus propios registros
                entries = TimeEntry.query.filter_by(user_id=current_user_id).order_by(TimeEntry.date.desc()).all()
            
            return jsonify({
                'time_entries': [entry.to_dict() for entry in entries],
                'total': len(entries)
            }), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Base de datos no disponible'}), 503

@app.route('/api/time-entries', methods=['POST'])
@jwt_required()
def create_time_entry():
    """Crear registro de tiempo"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    # Usuario solo puede crear registros para sí mismo (a menos que sea admin)
    claims = get_jwt()
    user_role = claims.get('role')
    
    target_user_id = data.get('user_id', current_user_id)
    
    if user_role != 'admin' and target_user_id != current_user_id:
        return jsonify({'error': 'Solo puedes crear registros para ti mismo'}), 403
    
    if db:
        try:
            new_entry = TimeEntry(
                user_id=target_user_id,
                date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
                check_in=datetime.fromisoformat(data['check_in'].replace('Z', '+00:00')) if data.get('check_in') else None,
                check_out=datetime.fromisoformat(data['check_out'].replace('Z', '+00:00')) if data.get('check_out') else None,
                total_hours=data.get('total_hours'),
                notes=data.get('notes')
            )
            
            db.session.add(new_entry)
            db.session.commit()
            
            return jsonify({
                'message': 'Registro creado exitosamente',
                'time_entry': new_entry.to_dict()
            }), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Base de datos no disponible'}), 503

# =================== RUTAS EXISTENTES (mantén las que necesites) ===================

@app.route('/')
def home():
    return jsonify({
        'message': f'🚀 TimeTracer API v2.0 with Authentication',
        'status': 'success',
        'version': '2.0.0',
        'database': DATABASE_TYPE,
        'persistent': IS_PERSISTENT,
        'endpoints': {
            'auth_login': '/api/auth/login',
            'auth_me': '/api/auth/me',
            'users': '/api/users',
            'time_entries': '/api/time-entries',
            'health': '/api/health'
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
        'authentication': 'enabled'
    })

# =================== INICIALIZACIÓN ===================

def init_database():
    if not db:
        print("⚠️ No database available")
        return
    
    try:
        with app.app_context():
            db.create_all()
            
            # Crear usuarios de ejemplo si no existen
            if User.query.count() == 0:
                admin = User(
                    username='admin',
                    name='Admin TimeTracer',
                    email='admin@timetracer.com',
                    role='admin',
                    department='IT',
                    status='active'
                )
                admin.set_password('admin123')
                
                manager = User(
                    username='manager1',
                    name='Carlos Manager',
                    email='manager@company.com',
                    role='manager',
                    department='Operations',
                    status='active'
                )
                manager.set_password('manager123')
                
                user1 = User(
                    username='user1',
                    name='Ana Worker',
                    email='ana@company.com',
                    role='user',
                    department='Sales',
                    status='active',
                    manager_name='Carlos Manager'
                )
                user1.set_password('user123')
                
                user2 = User(
                    username='user2',
                    name='Luis Developer',
                    email='luis@company.com',
                    role='user',
                    department='IT',
                    status='active',
                    manager_name='Carlos Manager'
                )
                user2.set_password('user123')
                
                db.session.add_all([admin, manager, user1, user2])
                db.session.commit()
                
                print("✅ Sample users created!")
                print("   Admin: admin / admin123")
                print("   Manager: manager1 / manager123")
                print("   User: user1 / user123")
                
        print(f"✅ {DATABASE_TYPE} initialized successfully!")
    except Exception as e:
        print(f"⚠️ Database initialization failed: {e}")

init_database()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Starting TimeTracer with Authentication")
    app.run(host='0.0.0.0', port=port, debug=False)