from flask import Flask, jsonify, request, redirect
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, get_jwt
from flask_bcrypt import Bcrypt
import os
import sys
from datetime import datetime, timedelta
from auth import token_required, admin_required, manager_or_admin_required
from data.mock_data import get_mock_users
from src.init_db import init_database
from src.date_utils import parse_datetime_string, datetime_to_string
from src.models import init_models

app = Flask(__name__)

# 🔧 CORS CONFIGURATION
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

MOCK_USERS = get_mock_users()  

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL')
db = None
User = None
TimeEntry = None
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
            User, TimeEntry = init_models(db)
            DATABASE_TYPE = 'PostgreSQL'
            IS_PERSISTENT = True
            app.DATABASE_TYPE = DATABASE_TYPE  # Store for init_db module
            print("✅ PostgreSQL with pg8000 configured!")
        except ImportError as e:
            print(f"⚠️ pg8000 not available: {e}")
            db = None
            
    except Exception as e:
        print(f"❌ PostgreSQL setup failed: {e}")
        db = None

# # =================== MODELS ===================
# if db:
#     class User(db.Model):
#         __tablename__ = 'users'
        
#         id = db.Column(db.Integer, primary_key=True)
#         name = db.Column(db.String(100), nullable=False)
#         email = db.Column(db.String(120), unique=True, nullable=False)
#         users_password = db.Column('users_password', db.String(255), nullable=False)
#         role = db.Column(db.String(20), nullable=False, default='worker')
#         department = db.Column(db.String(50), nullable=False)
#         status = db.Column(db.String(20), nullable=False, default='active')
#         created_at = db.Column(db.DateTime, default=datetime.now)
        
#         def to_dict(self):
#             return {
#                 'id': self.id,
#                 'name': self.name,
#                 'email': self.email,
#                 'role': self.role,
#                 'department': self.department,
#                 'status': self.status,
#                 'created_at': self.created_at.isoformat()
#             }

#     class TimeEntry(db.Model):
#         __tablename__ = 'time_entries'
        
#         id = db.Column(db.Integer, primary_key=True)
#         user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
#         date = db.Column(db.Date, nullable=False)
#         check_in = db.Column(db.DateTime, nullable=True)
#         check_out = db.Column(db.DateTime, nullable=True)
#         total_hours = db.Column(db.Float, nullable=True)
#         notes = db.Column(db.Text, nullable=True)
#         created_at = db.Column(db.DateTime, default=datetime.now)
        
#         def to_dict(self):
#             return {
#                 'id': self.id,
#                 'user_id': self.user_id,
#                 'date': self.date.isoformat(),
#                 'check_in': datetime_to_string(self.check_in),
#                 'check_out': datetime_to_string(self.check_out),
#                 'total_hours': self.total_hours,
#                 'notes': self.notes,
#                 'created_at': self.created_at.isoformat()
#             }

# =================== PUBLIC DOCUMENTATION ROUTES ===================

@app.route('/favicon.svg')
@app.route('/favicon.ico')
def favicon():
    return redirect('https://api.iconify.design/material-symbols:schedule-outline.svg?color=%23FFEB3B')

@app.route('/')
def home():
    """Root endpoint - Live statistics + API summary"""
    
    # Base response structure
    response_data = {
        'app': 'TimeTracer API',
        'version': '1.0.0',
        'status': 'online',
        'database': {},
        'endpoints': {
            'public': [],
            'authentication': [],
            'protected_jwt': []
        }
    }
    
    # =================== DATABASE STATISTICS ===================
    if db:
        try:
            # Verify connection
            db.session.execute(db.text('SELECT 1'))
            
            # Get real-time statistics
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
            
            # Last database modification
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
            
            # Build database object with statistics
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
    
    # =================== ENDPOINTS SUMMARY ===================
    base_url = request.url_root.rstrip('/')
    
    # Public endpoints (browsable in browser)
    response_data['endpoints']['public'] = [
        f"GET {base_url}/",
        f"GET {base_url}/api/health",
        f"GET {base_url}/api/docs"
    ]
    
    # Authentication endpoints (require POST)
    response_data['endpoints']['authentication'] = [
        f"POST {base_url}/api/auth/login"
    ]
    
    # Protected endpoints (require JWT)
    response_data['endpoints']['protected_jwt'] = [
        f"GET {base_url}/api/auth/me",
        f"GET {base_url}/api/users",
        f"POST {base_url}/api/users (admin only)",
        f"PUT {base_url}/api/users/:id (admin only)",
        f"DELETE {base_url}/api/users/:id (admin only)",
        f"GET {base_url}/api/time-entries",
        f"POST {base_url}/api/time-entries",
        f"PUT {base_url}/api/time-entries/:id (manager/admin)",
        f"DELETE {base_url}/api/time-entries/:id (manager/admin)"
    ]
    
    # Additional information
    response_data['documentation'] = f"{base_url}/api/docs"
    response_data['links'] = {
        'frontend': 'https://time-tracer-bottega-front.onrender.com',
        'github': 'https://github.com/diegogerwig/devCamp_BOTTEGA_Full_Stack_PROJECT'
    }
    
    # Use json.dumps to preserve order
    import json
    from flask import Response
    
    json_str = json.dumps(response_data, ensure_ascii=False, indent=2)
    return Response(json_str, mimetype='application/json')

