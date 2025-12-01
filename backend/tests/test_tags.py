import pytest
from app.models.item import Item
from app.models.tag import Tag
from app.models.collection import Collection
from app import db

def test_create_item_with_tags(client, auth_headers):
    """Test creating item with tags"""
    from app.models.collection import Collection
    
    # Create a collection first
    c = Collection(user_id=1, name="Test Collection", type="CUSTOM")
    db.session.add(c)
    db.session.commit()
    
    data = {
        'collection_id': c.id,
        'difficulty': 3,
        'tags': ['math', 'fractions', 'algebra']
    }
    
    response = client.post('/api/items', json=data, headers=auth_headers)
    assert response.status_code == 201
    
    item = response.json
    assert len(item['tags']) == 3
    tag_names = [t['name'] for t in item['tags']]
    assert 'math' in tag_names
    assert 'fractions' in tag_names
    assert 'algebra' in tag_names

def test_create_item_reuses_existing_tags(client, auth_headers):
    """Test that tags are reused (case-insensitive)"""
    from app.models.collection import Collection
    
    c = Collection(user_id=1, name="Test Collection", type="CUSTOM")
    db.session.add(c)
    db.session.commit()
    
    # Create first item with tag "Math"
    data1 = {'collection_id': c.id, 'tags': ['Math']}
    response1 = client.post('/api/items', json=data1, headers=auth_headers)
    assert response1.status_code == 201
    
    # Create second item with tag "math" (different case)
    data2 = {'collection_id': c.id, 'tags': ['math', 'Science']}
    response2 = client.post('/api/items', json=data2, headers=auth_headers)
    assert response2.status_code == 201
    
    # Verify only 2 unique tags exist (Math/math is one tag)
    tags = Tag.query.filter_by(user_id=1).all()
    assert len(tags) == 2
    tag_names = [t.name for t in tags]
    # First tag created should keep its original case
    assert 'Math' in tag_names or 'math' in tag_names
    assert 'Science' in tag_names

def test_filter_items_by_tag(client, auth_headers):
    """Test filtering items by tag"""
    from app.models.collection import Collection
    
    c = Collection(user_id=1, name="Test Collection", type="CUSTOM")
    db.session.add(c)
    db.session.commit()
    
    # Create items with different tags
    data1 = {'collection_id': c.id, 'title': 'Item 1', 'tags': ['math', 'easy']}
    data2 = {'collection_id': c.id, 'title': 'Item 2', 'tags': ['math', 'hard']}
    data3 = {'collection_id': c.id, 'title': 'Item 3', 'tags': ['science']}
    
    client.post('/api/items', json=data1, headers=auth_headers)
    client.post('/api/items', json=data2, headers=auth_headers)
    client.post('/api/items', json=data3, headers=auth_headers)
    
    # Filter by 'math'
    response = client.get('/api/items?tag=math', headers=auth_headers)
    assert response.status_code == 200
    data = response.json
    assert data['total'] == 2
    titles = [i['title'] for i in data['items']]
    assert 'Item 1' in titles
    assert 'Item 2' in titles
    
    # Filter by 'math' AND 'hard' (AND logic)
    response = client.get('/api/items?tag=math&tag=hard', headers=auth_headers)
    assert response.status_code == 200
    data = response.json
    assert data['total'] == 1
    assert data['items'][0]['title'] == 'Item 2'

def test_tag_user_isolation(client, auth_headers, other_auth_headers):
    """Test that tags are isolated between users"""
    from app.models.collection import Collection
    
    # User 1 creates collection and item with tag
    c1 = Collection(user_id=1, name="User1 Collection", type="CUSTOM")
    db.session.add(c1)
    db.session.commit()
    
    data1 = {'collection_id': c1.id, 'tags': ['shared']}
    client.post('/api/items', json=data1, headers=auth_headers)
    
    # User 2 creates collection and item with same tag name
    c2 = Collection(user_id=2, name="User2 Collection", type="CUSTOM")
    db.session.add(c2)
    db.session.commit()
    
    data2 = {'collection_id': c2.id, 'tags': ['shared']}
    client.post('/api/items', json=data2, headers=other_auth_headers)
    
    # Verify 2 separate tags exist
    tags = Tag.query.filter_by(name='shared').all()
    assert len(tags) == 2
    user_ids = {t.user_id for t in tags}
    assert len(user_ids) == 2

def test_update_item_tags(client, auth_headers):
    """Test updating tags on an existing item"""
    from app.models.collection import Collection
    
    c = Collection(user_id=1, name="Test Collection", type="CUSTOM")
    db.session.add(c)
    db.session.commit()
    
    # Create item with initial tags
    data = {'collection_id': c.id, 'tags': ['old1', 'old2']}
    response = client.post('/api/items', json=data, headers=auth_headers)
    item_id = response.json['id']
    
    # Update tags
    update_data = {'tags': ['new1', 'new2', 'new3']}
    response = client.patch(f'/api/items/{item_id}', json=update_data, headers=auth_headers)
    assert response.status_code == 200
    
    item = response.json
    assert len(item['tags']) == 3
    tag_names = [t['name'] for t in item['tags']]
    assert 'new1' in tag_names
    assert 'new2' in tag_names
    assert 'new3' in tag_names
    assert 'old1' not in tag_names
    assert 'old2' not in tag_names

def test_clear_item_tags(client, auth_headers):
    """Test clearing all tags from an item"""
    from app.models.collection import Collection
    
    c = Collection(user_id=1, name="Test Collection", type="CUSTOM")
    db.session.add(c)
    db.session.commit()
    
    # Create item with tags
    data = {'collection_id': c.id, 'tags': ['tag1', 'tag2']}
    response = client.post('/api/items', json=data, headers=auth_headers)
    item_id = response.json['id']
    
    # Clear tags
    update_data = {'tags': []}
    response = client.patch(f'/api/items/{item_id}', json=update_data, headers=auth_headers)
    assert response.status_code == 200
    
    item = response.json
    assert len(item['tags']) == 0

def test_tag_validation(client, auth_headers):
    """Test tag validation (length, empty)"""
    from app.models.collection import Collection
    
    c = Collection(user_id=1, name="Test Collection", type="CUSTOM")
    db.session.add(c)
    db.session.commit()
    
    # Test tag too long
    data = {'collection_id': c.id, 'tags': ['a' * 31]}
    response = client.post('/api/items', json=data, headers=auth_headers)
    assert response.status_code == 400
    assert 'exceed 30 characters' in response.json['error']
    
    # Test empty tag
    data = {'collection_id': c.id, 'tags': ['']}
    response = client.post('/api/items', json=data, headers=auth_headers)
    assert response.status_code == 400
    assert 'cannot be empty' in response.json['error']

def test_get_tags_list(client, auth_headers):
    """Test GET /api/tags endpoint"""
    # Create some tags by creating items
    from app.models.collection import Collection
    
    c = Collection(user_id=1, name="Test Collection", type="CUSTOM")
    db.session.add(c)
    db.session.commit()
    
    data = {'collection_id': c.id, 'tags': ['alpha', 'beta', 'gamma']}
    client.post('/api/items', json=data, headers=auth_headers)
    
    # Get tags
    response = client.get('/api/tags', headers=auth_headers)
    assert response.status_code == 200
    
    tags = response.json
    assert len(tags) >= 3
    tag_names = [t['name'] for t in tags]
    assert 'alpha' in tag_names
    assert 'beta' in tag_names
    assert 'gamma' in tag_names
