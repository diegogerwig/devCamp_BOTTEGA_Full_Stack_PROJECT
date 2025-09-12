from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Crear instancia de Flask
app = Flask(__name__)

# Configuración CORS para desarrollo
CORS(app, origins=["http://localhost:3000"])

# Configuración de la base de datos
if os.getenv('DATABASE_URL'):
    # Producción (Render)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
else:
    # Desarrollo local
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///timetracer.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar extensiones
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Modelo básico para prueba
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='worker')
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# Rutas básicas
@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'ok',
        'message': 'TimeTracer API is running',
        'version': '1.0.0'
    })

@app.route('/api/users')
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@app.route('/api/test-db')
def test_db():
    try:
        # Intentar crear las tablas
        db.create_all()
        
        # Verificar si existe algún usuario de prueba
        test_user = User.query.first()
        if not test_user:
            # Crear usuario de prueba
            test_user = User(
                email='admin@timetracer.com',
                name='Administrador',
                role='admin'
            )
            db.session.add(test_user)
            db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Database connected successfully',
            'user_count': User.query.count()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Database error: {str(e)}'
        }), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)