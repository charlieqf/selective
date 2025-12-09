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
    status = db.Column(db.String(20), default='UNANSWERED')  # UNANSWERED, ANSWERED, MASTERED
    needs_review = db.Column(db.Boolean, default=False, nullable=False)  # Independent review flag
    
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
        db.CheckConstraint("status IN ('UNANSWERED', 'ANSWERED', 'MASTERED')", name='check_status_valid'),
    )
    
    # Relationships
    tags = db.relationship('Tag', secondary='item_tags', backref=db.backref('items', lazy='dynamic'))
    
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
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'attempts': self.attempts,
            'tags': [tag.to_dict() for tag in self.tags],
            'needs_review': self.needs_review
        }

# Association Table
item_tags = db.Table('item_tags',
    db.Column('item_id', db.Integer, db.ForeignKey('items.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True),
    db.Index('idx_item_tags_tag_item', 'tag_id', 'item_id')
)

