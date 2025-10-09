from flask import Flask, jsonify, request, redirect
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, get_jwt
from flask_bcrypt import Bcrypt
import os
from datetime import datetime, timedelta
from auth import token_required, admin_required, manager_or_admin_required
from src.init_db import init_database
from src.date_utils import parse_datetime_string

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

# =================== DATABASE INITIALIZATION ===================
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise RuntimeError("❌ DATABASE_URL environment variable is required")

print(f"🔍 DATABASE_URL found: {DATABASE_URL[:50]}...")

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
    from src.models import init_models
    
    db = SQLAlchemy(app)
    User, TimeEntry = init_models(db)
    
    # Verify connection
    with app.app_context():
        db.session.execute(db.text('SELECT 1'))
    
    print("✅ PostgreSQL connected successfully!")
    
except ImportError as e:
    raise RuntimeError(f"❌ pg8000 not installed: {e}")
except Exception as e:
    raise RuntimeError(f"❌ Database connection failed: {e}")

# =================== UTILITY ROUTES ===================
@app.route('/favicon.svg')
@app.route('/favicon.ico')
def favicon():
    return redirect('https://api.iconify.design/material-symbols:schedule-outline.svg?color=%23FFEB3B')

@app.route('/')
def home():
    """Root endpoint - Live statistics + API summary"""
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
        
        # Build response
        base_url = request.url_root.rstrip('/')
        response_data = {
            'app': 'TimeTracer API',
            'version': '1.0.0',
            'status': 'online',
            'database': {
                'type': 'PostgreSQL',
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
                },
                'last_database_change': last_change.isoformat() if last_change else None
            },
            'endpoints': {
                'public': [
                    f"GET {base_url}/",
                    f"GET {base_url}/api/health",
                    f"GET {base_url}/api/docs"
                ],
                'authentication': [
                    f"POST {base_url}/api/auth/login"
                ],
                'protected_jwt': [
                    f"GET {base_url}/api/auth/me",
                    f"GET {base_url}/api/users",
                    f"POST {base_url}/api/users (admin)",
                    f"PUT {base_url}/api/users/:id (admin)",
                    f"DELETE {base_url}/api/users/:id (admin)",
                    f"GET {base_url}/api/time-entries",
                    f"POST {base_url}/api/time-entries",
                    f"PUT {base_url}/api/time-entries/:id (manager/admin)",
                    f"DELETE {base_url}/api/time-entries/:id (manager/admin)"
                ]
            },
            'documentation': f"{base_url}/api/docs",
            'links': {
                'frontend': 'https://time-tracer-bottega-front.onrender.com',
                'github': 'https://github.com/diegogerwig/devCamp_BOTTEGA_Full_Stack_PROJECT'
            }
        }
        
        import json
        from flask import Response
        json_str = json.dumps(response_data, ensure_ascii=False, indent=2)
        return Response(json_str, mimetype='application/json')
        
    except Exception as e:
        return jsonify({
            'app': 'TimeTracer API',
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/api/health')
def health_check():
    """Health check for monitoring"""
    try:
        db.session.execute(db.text('SELECT 1'))
        return jsonify({
            'status': 'healthy',
            'database': 'connected'
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e)
        }), 503

@app.route('/api/docs')
def api_documentation():
    """API documentation"""
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
                'GET /api/users': 'List users (filtered by role)',
                'GET /api/time-entries': 'List entries (filtered by role)',
                'POST /api/time-entries': 'Create/update entry'
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
            'worker': 'Own entries only'
        }
    })

