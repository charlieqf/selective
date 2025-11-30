import pytest
from app.models.item import Item
from app.models.answer import Answer
from app import db

def test_submit_answer_success(client, auth_headers, app):
    """Test submitting an answer successfully"""
    with app.app_context():
        # Create a question (Item) for the test user (user_id=1 from auth_headers)
        item = Item(
            title="Test Question",
            subject="MATHS",
            difficulty=3,
            content_text="What is 1+1?",
            author_id=1,
            status="NEED_REVIEW"
        )
        db.session.add(item)
        db.session.commit()
        item_id = item.id

    # Submit correct answer
    data = {
        'is_correct': True,
        'content': '2',
        'duration_seconds': 10
    }
    # Updated to use /api/items
    response = client.post(f'/api/items/{item_id}/answers', json=data, headers=auth_headers)
    
    assert response.status_code == 201
    assert response.json['item_status'] == 'MASTERED'
    
    with app.app_context():
        # Verify DB
        ans = Answer.query.filter_by(item_id=item_id).first()
        assert ans is not None
        assert ans.is_correct is True
        assert ans.duration_seconds == 10
        
        q = Item.query.get(item_id)
        assert q.status == 'MASTERED'
        assert q.attempts == 1

def test_submit_answer_unauthorized(client, auth_headers, other_auth_headers, app):
    """Test submitting an answer to another user's question (should fail)"""
    with app.app_context():
        # Create a question for user 1 (testuser)
        item = Item(
            title="User 1 Question",
            subject="MATHS",
            difficulty=3,
            author_id=1
        )
        db.session.add(item)
        db.session.commit()
        item_id = item.id

    # User 2 tries to answer
    data = {'is_correct': True}
    response = client.post(f'/api/items/{item_id}/answers', json=data, headers=other_auth_headers)
    
    assert response.status_code == 403
    assert 'Unauthorized' in response.json['error']

def test_get_answer_history_success(client, auth_headers, app):
    """Test retrieving answer history"""
    with app.app_context():
        item = Item(
            title="History Question",
            subject="MATHS",
            difficulty=3,
            author_id=1
        )
        db.session.add(item)
        db.session.commit()
        item_id = item.id
        
        # Add some answers with explicit timestamps to ensure order
        from datetime import datetime, timedelta
        now = datetime.utcnow()
        a1 = Answer(item_id=item_id, user_id=1, is_correct=False, duration_seconds=5, created_at=now - timedelta(minutes=1))
        a2 = Answer(item_id=item_id, user_id=1, is_correct=True, duration_seconds=3, created_at=now)
        db.session.add_all([a1, a2])
        db.session.commit()

    response = client.get(f'/api/items/{item_id}/answers', headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json
    assert len(data) == 2
    # Should be ordered by created_at desc (latest first)
    assert data[0]['is_correct'] is True
    assert data[1]['is_correct'] is False

def test_get_answer_history_unauthorized(client, auth_headers, other_auth_headers, app):
    """Test retrieving history of another user's question (should fail)"""
    with app.app_context():
        item = Item(
            title="User 1 Question",
            subject="MATHS",
            difficulty=3,
            author_id=1
        )
        db.session.add(item)
        db.session.commit()
        item_id = item.id

    response = client.get(f'/api/items/{item_id}/answers', headers=other_auth_headers)
    
    assert response.status_code == 403

def test_answer_updates_stats(client, auth_headers, app):
    """Test that attempts and success_rate are updated correctly"""
    with app.app_context():
        item = Item(
            title="Stats Question",
            subject="MATHS",
            difficulty=3,
            author_id=1
        )
        db.session.add(item)
        db.session.commit()
        item_id = item.id
        
    # 1. Submit Correct Answer
    client.post(f'/api/items/{item_id}/answers', json={'is_correct': True}, headers=auth_headers)
    
    with app.app_context():
        q = Item.query.get(item_id)
        assert q.attempts == 1
        assert q.success_rate == 100.0 # 1/1
        
    # 2. Submit Incorrect Answer
    client.post(f'/api/items/{item_id}/answers', json={'is_correct': False}, headers=auth_headers)
    
    with app.app_context():
        q = Item.query.get(item_id)
        assert q.attempts == 2
        assert q.success_rate == 50.0 # 1/2
        
    # 3. Submit Correct Answer
    client.post(f'/api/items/{item_id}/answers', json={'is_correct': True}, headers=auth_headers)
    
    with app.app_context():
        q = Item.query.get(item_id)
        assert q.attempts == 3
        assert abs(q.success_rate - 66.7) < 0.1 # 2/3 = 66.7%
