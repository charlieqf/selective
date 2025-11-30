import pytest
from app.models.item import Item
from app import db

def test_get_stats(client, auth_headers):
    # Create test items
    # 1. Answered & Mastered (Maths)
    q1 = Item(title="Q1", subject="MATHS", difficulty=3, status="MASTERED", author_id=1)
    # 2. Answered (Reading)
    q2 = Item(title="Q2", subject="READING", difficulty=2, status="ANSWERED", author_id=1)
    # 3. Need Review (Maths)
    q3 = Item(title="Q3", subject="MATHS", difficulty=4, status="NEED_REVIEW", author_id=1)
    # 4. Unanswered (Writing)
    q4 = Item(title="Q4", subject="WRITING", difficulty=1, status="UNANSWERED", author_id=1)
    
    db.session.add_all([q1, q2, q3, q4])
    db.session.commit()
    
    # Create a collection
    from app.models.collection import Collection
    c1 = Collection(user_id=1, name="My Collection", icon="star", color="#000000")
    db.session.add(c1)
    db.session.commit()
    
    # Update items to belong to collection
    q1.collection_id = c1.id
    q3.collection_id = c1.id
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
    
    # Verify by collection
    # Note: keys in JSON are strings, so we use str(c1.id)
    col_id = str(c1.id)
    assert col_id in data['by_collection']
    assert data['by_collection'][col_id]['total'] == 2 # q1 and q3
    assert data['by_collection'][col_id]['mastered'] == 1 # q1 is MASTERED
    assert data['by_collection'][col_id]['name'] == "My Collection"
    
    # Verify by difficulty
    assert data['by_difficulty']['3'] == 1
    assert data['by_difficulty']['4'] == 1

def test_get_recommendations(client, auth_headers):
    # Create test items with different priorities
    # Priority 1: Need Review (Diff 1)
    q1 = Item(title="Q1", subject="MATHS", difficulty=1, status="NEED_REVIEW", author_id=1)
    # Priority 2: Need Review (Diff 5)
    q2 = Item(title="Q2", subject="MATHS", difficulty=5, status="NEED_REVIEW", author_id=1)
    # Priority 3: Unanswered (Diff 2)
    q3 = Item(title="Q3", subject="MATHS", difficulty=2, status="UNANSWERED", author_id=1)
    # Priority 4: Answered (Should not be recommended)
    q4 = Item(title="Q4", subject="MATHS", difficulty=3, status="ANSWERED", author_id=1)
    
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
    q5 = Item(title="Q5", subject="READING", difficulty=1, status="NEED_REVIEW", author_id=1)
    db.session.add(q5)
    db.session.commit()
    
    response = client.get('/api/analytics/recommendations?subject=READING', headers=auth_headers)
    assert len(response.json) == 1
    assert response.json[0]['title'] == 'Q5'

    # Test collection filter
    # Create a collection and link items
    from app.models.collection import Collection
    c2 = Collection(user_id=1, name="Rec Collection", type="CUSTOM")
    db.session.add(c2)
    db.session.commit()
    
    q6 = Item(title="Q6", collection_id=c2.id, difficulty=1, status="NEED_REVIEW", author_id=1)
    q7 = Item(title="Q7", collection_id=c2.id, difficulty=2, status="UNANSWERED", author_id=1)
    # q8 not in collection
    q8 = Item(title="Q8", difficulty=1, status="NEED_REVIEW", author_id=1)
    
    db.session.add_all([q6, q7, q8])
    db.session.commit()
    
    response = client.get(f'/api/analytics/recommendations?collection_id={c2.id}', headers=auth_headers)
    assert response.status_code == 200
    data = response.json
    assert len(data) == 2
    assert data[0]['title'] == 'Q6'
    assert data[1]['title'] == 'Q7'
