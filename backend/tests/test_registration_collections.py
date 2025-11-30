import pytest
from app.models.user import User
from app.models.collection import Collection
from app import db

def test_registration_creates_collections(client, app):
    # Register a new user
    data = {
        "username": "new_reg_user",
        "email": "new_reg@test.com",
        "password": "password123",
        "role": "student"
    }
    
    response = client.post('/api/auth/register', json=data)
    assert response.status_code == 201
    user_id = response.json['user']['id']
    
    with app.app_context():
        # Verify user exists
        user = User.query.get(user_id)
        assert user is not None
        
        # Verify collections
        collections = Collection.query.filter_by(user_id=user_id).all()
        assert len(collections) == 4
        
        names = [c.name for c in collections]
        assert "READING" in names
        assert "WRITING" in names
        assert "MATHS" in names
        assert "THINKING_SKILLS" in names
        
        print(f"User {user_id} has collections: {names}")
