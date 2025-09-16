from flask import Flask, jsonify, request, redirect
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)

# CORS configurado para Render
CORS(app, origins=["*"])

# Configuración de la base de datos
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL or 'sqlite:///timetracer.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

db = SQLAlchemy(app)

# =================== MODELOS DE BASE DE DATOS ===================

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False, default='worker')  # admin, manager, worker
    department = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='active')  # active, inactive
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    time_entries = db.relationship('TimeEntry', backref='user', lazy=True, cascade='all, delete-orphan')
    absences = db.relationship('Absence', backref='user', lazy=True, cascade='all, delete-orphan')
    
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
    break_start = db.Column(db.DateTime, nullable=True)
    break_end = db.Column(db.DateTime, nullable=True)
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
            'break_start': self.break_start.isoformat() if self.break_start else None,
            'break_end': self.break_end.isoformat() if self.break_end else None,
            'total_hours': self.total_hours,
            'notes': self.notes,
            'created_at': self.created_at.isoformat()
        }

class Absence(db.Model):
    __tablename__ = 'absences'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    absence_type = db.Column(db.String(50), nullable=False)  # vacation, sick, personal, etc.
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, approved, rejected
    reason = db.Column(db.Text, nullable=True)
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'absence_type': self.absence_type,
            'status': self.status,
            'reason': self.reason,
            'approved_by': self.approved_by,
            'created_at': self.created_at.isoformat()
        }

# =================== RUTAS ===================

@app.route('/favicon.svg')
@app.route('/favicon.ico')
def favicon():
    return redirect('https://api.iconify.design/material-symbols:schedule-outline.svg?color=%23FFEB3B')

@app.route('/')
def home():
    return jsonify({
        'message': '🚀 TimeTracer API v2.0 with PostgreSQL',
        'status': 'success',
        'version': '2.0.0',
        'database': 'PostgreSQL' if DATABASE_URL else 'SQLite (Dev)',
        'endpoints': {
            'health': '/api/health',
            'users': '/api/users',
            'time_entries': '/api/time-entries',
            'absences': '/api/absences',
            'status': '/api/status'
        }
    })

@app.route('/api/health')
def health_check():
    try:
        # Verificar conexión a la base de datos
        db.session.execute(db.text('SELECT 1'))
        db_status = 'healthy'
        db_type = 'PostgreSQL' if DATABASE_URL else 'SQLite'
    except Exception as e:
        db_status = f'error: {str(e)}'
        db_type = 'unknown'
    
    return jsonify({
        'status': 'healthy' if db_status == 'healthy' else 'unhealthy',
        'database': db_status,
        'database_type': db_type,
        'message': 'TimeTracer backend with persistent database',
        'environment': os.getenv('FLASK_ENV', 'production'),
        'server': 'Render'
    })