# =================== AUTHENTICATION ===================
@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login - returns JWT token"""
    print("=" * 50)
    print("🔐 LOGIN ATTEMPT")
    
    try:
        data = request.get_json()
        print(f"📦 Request data received: {data is not None}")
        
        if not data:
            print("❌ No request body")
            return jsonify({'message': 'Request body is required'}), 400
        
        email = data.get('email')
        password = data.get('password')
        print(f"📧 Email: {email}")
        print(f"🔑 Password received: {bool(password)}")
        
        if not email or not password:
            print("❌ Missing email or password")
            return jsonify({'message': 'Email and password required'}), 400
        
        # Database query
        print(f"🔍 Searching user with email: {email}")
        user = User.query.filter_by(email=email).first()
        
        if not user:
            print(f"❌ User not found: {email}")
            return jsonify({'message': 'Invalid credentials'}), 401
        
        print(f"✅ User found: {user.name} (ID: {user.id})")
        print(f"👤 Role: {user.role}")
        print(f"🏢 Department: {user.department}")
        
        # Password check
        print("🔐 Checking password...")
        password_valid = bcrypt.check_password_hash(user.users_password, password)
        print(f"🔐 Password valid: {password_valid}")
        
        if not password_valid:
            print("❌ Invalid password")
            return jsonify({'message': 'Invalid credentials'}), 401
        
        # Create JWT token
        print("🎫 Creating access token...")
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={
                'email': user.email,
                'role': user.role,
                'name': user.name,
                'department': user.department
            }
        )
        print("✅ Token created successfully")
        
        response_data = {
            'message': 'Login successful',
            'access_token': access_token,
            'user': user.to_dict()
        }
        print("✅ Login successful!")
        print("=" * 50)
        
        return jsonify(response_data), 200
        
    except AttributeError as e:
        print(f"❌ AttributeError (model issue): {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': f'Model error: {str(e)}'}), 500
        
    except Exception as e:
        print(f"❌ Unexpected error in login: {e}")
        print(f"❌ Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': f'Server error: {str(e)}'}), 500

@app.route('/api/auth/me', methods=['GET'])
@token_required
def get_current_user():
    """Get current authenticated user"""
    try:
        user_id = int(get_jwt_identity())
        print(f"🔍 Getting user with ID: {user_id}")
        
        user = User.query.get(user_id)
        
        if not user:
            print(f"❌ User not found with ID: {user_id}")
            return jsonify({'message': 'User not found'}), 404
        
        print(f"✅ User found: {user.name}")
        user_dict = user.to_dict()
        
        return jsonify({'user': user_dict}), 200
        
    except AttributeError as e:
        print(f"❌ Model error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': f'Model error: {str(e)}'}), 500
        
    except Exception as e:
        print(f"❌ Get current user error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': f'Server error: {str(e)}'}), 500

# =================== USER MANAGEMENT ===================
@app.route('/api/users', methods=['GET'])
@token_required
def get_users():
    """Get users list (filtered by role and department)"""
    try:
        claims = get_jwt()
        user_role = claims.get('role')
        user_dept = claims.get('department')
        user_id = int(get_jwt_identity())
        
        if user_role == 'admin':
            users = User.query.all()
        elif user_role == 'manager':
            users = User.query.filter_by(department=user_dept).all()
        else:
            users = User.query.filter_by(id=user_id).all()
        
        return jsonify({
            'users': [user.to_dict() for user in users],
            'total': len(users)
        })
        
    except Exception as e:
        print(f"Get users error: {e}")
        return jsonify({'message': 'Server error'}), 500

@app.route('/api/users', methods=['POST'])
@admin_required
def create_user():
    """Create new user (admin only)"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'Request body is required'}), 400
        
        required_fields = ['name', 'email', 'password', 'department']
        if not all(field in data for field in required_fields):
            return jsonify({'message': 'Missing required fields'}), 400
        
        new_user_role = data.get('role', 'worker')
        if new_user_role not in ['worker', 'manager', 'admin']:
            return jsonify({'message': 'Invalid role'}), 400
        
        # Check if email exists
        existing = User.query.filter_by(email=data['email']).first()
        if existing:
            return jsonify({'message': 'Email already registered'}), 400
        
        # Create user
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
        print(f"Create user error: {e}")
        return jsonify({'message': f'Server error: {str(e)}'}), 500

