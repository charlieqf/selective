import sys
import os
import pytest

# 添加backend目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.user import User
from app.models.question import Question

@pytest.fixture
def app():
    """创建测试应用"""
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """创建测试客户端"""
    return app.test_client()

@pytest.fixture
def auth_headers(app, client):
    """创建认证header"""
    with app.app_context():
        # Create a user and login
        user = User(username='testuser', email='test@example.com')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        
        response = client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'password'
        })
        token = response.json['token']
        return {'Authorization': f'Bearer {token}'}

@pytest.fixture
def other_auth_headers(app, client):
    """创建另一个用户的认证header"""
    with app.app_context():
        # Create another user
        user = User(username='otheruser', email='other@example.com')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        
        response = client.post('/api/auth/login', json={
            'username': 'otheruser',
            'password': 'password'
        })
        token = response.json['token']
        return {'Authorization': f'Bearer {token}'}
