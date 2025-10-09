from datetime import datetime
from date_utils import datetime_to_string

def init_models(db):
    class User(db.Model):
        __tablename__ = 'users'
        
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), nullable=False)
        email = db.Column(db.String(120), unique=True, nullable=False)
        users_password = db.Column('users_password', db.String(255), nullable=False)
        role = db.Column(db.String(20), nullable=False, default='worker')
        department = db.Column(db.String(50), nullable=False)
        status = db.Column(db.String(20), nullable=False, default='active')
        created_at = db.Column(db.DateTime, default=datetime.now)
        
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
        created_at = db.Column(db.DateTime, default=datetime.now)
        
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
    
    return User, TimeEntry