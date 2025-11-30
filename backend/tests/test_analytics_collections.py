
import pytest
from app.models.item import Item
from app.models.collection import Collection
from app.models.user import User
from app import db

def test_analytics_includes_collections(client, auth_headers):
    # Get test user
    test_user = User.query.filter_by(username='testuser').first()
    assert test_user is not None

    # Create collections
    c1 = Collection(user_id=test_user.id, name="Maths", type="SUBJECT", color="#ff0000")
    c2 = Collection(user_id=test_user.id, name="Science", type="CUSTOM", color="#00ff00")
    db.session.add_all([c1, c2])
    db.session.commit()
    
    # Create items linked to collections
    i1 = Item(author_id=test_user.id, collection_id=c1.id, status='ANSWERED', difficulty=1)
    i2 = Item(author_id=test_user.id, collection_id=c1.id, status='MASTERED', difficulty=2)
    i3 = Item(author_id=test_user.id, collection_id=c2.id, status='UNANSWERED', difficulty=3)
    db.session.add_all([i1, i2, i3])
    db.session.commit()
    
    # Get analytics
    response = client.get('/api/analytics/stats', headers=auth_headers)
    assert response.status_code == 200
    data = response.json
    
    # Verify by_collection exists
    assert 'by_collection' in data
    by_col = data['by_collection']
    
    # Verify c1 stats
    assert str(c1.id) in by_col
    assert by_col[str(c1.id)]['name'] == "Maths"
    assert by_col[str(c1.id)]['total'] == 2
    assert by_col[str(c1.id)]['answered'] == 2 # ANSWERED + MASTERED
    assert by_col[str(c1.id)]['mastered'] == 1
    
    # Verify c2 stats
    assert str(c2.id) in by_col
    assert by_col[str(c2.id)]['name'] == "Science"
    assert by_col[str(c2.id)]['total'] == 1
    assert by_col[str(c2.id)]['answered'] == 0
