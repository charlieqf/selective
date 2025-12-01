import pytest
from app.models.collection import Collection
from app import db

def test_list_items_includes_tags(client, auth_headers):
    """Test that GET /api/items includes tags in the response"""
    
    # Create a collection
    c = Collection(user_id=1, name="Test Collection", type="CUSTOM")
    db.session.add(c)
    db.session.commit()
    
    # Create item with tags
    data = {
        'collection_id': c.id,
        'title': 'Tagged Item',
        'tags': ['tag1', 'tag2']
    }
    client.post('/api/items', json=data, headers=auth_headers)
    
    # List items
    response = client.get('/api/items', headers=auth_headers)
    assert response.status_code == 200
    
    items = response.json['items']
    assert len(items) == 1
    item = items[0]
    
    # Verify tags are present
    assert 'tags' in item
    assert len(item['tags']) == 2
    tag_names = [t['name'] for t in item['tags']]
    assert 'tag1' in tag_names
    assert 'tag2' in tag_names
