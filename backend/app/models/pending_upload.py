from app import db
from datetime import datetime, timedelta

class PendingUpload(db.Model):
    """Track temporary image uploads before they are attached to questions"""
    __tablename__ = 'pending_uploads'
    
    public_id = db.Column(db.String(255), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship
    user = db.relationship('User', backref='pending_uploads')
    
    @staticmethod
    def cleanup_expired(hours=24):
        """Remove uploads older than specified hours"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        expired = PendingUpload.query.filter(PendingUpload.created_at < cutoff).all()
        for upload in expired:
            db.session.delete(upload)
        db.session.commit()
        return len(expired)