@app.route('/api/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    """Update user (admin only)"""
    try:
        data = request.get_json()
        current_user_id = int(get_jwt_identity())
        
        if user_id == current_user_id:
            return jsonify({'message': 'Cannot edit your own user'}), 403
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        # Update fields
        if 'name' in data:
            user.name = data['name']
            
        if 'email' in data:
            existing = User.query.filter(
                User.email == data['email'],
                User.id != user_id
            ).first()
            if existing:
                return jsonify({'message': 'Email already in use'}), 400
            user.email = data['email']
            
        if 'role' in data:
            if data['role'] not in ['worker', 'manager', 'admin']:
                return jsonify({'message': 'Invalid role'}), 400
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
        print(f"Update user error: {e}")
        return jsonify({'message': f'Server error: {str(e)}'}), 500

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """Delete user (admin only)"""
    try:
        current_user_id = int(get_jwt_identity())
        
        if user_id == current_user_id:
            return jsonify({'message': 'Cannot delete your own user'}), 403
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        # Delete user's time entries first
        TimeEntry.query.filter_by(user_id=user_id).delete()
        
        # Delete user
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': 'User deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Delete user error: {e}")
        return jsonify({'message': f'Server error: {str(e)}'}), 500

# =================== TIME ENTRIES ===================
@app.route('/api/time-entries', methods=['GET'])
@token_required
def get_time_entries():
    """Get time entries (filtered by role and department)"""
    try:
        claims = get_jwt()
        user_role = claims.get('role')
        user_dept = claims.get('department')
        user_id = int(get_jwt_identity())
        
        if user_role == 'admin':
            entries = TimeEntry.query.order_by(TimeEntry.check_in.desc()).all()
        elif user_role == 'manager':
            dept_users = User.query.filter_by(department=user_dept).all()
            user_ids = [u.id for u in dept_users]
            entries = TimeEntry.query.filter(
                TimeEntry.user_id.in_(user_ids)
            ).order_by(TimeEntry.check_in.desc()).all()
        else:
            entries = TimeEntry.query.filter_by(
                user_id=user_id
            ).order_by(TimeEntry.check_in.desc()).all()
        
        return jsonify({
            'time_entries': [entry.to_dict() for entry in entries],
            'total': len(entries)
        })
        
    except Exception as e:
        print(f"Get time entries error: {e}")
        return jsonify({'message': 'Server error'}), 500

@app.route('/api/time-entries', methods=['POST'])
@token_required
def create_time_entry():
    """Create or update time entry"""
    try:
        claims = get_jwt()
        user_role = claims.get('role')
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'Request body is required'}), 400
        
        if 'date' not in data or 'check_in' not in data:
            return jsonify({'message': 'Date and check-in time are required'}), 400
        
        target_user_id = data.get('user_id', user_id)
        
        # Validate permissions
        if user_role == 'worker' and target_user_id != user_id:
            return jsonify({'message': 'Cannot create entries for other users'}), 403
        
        # Parse date
        entry_date_str = data['date']
        if isinstance(entry_date_str, str):
            entry_date = datetime.strptime(entry_date_str, '%Y-%m-%d').date()
        else:
            entry_date = entry_date_str
        
        # Parse times
        check_in = parse_datetime_string(data['check_in'])
        check_out = parse_datetime_string(data.get('check_out')) if data.get('check_out') else None
        
        if not check_in:
            return jsonify({'message': 'Invalid check-in format'}), 400
        
        # Check for open entries
        if not check_out:
            open_entry = TimeEntry.query.filter_by(
                user_id=target_user_id,
                check_out=None
            ).first()
            
            if open_entry:
                return jsonify({
                    'message': f'Open entry exists from {open_entry.date}. Close it first.',
                    'open_entry': open_entry.to_dict()
                }), 400
        
        # Check if updating existing entry
        existing = None
        if 'entry_id' in data:
            existing = TimeEntry.query.get(data['entry_id'])
        else:
            existing = TimeEntry.query.filter_by(
                user_id=target_user_id,
                date=entry_date,
                check_out=None
            ).first()
        
        if existing:
            # Update existing
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
            # Create new
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
        print(f"Create time entry error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': f'Server error: {str(e)}'}), 500

@app.route('/api/time-entries/<int:entry_id>', methods=['PUT'])
@manager_or_admin_required
def update_time_entry(entry_id):
    """Update time entry (manager/admin only)"""
    try:
        claims = get_jwt()
        user_role = claims.get('role')
        user_dept = claims.get('department')
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        entry = TimeEntry.query.get(entry_id)
        if not entry:
            return jsonify({'message': 'Entry not found'}), 404
        
        entry_owner = User.query.get(entry.user_id)
        
        # Validate permissions
        if user_role == 'manager':
            if entry.user_id == user_id:
                return jsonify({'message': 'Cannot edit your own entries'}), 403
            if entry_owner.department != user_dept:
                return jsonify({'message': 'No permission for this department'}), 403
        
        # Update fields
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
        print(f"Update time entry error: {e}")
        return jsonify({'message': f'Server error: {str(e)}'}), 500

@app.route('/api/time-entries/<int:entry_id>', methods=['DELETE'])
@manager_or_admin_required
def delete_time_entry(entry_id):
    """Delete time entry (manager/admin only)"""
    try:
        claims = get_jwt()
        user_role = claims.get('role')
        user_dept = claims.get('department')
        user_id = int(get_jwt_identity())
        
        entry = TimeEntry.query.get(entry_id)
        if not entry:
            return jsonify({'message': 'Entry not found'}), 404
        
        entry_owner = User.query.get(entry.user_id)
        
        # Validate permissions
        if user_role == 'manager':
            if entry.user_id == user_id:
                return jsonify({'message': 'Cannot delete your own entries'}), 403
            if entry_owner.department != user_dept:
                return jsonify({'message': 'No permission for this department'}), 403
        
        db.session.delete(entry)
        db.session.commit()
        
        return jsonify({'message': 'Entry deleted'}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Delete time entry error: {e}")
        return jsonify({'message': f'Server error: {str(e)}'}), 500

# =================== INITIALIZATION ===================
init_database(app, db)

# =================== DEBUG ENDPOINT (remove in production) ===================
@app.route('/api/debug/db-status', methods=['GET'])
def debug_db_status():
    """Debug endpoint to check database status"""
    try:
        # Check connection
        db.session.execute(db.text('SELECT 1'))
        
        # Get counts
        user_count = User.query.count()
        entry_count = TimeEntry.query.count()
        
        # Get sample users (without passwords)
        users = User.query.limit(5).all()
        user_list = []
        for u in users:
            try:
                user_list.append({
                    'id': u.id,
                    'name': u.name,
                    'email': u.email,
                    'role': u.role,
                    'department': u.department,
                    'has_password': bool(u.users_password)
                })
            except Exception as e:
                user_list.append({
                    'error': str(e),
                    'user_id': u.id if hasattr(u, 'id') else 'unknown'
                })
        
        return jsonify({
            'database': 'connected',
            'users': {
                'total': user_count,
                'sample': user_list
            },
            'time_entries': {
                'total': entry_count
            }
        }), 200
        
    except Exception as e:
        import traceback
        return jsonify({
            'database': 'error',
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Starting TimeTracer API on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)