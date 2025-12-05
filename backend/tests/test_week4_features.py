import pytest
from app.models.user import User
from app.models.pending_upload import PendingUpload
from unittest.mock import patch, MagicMock
from app import db
from datetime import datetime, timedelta


class TestPendingUploadSecurity:
    """Tests for upload ownership and security"""
    
    def test_upload_ownership_protection(self, client, auth_headers, other_auth_headers):
        """Test that users cannot delete other users' pending uploads"""
        with patch('app.routes.upload.cloudinary.uploader.destroy') as mock_destroy:
            # User 1 uploads an image
            public_id = 'selective-questions/user1_image.jpg'
            pending_upload = PendingUpload(
                public_id=public_id,
                user_id=1  # User 1
            )
            db.session.add(pending_upload)
            db.session.commit()
            
            # User 2 tries to delete User 1's image
            response = client.delete('/api/upload', 
                                    json={'public_id': public_id}, 
                                    headers=other_auth_headers)
            
            # Should be forbidden
            assert response.status_code == 403
            assert 'Unauthorized' in response.json['error']
            
            # Cloudinary should NOT be called
            mock_destroy.assert_not_called()
            
            # Image should still exist in database
            assert PendingUpload.query.filter_by(public_id=public_id).first() is not None
    
    def test_cloudinary_failure_preserves_database(self, client, auth_headers):
        """Test that DB record is not deleted when Cloudinary fails"""
        public_id = 'selective-questions/test_image.jpg'
        pending_upload = PendingUpload(
            public_id=public_id,
            user_id=1
        )
        db.session.add(pending_upload)
        db.session.commit()
        
        # Mock Cloudinary to return failure
        with patch('app.routes.upload.cloudinary.uploader.destroy') as mock_destroy:
            mock_destroy.return_value = {'result': 'error'}
            
            response = client.delete('/api/upload', 
                                    json={'public_id': public_id}, 
                                    headers=auth_headers)
            
            # Should return error
            assert response.status_code == 400
            assert 'Failed to delete image from storage' in response.json['error']
            
            # Database record should STILL EXIST (for retry)
            assert PendingUpload.query.filter_by(public_id=public_id).first() is not None
    
    def test_successful_delete_removes_from_database(self, client, auth_headers):
        """Test that successful Cloudinary delete also removes DB record"""
        public_id = 'selective-questions/test_image.jpg'
        pending_upload = PendingUpload(
            public_id=public_id,
            user_id=1
        )
        db.session.add(pending_upload)
        db.session.commit()
        
        with patch('app.routes.upload.cloudinary.uploader.destroy') as mock_destroy:
            mock_destroy.return_value = {'result': 'ok'}
            
            response = client.delete('/api/upload', 
                                    json={'public_id': public_id}, 
                                    headers=auth_headers)
            
            assert response.status_code == 200
            
            # NOW database record should be gone
            assert PendingUpload.query.filter_by(public_id=public_id).first() is None
    
    def test_cleanup_expired_uploads(self, app):
        """Test that old pending uploads are cleaned up"""
        with app.app_context():
            # Create old upload (25 hours ago)
            old_upload = PendingUpload(
                public_id='selective-questions/old.jpg',
                user_id=1
            )
            old_upload.created_at = datetime.utcnow() - timedelta(hours=25)
            db.session.add(old_upload)
            
            # Create recent upload
            recent_upload = PendingUpload(
                public_id='selective-questions/recent.jpg',
                user_id=1
            )
            db.session.add(recent_upload)
            db.session.commit()
            
            # Mock Cloudinary
            with patch('cloudinary.uploader.destroy') as mock_destroy:
                mock_destroy.return_value = {'result': 'ok'}
                
                # Run cleanup
                deleted_count = PendingUpload.cleanup_expired(hours=24)
                
                # Should delete 1
                assert deleted_count == 1
                
                # Verify Cloudinary was called for the old image
                mock_destroy.assert_called_once_with('selective-questions/old.jpg')
                
                # Old should be gone, recent should remain
                assert PendingUpload.query.filter_by(public_id='selective-questions/old.jpg').first() is None
                assert PendingUpload.query.filter_by(public_id='selective-questions/recent.jpg').first() is not None


class TestRegistrationRoles:
    """Tests for user registration with different roles"""
    
    def test_register_as_parent(self, client):
        """Test registering with parent role"""
        import uuid
        username = f'parent_user_{uuid.uuid4().hex[:8]}'
        data = {
            'username': username,
            'email': f'{username}@example.com',
            'password': 'password123',
            'role': 'parent'
        }
        response = client.post('/api/auth/register', json=data)
        
        assert response.status_code == 201
        assert response.json['user']['role'] == 'parent'
        
        # Verify in database
        user = User.query.filter_by(username=username).first()
        assert user is not None
        assert user.role == 'parent'
    
    def test_register_as_tutor(self, client):
        """Test registering with tutor role"""
        import uuid
        username = f'tutor_user_{uuid.uuid4().hex[:8]}'
        data = {
            'username': username,
            'email': f'{username}@example.com',
            'password': 'password123',
            'role': 'tutor'
        }
        response = client.post('/api/auth/register', json=data)
        
        assert response.status_code == 201
        assert response.json['user']['role'] == 'tutor'
    
    def test_register_invalid_role_defaults_to_student(self, client):
        """Test that invalid role defaults to student"""
        import uuid
        username = f'test_user_{uuid.uuid4().hex[:8]}'
        data = {
            'username': username,
            'email': f'{username}@example.com',
            'password': 'password123',
            'role': 'admin'  # Invalid role
        }
        response = client.post('/api/auth/register', json=data)
        
        assert response.status_code == 201
        # Should default to student
        assert response.json['user']['role'] == 'student'
    
    def test_register_without_role_defaults_to_student(self, client):
        """Test that omitting role defaults to student"""
        import uuid
        username = f'test_user_{uuid.uuid4().hex[:8]}'
        data = {
            'username': username,
            'email': f'{username}@example.com',
            'password': 'password123'
            # No role specified
        }
        response = client.post('/api/auth/register', json=data)
        
        assert response.status_code == 201
        assert response.json['user']['role'] == 'student'
