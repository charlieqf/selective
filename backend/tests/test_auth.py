import pytest
from app.models.user import User
from app import db

def test_register(client):
    # Test registration
    data = {
        "username": "newuser",
        "email": "new@example.com",
        "password": "password123"
    }
    response = client.post('/api/auth/register', json=data)
    assert response.status_code == 201
    assert 'token' in response.json
    assert response.json['user']['username'] == 'newuser'
    
    # Verify user in DB
    user = User.query.filter_by(username='newuser').first()
    assert user is not None
    assert user.email == 'new@example.com'

def test_register_duplicate(client):
    # Create existing user
    user = User(username="existing", email="existing@example.com")
    user.set_password("password")
    db.session.add(user)
    db.session.commit()
    
    # Try to register same username
    data = {
        "username": "existing",
        "email": "other@example.com",
        "password": "password123"
    }
    response = client.post('/api/auth/register', json=data)
    assert response.status_code == 409
    
    # Try to register same email
    data = {
        "username": "other",
        "email": "existing@example.com",
        "password": "password123"
    }
    response = client.post('/api/auth/register', json=data)
    assert response.status_code == 409

def test_login(client):
    # Create user
    user = User(username="loginuser", email="login@example.com")
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()
    
    # Test successful login
    data = {
        "username": "loginuser",
        "password": "password123"
    }
    response = client.post('/api/auth/login', json=data)
    assert response.status_code == 200
    assert 'token' in response.json
    
    # Test invalid password
    data['password'] = "wrongpass"
    response = client.post('/api/auth/login', json=data)
    assert response.status_code == 401
    
    # Test non-existent user
    data['username'] = "nouser"
    response = client.post('/api/auth/login', json=data)
    assert response.status_code == 401

def test_me(client, auth_headers):
    # Test get current user with valid token
    response = client.get('/api/auth/me', headers=auth_headers)
    assert response.status_code == 200
    assert response.json['username'] == 'testuser' # Created in auth_headers fixture

def test_me_unauthorized(client):
    # Test get current user without token
    response = client.get('/api/auth/me')
    assert response.status_code == 401
