import pytest
from app.models.user import User
from app.models.item import Item
from unittest.mock import patch
from app import db


def test_create_item(client, auth_headers):
    data = {
        'subject': 'MATHS',
        'difficulty': 3,
        'title': 'Test Item',
        'content_text': 'What is 1+1?',
        'images': [{'url': 'http://example.com/img.jpg', 'public_id': 'img123'}]
    }
    response = client.post('/api/items', json=data, headers=auth_headers)
    assert response.status_code == 201
    assert response.json['title'] == 'Test Item'
    assert response.json['images'][0]['public_id'] == 'img123'

def test_create_item_validation(client, auth_headers):
    # Invalid difficulty
    data = {'subject': 'MATHS', 'difficulty': 6}
    response = client.post('/api/items', json=data, headers=auth_headers)
    assert response.status_code == 400

def test_update_item_ownership(client, auth_headers, other_auth_headers):
    # User 1 creates item
    data = {'subject': 'MATHS', 'difficulty': 3}
    response = client.post('/api/items', json=data, headers=auth_headers)
    item_id = response.json['id']
    
    # User 2 tries to update
    update_data = {'title': 'Hacked'}
    response = client.patch(f'/api/items/{item_id}', json=update_data, headers=other_auth_headers)
    assert response.status_code == 403

def test_delete_item_cleanup(client, auth_headers):
    # Mock cloudinary
    with patch('app.routes.items.cloudinary.uploader.destroy') as mock_destroy:
        mock_destroy.return_value = {'result': 'ok'}
        
        # Create item with image
        data = {
            'subject': 'MATHS', 
            'images': [{'url': 'http://example.com/img.jpg', 'public_id': 'img123'}]
        }
        response = client.post('/api/items', json=data, headers=auth_headers)
        item_id = response.json['id']
        
        # Delete item
        response = client.delete(f'/api/items/{item_id}', headers=auth_headers)
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

def test_get_items_list(client, auth_headers):
    # Create multiple items
    q1 = Item(title="Q1", subject="MATHS", difficulty=1, author_id=1)
    q2 = Item(title="Q2", subject="READING", difficulty=2, author_id=1)
    db.session.add_all([q1, q2])
    db.session.commit()
    
    response = client.get('/api/items', headers=auth_headers)
    assert response.status_code == 200
    data = response.json
    assert data['total'] == 2
    assert len(data['items']) == 2

def test_get_items_filter(client, auth_headers):
    q1 = Item(title="Math Q", subject="MATHS", difficulty=1, status="UNANSWERED", author_id=1)
    q2 = Item(title="Read Q", subject="READING", difficulty=2, status="ANSWERED", author_id=1)
    db.session.add_all([q1, q2])
    db.session.commit()
    
    # Filter by subject
    response = client.get('/api/items?subject=MATHS', headers=auth_headers)
    assert response.json['total'] == 1
    assert response.json['items'][0]['title'] == 'Math Q'
    
    # Filter by difficulty
    response = client.get('/api/items?difficulty=2', headers=auth_headers)
    assert response.json['total'] == 1
    assert response.json['items'][0]['title'] == 'Read Q'
    
    # Filter by status
    response = client.get('/api/items?status=ANSWERED', headers=auth_headers)
    assert response.json['total'] == 1
    assert response.json['items'][0]['title'] == 'Read Q'

def test_get_items_sort(client, auth_headers):
    q1 = Item(title="Diff 1", difficulty=1, subject="MATHS", author_id=1)
    q2 = Item(title="Diff 5", difficulty=5, subject="MATHS", author_id=1)
    q3 = Item(title="Diff 3", difficulty=3, subject="MATHS", author_id=1)
    db.session.add_all([q1, q2, q3])
    db.session.commit()
    
    # Sort by difficulty ASC
    response = client.get('/api/items?sort_by=difficulty&sort_direction=asc', headers=auth_headers)
    data = response.json['items']
    assert data[0]['difficulty'] == 1
    assert data[1]['difficulty'] == 3
    assert data[2]['difficulty'] == 5
    
    # Sort by difficulty DESC
    response = client.get('/api/items?sort_by=difficulty&sort_direction=desc', headers=auth_headers)
    data = response.json['items']
    assert data[0]['difficulty'] == 5

def test_create_item_invalid_collection(client, auth_headers, other_auth_headers):
    from app.models.collection import Collection
    from app import db
    
    # Create a collection for other user
    c_other = Collection(user_id=2, name="Other Collection", type="CUSTOM")
    db.session.add(c_other)
    db.session.commit()
    
    # 1. Try to create item with non-existent collection
    data = {'subject': 'MATHS', 'difficulty': 3, 'collection_id': 9999}
    response = client.post('/api/items', json=data, headers=auth_headers)
    assert response.status_code == 404
    
    # 2. Try to create item with other user's collection
    data = {'subject': 'MATHS', 'difficulty': 3, 'collection_id': c_other.id}
    response = client.post('/api/items', json=data, headers=auth_headers)
    assert response.status_code == 403

def test_get_items_filter_collection(client, auth_headers):
    from app.models.collection import Collection
    from app import db
    
    # Create collections
    c1 = Collection(user_id=1, name="C1", type="CUSTOM")
    c2 = Collection(user_id=1, name="C2", type="CUSTOM")
    db.session.add_all([c1, c2])
    db.session.commit()
    
    # Create items
    q1 = Item(title="Q1", collection_id=c1.id, difficulty=1, author_id=1)
    q2 = Item(title="Q2", collection_id=c2.id, difficulty=1, author_id=1)
    q3 = Item(title="Q3", collection_id=c1.id, difficulty=1, author_id=1)
    db.session.add_all([q1, q2, q3])
    db.session.commit()
    
    # Filter by collection c1
    response = client.get(f'/api/items?collection_id={c1.id}', headers=auth_headers)
    assert response.status_code == 200
    data = response.json
    assert data['total'] == 2
    titles = [i['title'] for i in data['items']]
    assert 'Q1' in titles
    assert 'Q3' in titles
    assert 'Q2' not in titles