@app.route('/api/users', methods=['GET', 'POST'])
def handle_users():
    if request.method == 'GET':
        try:
            users = User.query.all()
            return jsonify({
                'users': [user.to_dict() for user in users],
                'total': len(users),
                'message': 'Users retrieved successfully'
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            new_user = User(
                name=data['name'],
                email=data['email'],
                role=data.get('role', 'worker'),
                department=data['department']
            )
            db.session.add(new_user)
            db.session.commit()
            
            return jsonify({
                'message': 'User created successfully',
                'user': new_user.to_dict()
            }), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400

@app.route('/api/users/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if request.method == 'GET':
        return jsonify(user.to_dict())
    
    elif request.method == 'PUT':
        try:
            data = request.get_json()
            user.name = data.get('name', user.name)
            user.email = data.get('email', user.email)
            user.role = data.get('role', user.role)
            user.department = data.get('department', user.department)
            user.status = data.get('status', user.status)
            
            db.session.commit()
            return jsonify({
                'message': 'User updated successfully',
                'user': user.to_dict()
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400
    
    elif request.method == 'DELETE':
        try:
            db.session.delete(user)
            db.session.commit()
            return jsonify({'message': 'User deleted successfully'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400

@app.route('/api/time-entries', methods=['GET', 'POST'])
def handle_time_entries():
    if request.method == 'GET':
        try:
            user_id = request.args.get('user_id')
            date_from = request.args.get('date_from')
            date_to = request.args.get('date_to')
            
            query = TimeEntry.query
            
            if user_id:
                query = query.filter(TimeEntry.user_id == user_id)
            if date_from:
                query = query.filter(TimeEntry.date >= datetime.strptime(date_from, '%Y-%m-%d').date())
            if date_to:
                query = query.filter(TimeEntry.date <= datetime.strptime(date_to, '%Y-%m-%d').date())
            
            entries = query.order_by(TimeEntry.date.desc()).all()
            
            return jsonify({
                'time_entries': [entry.to_dict() for entry in entries],
                'total': len(entries),
                'message': 'Time entries retrieved successfully'
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            new_entry = TimeEntry(
                user_id=data['user_id'],
                date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
                check_in=datetime.fromisoformat(data['check_in']) if data.get('check_in') else None,
                check_out=datetime.fromisoformat(data['check_out']) if data.get('check_out') else None,
                break_start=datetime.fromisoformat(data['break_start']) if data.get('break_start') else None,
                break_end=datetime.fromisoformat(data['break_end']) if data.get('break_end') else None,
                total_hours=data.get('total_hours'),
                notes=data.get('notes')
            )
            
            db.session.add(new_entry)
            db.session.commit()
            
            return jsonify({
                'message': 'Time entry created successfully',
                'time_entry': new_entry.to_dict()
            }), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400

@app.route('/api/absences', methods=['GET', 'POST'])
def handle_absences():
    if request.method == 'GET':
        try:
            user_id = request.args.get('user_id')
            status = request.args.get('status')
            
            query = Absence.query
            
            if user_id:
                query = query.filter(Absence.user_id == user_id)
            if status:
                query = query.filter(Absence.status == status)
            
            absences = query.order_by(Absence.start_date.desc()).all()
            
            return jsonify({
                'absences': [absence.to_dict() for absence in absences],
                'total': len(absences),
                'message': 'Absences retrieved successfully'
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            new_absence = Absence(
                user_id=data['user_id'],
                start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date(),
                end_date=datetime.strptime(data['end_date'], '%Y-%m-%d').date(),
                absence_type=data['absence_type'],
                reason=data.get('reason'),
                status=data.get('status', 'pending')
            )
            
            db.session.add(new_absence)
            db.session.commit()
            
            return jsonify({
                'message': 'Absence created successfully',
                'absence': new_absence.to_dict()
            }), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400

@app.route('/api/status')
def get_status():
    try:
        # Verificar conexión a la base de datos
        db.session.execute(db.text('SELECT 1'))
        
        # Contar registros
        user_count = User.query.count()
        entry_count = TimeEntry.query.count()
        absence_count = Absence.query.count()
        
        return jsonify({
            'backend': '✅ PostgreSQL Backend Online',
            'database': '✅ PostgreSQL Connected & Ready',
            'deploy': '✅ Render Deployment Successful',
            'cors': '✅ CORS Configured',
            'statistics': {
                'users': user_count,
                'time_entries': entry_count,
                'absences': absence_count
            },
            'features': [
                '🔧 PostgreSQL Database Integration',
                '📊 Real User & Time Entry Management',
                '🔐 CORS configured for frontend',
                '👥 User Management (CRUD)',
                '⏰ Time Entry Tracking',
                '🏖️ Absence Management',
                '📡 Deployed on Render infrastructure'
            ],
            'database_type': 'PostgreSQL' if DATABASE_URL else 'SQLite',
            'environment': os.getenv('FLASK_ENV', 'production')
        })
        
    except Exception as e:
        return jsonify({
            'backend': '❌ Database Connection Error',
            'database': f'❌ Error: {str(e)}',
            'deploy': '⚠️ Database Configuration Required',
            'error': 'Database connection failed'
        }), 500

# =================== INICIALIZACIÓN ===================

def create_sample_data():
    """Crear datos de ejemplo solo si no existen usuarios"""
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
        print("✅ Sample users created successfully!")

@app.before_first_request
def create_tables():
    """Crear tablas y datos de ejemplo al inicializar la aplicación"""
    try:
        db.create_all()
        create_sample_data()
        print("✅ Database tables created successfully!")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")

if __name__ == '__main__':
    # Para desarrollo local
    with app.app_context():
        db.create_all()
        create_sample_data()
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)