import pytest
from app import create_app, db
from app.models.user import User
from app.models.question import Question
from unittest.mock import patch

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_headers(client):
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
def other_auth_headers(client):
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

def test_create_question(client, auth_headers):
    data = {
        'subject': 'MATHS',
        'difficulty': 3,
        'title': 'Test Question',
        'content_text': 'What is 1+1?',
        'images': [{'url': 'http://example.com/img.jpg', 'public_id': 'img123'}]
    }
    response = client.post('/api/questions', json=data, headers=auth_headers)
    assert response.status_code == 201
    assert response.json['title'] == 'Test Question'
    assert response.json['images'][0]['public_id'] == 'img123'

def test_create_question_validation(client, auth_headers):
    # Invalid subject
    data = {'subject': 'INVALID', 'difficulty': 3}
    response = client.post('/api/questions', json=data, headers=auth_headers)
    assert response.status_code == 400
    
    # Invalid difficulty
    data = {'subject': 'MATHS', 'difficulty': 6}
    response = client.post('/api/questions', json=data, headers=auth_headers)
    assert response.status_code == 400

def test_update_question_ownership(client, auth_headers, other_auth_headers):
    # User 1 creates question
    data = {'subject': 'MATHS', 'difficulty': 3}
    response = client.post('/api/questions', json=data, headers=auth_headers)
    question_id = response.json['id']
    
    # User 2 tries to update
    update_data = {'title': 'Hacked'}
    response = client.patch(f'/api/questions/{question_id}', json=update_data, headers=other_auth_headers)
    assert response.status_code == 403

def test_delete_question_cleanup(client, auth_headers):
    # Mock cloudinary
    with patch('app.routes.questions.cloudinary.uploader.destroy') as mock_destroy:
        mock_destroy.return_value = {'result': 'ok'}
        
        # Create question with image
        data = {
            'subject': 'MATHS', 
            'images': [{'url': 'http://example.com/img.jpg', 'public_id': 'img123'}]
        }
        response = client.post('/api/questions', json=data, headers=auth_headers)
        question_id = response.json['id']
        
        # Delete question
        response = client.delete(f'/api/questions/{question_id}', headers=auth_headers)
        assert response.status_code == 200
        
        # Verify destroy called
        mock_destroy.assert_called_with('img123')

def test_upload_delete(client, auth_headers):
    with patch('app.routes.upload.cloudinary.uploader.destroy') as mock_destroy:
        mock_destroy.return_value = {'result': 'ok'}
        
        response = client.delete('/api/upload', json={'public_id': 'img123'}, headers=auth_headers)
        assert response.status_code == 200
        mock_destroy.assert_called_with('img123')

def test_upload_delete_unauthorized(client):
    response = client.delete('/api/upload', json={'public_id': 'img123'})
    assert response.status_code == 401
