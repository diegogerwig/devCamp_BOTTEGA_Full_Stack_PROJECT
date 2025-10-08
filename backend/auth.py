from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'message': 'Invalid or expired token', 'error': str(e)}), 401
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get('role') != 'admin':
                return jsonify({'message': 'Access denied. Admin role required'}), 403
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'message': 'Authentication error', 'error': str(e)}), 401
    return decorated

def manager_or_admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get('role') not in ['admin', 'manager']:
                return jsonify({'message': 'Access denied. Manager or admin role required'}), 403
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'message': 'Authentication error', 'error': str(e)}), 401
    return decorated