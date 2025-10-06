from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'message': 'Token inválido o expirado', 'error': str(e)}), 401
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
            current_user = get_jwt_identity()
            if current_user.get('role') != 'admin':
                return jsonify({'message': 'Acceso denegado. Se requiere rol de administrador'}), 403
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'message': 'Error de autenticación', 'error': str(e)}), 401
    return decorated

def manager_or_admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
            current_user = get_jwt_identity()
            if current_user.get('role') not in ['admin', 'manager']:
                return jsonify({'message': 'Acceso denegado. Se requiere rol de manager o admin'}), 403
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'message': 'Error de autenticación', 'error': str(e)}), 401
    return decorated