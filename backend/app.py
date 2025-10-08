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
    {
        'id': 1, 
        'name': 'Admin TimeTracer', 
        'email': 'admin@timetracer.com', 
        'password': bcrypt.generate_password_hash(os.getenv('ADMIN_PASSWORD', 'defaultpass')).decode('utf-8'), 
        'role': 'admin', 
        'department': 'IT', 
        'status': 'active', 
        'created_at': '2025-01-01T00:00:00'
    },
    {
        'id': 2, 
        'name': 'Juan Manager', 
        'email': 'juan@company.com', 
        'password': bcrypt.generate_password_hash(os.getenv('MANAGER_PASSWORD', 'defaultpass')).decode('utf-8'), 
        'role': 'manager', 
        'department': 'Operations', 
        'status': 'active', 
        'created_at': '2025-01-01T00:00:00'
    },
    {
        'id': 3, 
        'name': 'María Worker', 
        'email': 'maria@company.com', 
        'password': bcrypt.generate_password_hash(os.getenv('WORKER_PASSWORD', 'defaultpass')).decode('utf-8'), 
        'role': 'worker', 
        'department': 'Operations', 
        'status': 'active', 
        'created_at': '2025-01-01T00:00:00'
    },
]

MOCK_TIME_ENTRIES = []

# =================== RUTAS PÚBLICAS DE DOCUMENTACIÓN ===================

@app.route('/favicon.svg')
@app.route('/favicon.ico')
def favicon():
    return redirect('https://api.iconify.design/material-symbols:schedule-outline.svg?color=%23FFEB3B')

