import pytest
from app.models.user import User
from app.models.question import Question
from unittest.mock import patch
from app import db


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
    from app.models.pending_upload import PendingUpload
    from app import db
    
    with patch('app.routes.upload.cloudinary.uploader.destroy') as mock_destroy:
        mock_destroy.return_value = {'result': 'ok'}
        
        # Seed database to simulate a recent upload by this user
        public_id = 'selective-questions/img123'
        pending_upload = PendingUpload(
            public_id=public_id,
            user_id=1  # Matches the test user ID
        )
        db.session.add(pending_upload)
        db.session.commit()
        
        # Delete the pending upload
        response = client.delete('/api/upload', json={'public_id': public_id}, headers=auth_headers)
        assert response.status_code == 200
        mock_destroy.assert_called_with(public_id)
        
        # Verify it was removed from database
        assert PendingUpload.query.filter_by(public_id=public_id).first() is None

def test_upload_delete_unauthorized(client):
    response = client.delete('/api/upload', json={'public_id': 'img123'})
    assert response.status_code == 401

def test_get_questions_list(client, auth_headers):
    # Create multiple questions
    q1 = Question(title="Q1", subject="MATHS", difficulty=1, author_id=1)
    q2 = Question(title="Q2", subject="READING", difficulty=2, author_id=1)
    db.session.add_all([q1, q2])
    db.session.commit()
    
    response = client.get('/api/questions', headers=auth_headers)
    assert response.status_code == 200
    data = response.json
    assert data['total'] == 2
    assert len(data['questions']) == 2

def test_get_questions_filter(client, auth_headers):
    q1 = Question(title="Math Q", subject="MATHS", difficulty=1, status="UNANSWERED", author_id=1)
    q2 = Question(title="Read Q", subject="READING", difficulty=2, status="ANSWERED", author_id=1)
    db.session.add_all([q1, q2])
    db.session.commit()
    
    # Filter by subject
    response = client.get('/api/questions?subject=MATHS', headers=auth_headers)
    assert response.json['total'] == 1
    assert response.json['questions'][0]['title'] == 'Math Q'
    
    # Filter by difficulty
    response = client.get('/api/questions?difficulty=2', headers=auth_headers)
    assert response.json['total'] == 1
    assert response.json['questions'][0]['title'] == 'Read Q'
    
    # Filter by status
    response = client.get('/api/questions?status=ANSWERED', headers=auth_headers)
    assert response.json['total'] == 1
    assert response.json['questions'][0]['title'] == 'Read Q'

def test_get_questions_sort(client, auth_headers):
    q1 = Question(title="Diff 1", difficulty=1, subject="MATHS", author_id=1)
    q2 = Question(title="Diff 5", difficulty=5, subject="MATHS", author_id=1)
    q3 = Question(title="Diff 3", difficulty=3, subject="MATHS", author_id=1)
    db.session.add_all([q1, q2, q3])
    db.session.commit()
    
    # Sort by difficulty ASC
    response = client.get('/api/questions?sort_by=difficulty&sort_direction=asc', headers=auth_headers)
    data = response.json['questions']
    assert data[0]['difficulty'] == 1
    assert data[1]['difficulty'] == 3
    assert data[2]['difficulty'] == 5
    
    # Sort by difficulty DESC
    response = client.get('/api/questions?sort_by=difficulty&sort_direction=desc', headers=auth_headers)
    data = response.json['questions']
    assert data[0]['difficulty'] == 5
    assert data[1]['difficulty'] == 3
    assert data[2]['difficulty'] == 1

