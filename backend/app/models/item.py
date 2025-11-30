from app import db
from datetime import datetime
import json

class Item(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))  # Optional title
    
    # Core Fields
    # subject kept for migration/compatibility, will be deprecated
    subject = db.Column(db.String(50), nullable=True, index=True) 
    
    # New: Collection Relationship
    collection_id = db.Column(db.Integer, db.ForeignKey('collections.id'), nullable=True)
    
    difficulty = db.Column(db.Integer, default=3)  # 1-5, default 3
    status = db.Column(db.String(20), default='UNANSWERED')  # UNANSWERED, ANSWERED, MASTERED, NEED_REVIEW
    
    # Content Fields (JSON storage)
    images = db.Column(db.JSON)  
    content_text = db.Column(db.Text)
    
    # Metadata
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Statistics
    attempts = db.Column(db.Integer, default=0)
    success_rate = db.Column(db.Float, default=0.0)
    
    # Constraints
    __table_args__ = (
        db.CheckConstraint('difficulty >= 1 AND difficulty <= 5', name='check_difficulty_range'),
        db.CheckConstraint("status IN ('UNANSWERED', 'ANSWERED', 'MASTERED', 'NEED_REVIEW')", name='check_status_valid'),
    )
    
    def set_images(self, images_list):
        self.images = images_list
        
    def get_images(self):
        return self.images if self.images else []
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'subject': self.subject, # Legacy field
            'collection_id': self.collection_id, # New field
            'difficulty': self.difficulty,
            'status': self.status,
            'images': self.get_images(),
            'content_text': self.content_text,
            'author_id': self.author_id,
            'created_at': self.created_at.isoformat(),
            'attempts': self.attempts
        }
