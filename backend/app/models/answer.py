from app import db
from datetime import datetime

class Answer(db.Model):
    __tablename__ = 'answers'

    id = db.Column(db.Integer, primary_key=True)
    
    # Relationships
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Content (Optional for self-marking, but good to have)
    content = db.Column(db.Text) 
    
    # Result
    is_correct = db.Column(db.Boolean, nullable=False)
    
    # Metadata
    duration_seconds = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Backrefs are usually defined on the "One" side (User, Question), 
    # but we can define them here if needed, or rely on the other side.
    # Let's keep it simple for now.
    
    def to_dict(self):
        return {
            'id': self.id,
            'item_id': self.item_id,
            'user_id': self.user_id,
            'content': self.content,
            'is_correct': self.is_correct,
            'duration_seconds': self.duration_seconds,
            'created_at': self.created_at.isoformat()
        }