@app.route('/')
def home():
    """Root endpoint - Estadísticas en vivo + Documentación completa de la API"""
    
    # Estructura base de la respuesta
    response_data = {
        'app': 'TimeTracer API',
        'version': '1.0.0',
        'status': 'online',
        'database': {},
        'public_endpoints': {},
        'authentication': {},
        'protected_endpoints': {},
        'curl_examples': {}
    }
    
    # =================== ESTADÍSTICAS DE BASE DE DATOS ===================
    if db:
        try:
            # Verificar conexión
            db.session.execute(db.text('SELECT 1'))
            
            # Obtener estadísticas en tiempo real
            admins = User.query.filter_by(role='admin').count()
            managers = User.query.filter_by(role='manager').count()
            workers = User.query.filter_by(role='worker').count()
            total_users = admins + managers + workers
            
            total_entries = TimeEntry.query.count()
            open_entries = TimeEntry.query.filter_by(check_out=None).count()
            closed_entries = total_entries - open_entries
            
            total_hours_result = db.session.execute(
                db.text("SELECT COALESCE(SUM(total_hours), 0) FROM time_entries WHERE total_hours IS NOT NULL")
            ).scalar()
            total_hours = float(total_hours_result) if total_hours_result else 0.0
            
            # Última modificación en la base de datos
            last_changes = []
            
            last_user_change = db.session.execute(
                db.text("SELECT MAX(created_at) FROM users")
            ).scalar()
            if last_user_change:
                last_changes.append(last_user_change)
            
            last_entry_creation = db.session.execute(
                db.text("SELECT MAX(created_at) FROM time_entries")
            ).scalar()
            if last_entry_creation:
                last_changes.append(last_entry_creation)
            
            last_check_in = db.session.execute(
                db.text("SELECT MAX(check_in) FROM time_entries WHERE check_in IS NOT NULL")
            ).scalar()
            if last_check_in:
                last_changes.append(last_check_in)
            
            last_check_out = db.session.execute(
                db.text("SELECT MAX(check_out) FROM time_entries WHERE check_out IS NOT NULL")
            ).scalar()
            if last_check_out:
                last_changes.append(last_check_out)
            
            last_change = max(last_changes) if last_changes else None
            
            # Construir objeto database con estadísticas
            response_data['database'] = {
                'type': DATABASE_TYPE,
                'persistent': IS_PERSISTENT,
                'status': 'connected',
                'users': {
                    'total': total_users,
                    'admin': admins,
                    'manager': managers,
                    'worker': workers
                },
                'time_entries': {
                    'total': total_entries,
                    'open': open_entries,
                    'closed': closed_entries,
                    'total_hours_worked': round(total_hours, 2)
                }
            }
            
            if last_change:
                response_data['database']['last_database_change'] = last_change.isoformat()
            
        except Exception as e:
            print(f"Error getting statistics: {e}")
            response_data['database'] = {
                'type': DATABASE_TYPE,
                'persistent': IS_PERSISTENT,
                'status': 'error',
                'error': str(e)
            }
    else:
        response_data['database'] = {
            'type': DATABASE_TYPE,
            'persistent': IS_PERSISTENT,
            'status': 'disconnected'
        }
    
    # =================== DOCUMENTACIÓN DE ENDPOINTS ===================
    base_url = request.url_root.rstrip('/')
    
    # Endpoints públicos (navegables en el navegador)
    response_data['public_endpoints'] = {
        'note': '✅ Estos endpoints se pueden visitar directamente en el navegador',
        'root': {
            'url': f'{base_url}/',
            'method': 'GET',
            'browsable': '✅ YES',
            'auth_required': 'No',
            'description': 'Esta página - Estadísticas en vivo y documentación',
            'try_now': f'{base_url}/'
        },
        'health': {
            'url': f'{base_url}/api/health',
            'method': 'GET',
            'browsable': '✅ YES',
            'auth_required': 'No',
            'description': 'Health check del servidor para monitoring',
            'try_now': f'{base_url}/api/health'
        },
        'docs': {
            'url': f'{base_url}/api/docs',
            'method': 'GET',
            'browsable': '✅ YES',
            'auth_required': 'No',
            'description': 'Documentación detallada de la API',
            'try_now': f'{base_url}/api/docs'
        }
    }
    
    # Endpoints de autenticación (requieren POST)
    response_data['authentication'] = {
        'note': '⚠️ Estos endpoints requieren método POST (no se pueden visitar en navegador)',
        'login': {
            'url': f'{base_url}/api/auth/login',
            'method': 'POST',
            'browsable': '❌ NO - Requires POST',
            'auth_required': 'No',
            'description': 'Autenticación de usuarios - Devuelve JWT token',
            'body_example': {
                'email': 'admin@timetracer.com',
                'password': 'your_password'
            },
            'response_example': {
                'message': 'Login exitoso',
                'access_token': 'eyJ0eXAiOiJKV1QiLCJhbGc...',
                'user': {
                    'id': 1,
                    'name': 'Admin TimeTracer',
                    'email': 'admin@timetracer.com',
                    'role': 'admin',
                    'department': 'IT'
                }
            }
        }
    }
    
    # Endpoints protegidos (requieren JWT token)
    response_data['protected_endpoints'] = {
        'note': '🔒 Estos endpoints requieren JWT Token en el header Authorization',
        'how_to_use': {
            'step_1': 'Hacer POST a /api/auth/login con credenciales válidas',
            'step_2': 'Copiar el access_token de la respuesta',
            'step_3': 'Añadir header: Authorization: Bearer <token>',
            'step_4': 'Usar Postman, Thunder Client, curl o tu frontend'
        },
        'auth': {
            'me': {
                'url': f'{base_url}/api/auth/me',
                'method': 'GET',
                'browsable': '❌ NO - Requires JWT',
                'auth_required': 'JWT Token',
                'description': 'Obtener información del usuario actual autenticado'
            }
        },
        'users': {
            'list': {
                'url': f'{base_url}/api/users',
                'method': 'GET',
                'browsable': '❌ NO - Requires JWT',
                'auth_required': 'JWT Token',
                'description': 'Listar usuarios según permisos del rol (Admin ve todos, Manager ve su departamento, Worker solo a sí mismo)',
                'permissions': {
                    'admin': 'Ver todos los usuarios',
                    'manager': 'Ver usuarios de su departamento',
                    'worker': 'Ver solo su propio usuario'
                }
            },
            'create': {
                'url': f'{base_url}/api/users',
                'method': 'POST',
                'browsable': '❌ NO - Requires JWT + Admin',
                'auth_required': 'JWT Token (Admin only)',
                'description': 'Crear nuevo usuario (solo administradores)',
                'body_example': {
                    'name': 'Juan Pérez',
                    'email': 'juan@company.com',
                    'password': 'securepass123',
                    'role': 'worker',
                    'department': 'Operations'
                }
            },
            'update': {
                'url': f'{base_url}/api/users/:id',
                'method': 'PUT',
                'browsable': '❌ NO - Requires JWT + Admin',
                'auth_required': 'JWT Token (Admin only)',
                'description': 'Actualizar usuario existente (no puedes editar tu propio usuario)',
                'body_example': {
                    'name': 'Juan Pérez Updated',
                    'email': 'juan.new@company.com',
                    'role': 'manager',
                    'department': 'Sales',
                    'password': 'newpass123 (optional)'
                }
            },
            'delete': {
                'url': f'{base_url}/api/users/:id',
                'method': 'DELETE',
                'browsable': '❌ NO - Requires JWT + Admin',
                'auth_required': 'JWT Token (Admin only)',
                'description': 'Eliminar usuario y todos sus registros (no puedes eliminar tu propio usuario)'
            }
        },
        'time_entries': {
            'list': {
                'url': f'{base_url}/api/time-entries',
                'method': 'GET',
                'browsable': '❌ NO - Requires JWT',
                'auth_required': 'JWT Token',
                'description': 'Listar registros de tiempo según permisos',
                'permissions': {
                    'admin': 'Ver todos los registros',
                    'manager': 'Ver registros de su departamento',
                    'worker': 'Ver solo sus propios registros'
                }
            },
            'create': {
                'url': f'{base_url}/api/time-entries',
                'method': 'POST',
                'browsable': '❌ NO - Requires JWT',
                'auth_required': 'JWT Token',
                'description': 'Crear o actualizar registro de tiempo (check-in/check-out)',
                'body_example': {
                    'user_id': 3,
                    'date': '2025-10-08',
                    'check_in': '2025-10-08T08:00:00.000',
                    'check_out': '2025-10-08T17:00:00.000',
                    'notes': 'Jornada completa'
                }
            },
            'update': {
                'url': f'{base_url}/api/time-entries/:id',
                'method': 'PUT',
                'browsable': '❌ NO - Requires JWT + Manager/Admin',
                'auth_required': 'JWT Token (Manager/Admin only)',
                'description': 'Actualizar registro de tiempo (Managers no pueden editar sus propios registros)',
                'restrictions': {
                    'manager': 'No puede editar sus propios registros, solo los de su equipo',
                    'admin': 'Puede editar todos los registros'
                }
            },
            'delete': {
                'url': f'{base_url}/api/time-entries/:id',
                'method': 'DELETE',
                'browsable': '❌ NO - Requires JWT + Manager/Admin',
                'auth_required': 'JWT Token (Manager/Admin only)',
                'description': 'Eliminar registro de tiempo (Managers no pueden eliminar sus propios registros)'
            }
        }
    }
    
    # =================== EJEMPLOS DE CURL ===================
    response_data['curl_examples'] = {
        'note': '💻 Ejemplos de uso desde la terminal',
        
        '1_login': {
            'description': 'Login y obtener token JWT',
            'command': f'''curl -X POST {base_url}/api/auth/login \\
  -H "Content-Type: application/json" \\
  -d '{{"email":"admin@timetracer.com","password":"your_password"}}\''''
        },
        
        '2_save_token': {
            'description': 'Guardar token en variable de entorno',
            'command': f'''TOKEN=$(curl -s -X POST {base_url}/api/auth/login \\
  -H "Content-Type: application/json" \\
  -d '{{"email":"admin@timetracer.com","password":"your_password"}}' \\
  | jq -r '.access_token')'''
        },
        
        '3_get_users': {
            'description': 'Listar usuarios usando el token',
            'command': f'''curl {base_url}/api/users \\
  -H "Authorization: Bearer $TOKEN"'''
        },
        
        '4_get_current_user': {
            'description': 'Ver información del usuario actual',
            'command': f'''curl {base_url}/api/auth/me \\
  -H "Authorization: Bearer $TOKEN"'''
        },
        
        '5_get_time_entries': {
            'description': 'Listar registros de tiempo',
            'command': f'''curl {base_url}/api/time-entries \\
  -H "Authorization: Bearer $TOKEN"'''
        },
        
        '6_create_user': {
            'description': 'Crear nuevo usuario (solo admin)',
            'command': f'''curl -X POST {base_url}/api/users \\
  -H "Authorization: Bearer $TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{{"name":"Nuevo Usuario","email":"nuevo@company.com","password":"pass123","role":"worker","department":"IT"}}\''''
        },
        
        '7_create_time_entry': {
            'description': 'Crear registro de tiempo (check-in)',
            'command': f'''curl -X POST {base_url}/api/time-entries \\
  -H "Authorization: Bearer $TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{{"user_id":3,"date":"2025-10-08","check_in":"2025-10-08T08:00:00.000","check_out":null}}\''''
        },
        
        '8_complete_workflow': {
            'description': 'Flujo completo: Login → Listar usuarios → Crear registro',
            'bash_script': f'''#!/bin/bash

# 1. Login y guardar token
echo "🔐 Haciendo login..."
TOKEN=$(curl -s -X POST {base_url}/api/auth/login \\
  -H "Content-Type: application/json" \\
  -d '{{"email":"admin@timetracer.com","password":"your_password"}}' \\
  | jq -r '.access_token')

echo "✅ Token obtenido: ${{TOKEN:0:20}}..."

# 2. Ver información del usuario actual
echo "\\n👤 Usuario actual:"
curl -s {base_url}/api/auth/me \\
  -H "Authorization: Bearer $TOKEN" \\
  | jq '.'

# 3. Listar usuarios
echo "\\n👥 Usuarios:"
curl -s {base_url}/api/users \\
  -H "Authorization: Bearer $TOKEN" \\
  | jq '.users[] | {{id, name, role, department}}'

# 4. Listar registros de tiempo
echo "\\n⏰ Registros de tiempo:"
curl -s {base_url}/api/time-entries \\
  -H "Authorization: Bearer $TOKEN" \\
  | jq '.time_entries[] | {{id, user_id, date, check_in, check_out}}'
'''
        }
    }
    
    # =================== INFORMACIÓN ADICIONAL ===================
    response_data['additional_info'] = {
        'frontend_url': 'https://time-tracer-bottega-front.onrender.com',
        'github_repo': 'https://github.com/diegogerwig/devCamp_BOTTEGA_Full_Stack_PROJECT',
        'testing_tools': {
            'recommended': [
                'Postman - https://www.postman.com/',
                'Thunder Client (VS Code Extension)',
                'curl (Terminal)',
                'HTTPie - https://httpie.io/'
            ],
            'browser_extensions': [
                'ModHeader - Para añadir headers Authorization',
                'Requestly - Para modificar requests'
            ]
        },
        'roles_and_permissions': {
            'admin': {
                'description': 'Acceso completo al sistema',
                'can_do': [
                    'Ver todos los usuarios y registros',
                    'Crear, editar y eliminar usuarios',
                    'Editar y eliminar cualquier registro de tiempo',
                    'Acceder a todas las estadísticas'
                ]
            },
            'manager': {
                'description': 'Gestión de su departamento',
                'can_do': [
                    'Ver usuarios de su departamento',
                    'Ver y editar registros de su equipo',
                    'No puede editar/eliminar sus propios registros',
                    'Registrar su propia jornada'
                ]
            },
            'worker': {
                'description': 'Gestión de su propia jornada',
                'can_do': [
                    'Ver solo su propia información',
                    'Registrar check-in y check-out',
                    'Ver su historial de registros',
                    'No puede editar ni eliminar registros'
                ]
            }
        }
    }
    
    # Usar json.dumps para preservar el orden
    import json
    from flask import Response
    
    json_str = json.dumps(response_data, ensure_ascii=False, indent=2)
    return Response(json_str, mimetype='application/json')

@app.route('/api/health')
def health_check():
    """Simple health check para Render.com monitoring"""
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

@app.route('/api/docs')
def api_documentation():
    """Documentación completa de la API (alternativa a Swagger)"""
    base_url = request.url_root.rstrip('/')
    
    return jsonify({
        'api': 'TimeTracer API Documentation',
        'version': '1.0.0',
        'base_url': base_url,
        'authentication': {
            'type': 'JWT Bearer Token',
            'header': 'Authorization: Bearer <token>',
            'obtain_token': f'POST {base_url}/api/auth/login'
        },
        'endpoints': {
            'public': {
                'GET /': 'API root con estadísticas en vivo',
                'GET /api/health': 'Health check',
                'GET /api/docs': 'Esta documentación',
                'POST /api/auth/login': 'Login de usuarios'
            },
            'authenticated': {
                'GET /api/auth/me': 'Usuario actual',
                'GET /api/users': 'Listar usuarios (según rol)',
                'GET /api/time-entries': 'Listar registros (según rol)',
                'POST /api/time-entries': 'Crear registro'
            },
            'admin_only': {
                'POST /api/users': 'Crear usuario',
                'PUT /api/users/:id': 'Actualizar usuario',
                'DELETE /api/users/:id': 'Eliminar usuario'
            },
            'manager_admin': {
                'PUT /api/time-entries/:id': 'Actualizar registro',
                'DELETE /api/time-entries/:id': 'Eliminar registro'
            }
        },
        'roles': {
            'admin': 'Acceso completo al sistema',
            'manager': 'Gestión de su departamento',
            'worker': 'Gestión de sus propios registros'
        }
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