import os
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

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

def get_mock_users():
    return MOCK_USERS