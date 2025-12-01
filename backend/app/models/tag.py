from app import db
from datetime import datetime
from sqlalchemy import func

class Tag(db.Model):
    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Unique constraint per user (case-insensitive)
    __table_args__ = (
        db.Index('idx_tags_user_name_lower', 'user_id', func.lower(name), unique=True),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }
