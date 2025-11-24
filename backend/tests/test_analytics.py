import pytest
from app.models.question import Question
from app import db

def test_get_stats(client, auth_headers):
    # Create test questions
    # 1. Answered & Mastered (Maths)
    q1 = Question(title="Q1", subject="MATHS", difficulty=3, status="MASTERED", author_id=1)
    # 2. Answered (Reading)
    q2 = Question(title="Q2", subject="READING", difficulty=2, status="ANSWERED", author_id=1)
    # 3. Need Review (Maths)
    q3 = Question(title="Q3", subject="MATHS", difficulty=4, status="NEED_REVIEW", author_id=1)
    # 4. Unanswered (Writing)
    q4 = Question(title="Q4", subject="WRITING", difficulty=1, status="UNANSWERED", author_id=1)
    
    db.session.add_all([q1, q2, q3, q4])
    db.session.commit()
    
    response = client.get('/api/analytics/stats', headers=auth_headers)
    assert response.status_code == 200
    data = response.json
    
    # Verify overall stats
    assert data['total_questions'] == 4
    assert data['answered_questions'] == 2  # MASTERED + ANSWERED
    assert data['mastered_questions'] == 1
    assert data['need_review_questions'] == 1
    
    # Verify by subject
    assert data['by_subject']['MATHS']['total'] == 2
    assert data['by_subject']['MATHS']['mastered'] == 1
    assert data['by_subject']['READING']['total'] == 1
    assert data['by_subject']['WRITING']['total'] == 1
    
    # Verify by difficulty
    assert data['by_difficulty']['3'] == 1
    assert data['by_difficulty']['4'] == 1

def test_get_recommendations(client, auth_headers):
    # Create test questions with different priorities
    # Priority 1: Need Review (Diff 1)
    q1 = Question(title="Q1", subject="MATHS", difficulty=1, status="NEED_REVIEW", author_id=1)
    # Priority 2: Need Review (Diff 5)
    q2 = Question(title="Q2", subject="MATHS", difficulty=5, status="NEED_REVIEW", author_id=1)
    # Priority 3: Unanswered (Diff 2)
    q3 = Question(title="Q3", subject="MATHS", difficulty=2, status="UNANSWERED", author_id=1)
    # Priority 4: Answered (Should not be recommended)
    q4 = Question(title="Q4", subject="MATHS", difficulty=3, status="ANSWERED", author_id=1)
    
    db.session.add_all([q1, q2, q3, q4])
    db.session.commit()
    
    # Test default limit (10)
    response = client.get('/api/analytics/recommendations', headers=auth_headers)
    assert response.status_code == 200
    data = response.json
    
    assert len(data) == 3
    # Check order: Need Review (asc diff) -> Unanswered (asc diff)
    assert data[0]['title'] == 'Q1'
    assert data[1]['title'] == 'Q2'
    assert data[2]['title'] == 'Q3'
    
    # Test limit
    response = client.get('/api/analytics/recommendations?limit=1', headers=auth_headers)
    assert len(response.json) == 1
    assert response.json[0]['title'] == 'Q1'
    
    # Test subject filter
    q5 = Question(title="Q5", subject="READING", difficulty=1, status="NEED_REVIEW", author_id=1)
    db.session.add(q5)
    db.session.commit()
    
    response = client.get('/api/analytics/recommendations?subject=READING', headers=auth_headers)
    assert len(response.json) == 1
    assert response.json[0]['title'] == 'Q5'