@app.route('/api/health')
def health_check():
    """Simple health check for Render.com monitoring"""
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
    """Complete API documentation"""
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
                'GET /': 'API root with live statistics',
                'GET /api/health': 'Health check',
                'GET /api/docs': 'This documentation',
                'POST /api/auth/login': 'User login'
            },
            'authenticated': {
                'GET /api/auth/me': 'Current user',
                'GET /api/users': 'List users (by role)',
                'GET /api/time-entries': 'List entries (by role)',
                'POST /api/time-entries': 'Create entry'
            },
            'admin_only': {
                'POST /api/users': 'Create user',
                'PUT /api/users/:id': 'Update user',
                'DELETE /api/users/:id': 'Delete user'
            },
            'manager_admin': {
                'PUT /api/time-entries/:id': 'Update entry',
                'DELETE /api/time-entries/:id': 'Delete entry'
            }
        },
        'roles': {
            'admin': 'Full system access',
            'manager': 'Department management',
            'worker': 'Own entries management'
        }
    })

# =================== AUTHENTICATION ===================
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'message': 'Email and password required'}), 400
    
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
                    'message': 'Login successful',
                    'access_token': access_token,
                    'user': user.to_dict()
                }), 200
            else:
                return jsonify({'message': 'Invalid credentials'}), 401
                
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
            'message': 'Login successful (mock)',
            'access_token': access_token,
            'user': user_copy
        }), 200

    return jsonify({'message': 'Invalid credentials'}), 401

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

# =================== USER MANAGEMENT ===================
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
            return jsonify({'message': 'All fields are required'}), 400
        
        new_user_role = data.get('role', 'worker')
        
        if user_role != 'admin':
            return jsonify({'message': 'Only administrators can create users'}), 403
        
        if new_user_role not in ['worker', 'manager', 'admin']:
            return jsonify({'message': 'Invalid role'}), 400
        
        if db:
            try:
                existing = User.query.filter_by(email=data['email']).first()
                if existing:
                    return jsonify({'message': 'Email already registered'}), 400
                
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
                    'message': 'User created successfully',
                    'user': new_user.to_dict()
                }), 201
                
            except Exception as e:
                db.session.rollback()
                return jsonify({'message': f'Database error: {str(e)}'}), 500
        
        # Mock fallback
        if any(u['email'] == data['email'] for u in MOCK_USERS):
            return jsonify({'message': 'Email already registered'}), 400
        
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
            'message': 'User created (mock)',
            'user': user_copy
        }), 201
        
    except Exception as e:
        return jsonify({'message': f'Server error: {str(e)}'}), 500

@app.route('/api/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    try:
        data = request.get_json()
        current_user_id = int(get_jwt_identity())
        
        if user_id == current_user_id:
            return jsonify({'message': 'You cannot edit your own user'}), 403
        
        if db:
            try:
                user = User.query.get(user_id)
                if not user:
                    return jsonify({'message': 'User not found'}), 404
                
                if 'name' in data:
                    user.name = data['name']
                if 'email' in data:
                    existing = User.query.filter(User.email == data['email'], User.id != user_id).first()
                    if existing:
                        return jsonify({'message': 'Email already in use'}), 400
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
                    'message': 'User updated successfully',
                    'user': user.to_dict()
                }), 200
                
            except Exception as e:
                db.session.rollback()
                return jsonify({'message': f'Database error: {str(e)}'}), 500
        
        # Mock fallback
        user = next((u for u in MOCK_USERS if u['id'] == user_id), None)
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        if 'name' in data:
            user['name'] = data['name']
        if 'email' in data:
            if any(u['email'] == data['email'] and u['id'] != user_id for u in MOCK_USERS):
                return jsonify({'message': 'Email already in use'}), 400
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
            'message': 'User updated (mock)',
            'user': user_copy
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Server error: {str(e)}'}), 500

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    current_user_id = int(get_jwt_identity())
    
    if user_id == current_user_id:
        return jsonify({'message': 'You cannot delete your own user'}), 403
    
    if db:
        try:
            user = User.query.get(user_id)
            if not user:
                return jsonify({'message': 'User not found'}), 404
            
            TimeEntry.query.filter_by(user_id=user_id).delete()
            db.session.delete(user)
            db.session.commit()
            
            return jsonify({'message': 'User deleted successfully'}), 200
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': f'Error: {str(e)}'}), 500
    
    # Mock fallback
    user = next((u for u in MOCK_USERS if u['id'] == user_id), None)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    # global MOCK_TIME_ENTRIES
    # MOCK_TIME_ENTRIES = [e for e in MOCK_TIME_ENTRIES if e['user_id'] != user_id]
    MOCK_USERS.remove(user)
    
    return jsonify({'message': 'User deleted (mock)'}), 200

