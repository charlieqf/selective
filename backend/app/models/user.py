from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=True)  # Nullable for OAuth users
    role = db.Column(db.String(20), default='student')  # student, parent, admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # OAuth fields
    google_id = db.Column(db.String(100), unique=True, nullable=True, index=True)
    auth_provider = db.Column(db.String(20), default='local', nullable=False)  # 'local', 'google'
    avatar_url = db.Column(db.String(500), nullable=True)
    
    # Relationships
    items = db.relationship('Item', backref='author', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        if self.password_hash is None:
            return False
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat(),
            'avatar_url': self.avatar_url,
            'auth_provider': self.auth_provider
        }

