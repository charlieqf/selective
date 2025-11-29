import pytest
from app.models.question import Question
from app.models.answer import Answer
from app import db

def test_submit_answer_success(client, auth_headers, app):
    """Test submitting an answer successfully"""
    with app.app_context():
        # Create a question for the test user (user_id=1 from auth_headers)
        question = Question(
            title="Test Question",
            subject="MATHS",
            difficulty=3,
            content_text="What is 1+1?",
            author_id=1,
            status="NEED_REVIEW"
        )
        db.session.add(question)
        db.session.commit()
        question_id = question.id

    # Submit correct answer
    data = {
        'is_correct': True,
        'content': '2',
        'duration_seconds': 10
    }
    response = client.post(f'/api/questions/{question_id}/answers', json=data, headers=auth_headers)
    
    assert response.status_code == 201
    assert response.json['question_status'] == 'MASTERED'
    
    with app.app_context():
        # Verify DB
        ans = Answer.query.filter_by(question_id=question_id).first()
        assert ans is not None
        assert ans.is_correct is True
        assert ans.duration_seconds == 10
        
        q = Question.query.get(question_id)
        assert q.status == 'MASTERED'
        assert q.attempts == 1

def test_submit_answer_unauthorized(client, auth_headers, other_auth_headers, app):
    """Test submitting an answer to another user's question (should fail)"""
    with app.app_context():
        # Create a question for user 1 (testuser)
        # We need to make sure we use the ID of the user from auth_headers
        # Since auth_headers runs first, testuser should be ID 1.
        question = Question(
            title="User 1 Question",
            subject="MATHS",
            difficulty=3,
            author_id=1
        )
        db.session.add(question)
        db.session.commit()
        question_id = question.id

    # User 2 tries to answer
    data = {'is_correct': True}
    response = client.post(f'/api/questions/{question_id}/answers', json=data, headers=other_auth_headers)
    
    assert response.status_code == 403
    assert 'Unauthorized' in response.json['error']

def test_get_answer_history_success(client, auth_headers, app):
    """Test retrieving answer history"""
    with app.app_context():
        question = Question(
            title="History Question",
            subject="MATHS",
            difficulty=3,
            author_id=1
        )
        db.session.add(question)
        db.session.commit()
        question_id = question.id
        
        # Add some answers with explicit timestamps to ensure order
        from datetime import datetime, timedelta
        now = datetime.utcnow()
        a1 = Answer(question_id=question_id, user_id=1, is_correct=False, duration_seconds=5, created_at=now - timedelta(minutes=1))
        a2 = Answer(question_id=question_id, user_id=1, is_correct=True, duration_seconds=3, created_at=now)
        db.session.add_all([a1, a2])
        db.session.commit()

    response = client.get(f'/api/questions/{question_id}/answers', headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json
    assert len(data) == 2
    # Should be ordered by created_at desc (latest first)
    assert data[0]['is_correct'] is True
    assert data[1]['is_correct'] is False

def test_get_answer_history_unauthorized(client, auth_headers, other_auth_headers, app):
    """Test retrieving history of another user's question (should fail)"""
    with app.app_context():
        question = Question(
            title="User 1 Question",
            subject="MATHS",
            difficulty=3,
            author_id=1
        )
        db.session.add(question)
        db.session.commit()
        question_id = question.id

    response = client.get(f'/api/questions/{question_id}/answers', headers=other_auth_headers)
    
    assert response.status_code == 403