# =================== TIME ENTRIES ===================
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

@app.route('/api/time-entries', methods=['POST'])
@token_required
def create_time_entry():
    claims = get_jwt()
    user_role = claims.get('role')
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    if 'date' not in data or 'check_in' not in data:
        return jsonify({'message': 'Date and check-in time are required'}), 400
    
    target_user_id = data.get('user_id', user_id)
    
    # Validate permissions
    if user_role == 'worker' and target_user_id != user_id:
        return jsonify({'message': 'You cannot create entries for other users'}), 403
    
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
                return jsonify({'message': 'Invalid check-in date/time format'}), 400
            
            # 🔒 VALIDATION: Check if user has an open entry
            if not check_out:
                open_entry = TimeEntry.query.filter_by(
                    user_id=target_user_id,
                    check_out=None
                ).first()
                
                if open_entry:
                    return jsonify({
                        'message': f'An open entry already exists from {open_entry.date}. You must close it before opening a new one.',
                        'open_entry': open_entry.to_dict()
                    }), 400

            existing = None
            if 'entry_id' in data:
                # If entry_id provided, update that specific entry
                existing = TimeEntry.query.get(data['entry_id'])
            else:
                # If no entry_id, search for open entry on the same date
                existing = TimeEntry.query.filter_by(
                    user_id=target_user_id,
                    date=entry_date,
                    check_out=None
                ).first()
            
            if existing:
                # Update existing entry
                existing.check_in = check_in
                existing.check_out = check_out
                existing.total_hours = data.get('total_hours')
                existing.notes = data.get('notes')
                db.session.commit()
                
                return jsonify({
                    'message': 'Entry updated',
                    'time_entry': existing.to_dict()
                }), 200
            else:
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
                    'message': 'Entry created',
                    'time_entry': new_entry.to_dict()
                }), 201
                
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error in time entry: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'message': f'Error: {str(e)}'}), 500
   
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
                return jsonify({'message': 'Entry not found'}), 404
            
            entry_owner = User.query.get(entry.user_id)
            
            # Validate permissions
            if user_role == 'manager':
                if entry.user_id == user_id:
                    return jsonify({'message': 'You cannot edit your own entries'}), 403
                if entry_owner.department != user_dept:
                    return jsonify({'message': 'You do not have permission'}), 403
            
            # Update with correct date parsing
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
                'message': 'Entry updated',
                'time_entry': entry.to_dict()
            }), 200
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': f'Error: {str(e)}'}), 500
    
    entry_owner = next((u for u in MOCK_USERS if u['id'] == entry['user_id']), None)
    
    if user_role == 'manager':
        if entry['user_id'] == user_id:
            return jsonify({'message': 'You cannot edit your own entries'}), 403
        if entry_owner['department'] != user_dept:
            return jsonify({'message': 'You do not have permission'}), 403
    
    if 'check_in' in data:
        entry['check_in'] = data['check_in']
    if 'check_out' in data:
        entry['check_out'] = data['check_out']
    if 'total_hours' in data:
        entry['total_hours'] = data['total_hours']
    if 'notes' in data:
        entry['notes'] = data['notes']
    
    return jsonify({
        'message': 'Entry updated (mock)',
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
                return jsonify({'message': 'Entry not found'}), 404
            
            entry_owner = User.query.get(entry.user_id)
            
            if user_role == 'manager':
                if entry.user_id == user_id:
                    return jsonify({'message': 'You cannot delete your own entries'}), 403
                if entry_owner.department != user_dept:
                    return jsonify({'message': 'You do not have permission'}), 403
            
            db.session.delete(entry)
            db.session.commit()
            
            return jsonify({'message': 'Entry deleted'}), 200
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': f'Error: {str(e)}'}), 500
    
    # entry_owner = next((u for u in MOCK_USERS if u['id'] == entry['user_id']), None)
    
    if user_role == 'manager':
        if entry['user_id'] == user_id:
            return jsonify({'message': 'You cannot delete your own entries'}), 403
        if entry_owner['department'] != user_dept:
            return jsonify({'message': 'You do not have permission'}), 403
    
    return jsonify({'message': 'Entry deleted (mock)'}), 200

init_database(app, db)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Starting TimeTracer with {DATABASE_TYPE}")
    app.run(host='0.0.0.0', port=port, debug=False)