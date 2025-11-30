from app import db
from datetime import datetime
from sqlalchemy import Computed, UniqueConstraint

class Collection(db.Model):
    __tablename__ = 'collections'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20), default='SUBJECT', nullable=False)  # SUBJECT, CUSTOM, etc.
    icon = db.Column(db.String(50))  # Optional icon name
    color = db.Column(db.String(20)) # Optional hex color
    
    # Soft Delete
    is_deleted = db.Column(db.Boolean, default=False, index=True)
    deleted_at = db.Column(db.DateTime, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Generated Column for Uniqueness (MySQL/TiDB compatible)
    # active_name is name if is_deleted is 0, else NULL.
    # This allows multiple deleted items with same name, but only one active item.
    active_name = db.Column(db.String(100), Computed("CASE WHEN is_deleted = 0 THEN name ELSE NULL END"))

    __table_args__ = (
        UniqueConstraint('user_id', 'active_name', name='uq_user_active_collection'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'icon': self.icon,
            'color': self.color,
            'is_deleted': self.is_deleted,
            'created_at': self.created_at.isoformat()
        }
