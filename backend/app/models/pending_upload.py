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
        import cloudinary.uploader
        
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        expired = PendingUpload.query.filter(PendingUpload.created_at < cutoff).all()
        
        count = 0
        for upload in expired:
            try:
                # Delete from Cloudinary
                cloudinary.uploader.destroy(upload.public_id)
                # Delete from DB
                db.session.delete(upload)
                count += 1
            except Exception as e:
                print(f"Failed to delete expired upload {upload.public_id}: {e}")
                
        db.session.commit()
        return count
