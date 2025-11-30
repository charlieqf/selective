import pytest
from app.models.collection import Collection
from app.models.item import Item
from app import db

def test_create_collection(client, auth_headers):
    data = {
        'name': 'My Collection',
        'icon': 'book',
        'color': '#FF0000'
    }
    response = client.post('/api/collections', json=data, headers=auth_headers)
    assert response.status_code == 201
    assert response.json['name'] == 'My Collection'
    assert response.json['id'] is not None

def test_create_collection_duplicate(client, auth_headers):
    data = {'name': 'Duplicate Test'}
    client.post('/api/collections', json=data, headers=auth_headers)
    
    # Try creating again
    response = client.post('/api/collections', json=data, headers=auth_headers)
    assert response.status_code == 409
    assert 'already exists' in response.json['error']

def test_soft_delete_collection(client, auth_headers):
    # Create
    data = {'name': 'To Delete'}
    response = client.post('/api/collections', json=data, headers=auth_headers)
    collection_id = response.json['id']
    
    # Soft Delete
    patch_data = {'is_deleted': True}
    response = client.patch(f'/api/collections/{collection_id}', json=patch_data, headers=auth_headers)
    assert response.status_code == 200
    assert response.json['is_deleted'] is True
    
    # Verify not in active list
    response = client.get('/api/collections', headers=auth_headers)
    ids = [c['id'] for c in response.json]
    assert collection_id not in ids
    
    # Verify in trash
    response = client.get('/api/collections/trash', headers=auth_headers)
    ids = [c['id'] for c in response.json]
    assert collection_id in ids

def test_restore_collection(client, auth_headers):
    # Create and Delete
    data = {'name': 'To Restore'}
    response = client.post('/api/collections', json=data, headers=auth_headers)
    collection_id = response.json['id']
    client.patch(f'/api/collections/{collection_id}', json={'is_deleted': True}, headers=auth_headers)
    
    # Restore
    response = client.post(f'/api/collections/{collection_id}/restore', headers=auth_headers)
    assert response.status_code == 200
    assert response.json['is_deleted'] is False
    
    # Verify in active list
    response = client.get('/api/collections', headers=auth_headers)
    ids = [c['id'] for c in response.json]
    assert collection_id in ids

def test_restore_conflict(client, auth_headers):
    # 1. Create "Math" and delete it
    client.post('/api/collections', json={'name': 'Math'}, headers=auth_headers)
    c1_id = Collection.query.filter_by(name='Math').first().id
    client.patch(f'/api/collections/{c1_id}', json={'is_deleted': True}, headers=auth_headers)
    
    # 2. Create another "Math" (allowed because first is deleted)
    response = client.post('/api/collections', json={'name': 'Math'}, headers=auth_headers)
    assert response.status_code == 201
    
    # 3. Try to restore first "Math" (should conflict)
    response = client.post(f'/api/collections/{c1_id}/restore', headers=auth_headers)
    assert response.status_code == 409
    assert 'rename it first' in response.json['error']

def test_hard_delete_cascade(client, auth_headers):
    # Create collection and item
    c_resp = client.post('/api/collections', json={'name': 'Hard Delete'}, headers=auth_headers)
    c_id = c_resp.json['id']
    
    i_resp = client.post('/api/items', json={'collection_id': c_id, 'title': 'Item 1'}, headers=auth_headers)
    i_id = i_resp.json['id']
    
    # Must soft delete first
    client.patch(f'/api/collections/{c_id}', json={'is_deleted': True}, headers=auth_headers)
    
    # Hard delete
    response = client.delete(f'/api/collections/{c_id}', headers=auth_headers)
    assert response.status_code == 200
    
    # Verify collection gone
    assert Collection.query.get(c_id) is None
    
    # Verify item gone
    assert Item.query.get(i_id) is None

def test_hard_delete_active_collection_fails(client, auth_headers):
    # Create
    response = client.post('/api/collections', json={'name': 'Active'}, headers=auth_headers)
    c_id = response.json['id']
    
    # Try hard delete without soft delete
    response = client.delete(f'/api/collections/{c_id}', headers=auth_headers)
    assert response.status_code == 400
    assert 'must be in trash' in response.json['error']

def test_stats_update_after_collection_change(client, auth_headers):
    # 1. Create collection and item
    c_resp = client.post('/api/collections', json={'name': 'Stats Test'}, headers=auth_headers)
    c_id = c_resp.json['id']
    
    client.post('/api/items', json={'collection_id': c_id, 'title': 'Item 1', 'status': 'MASTERED'}, headers=auth_headers)
    
    # 2. Check stats
    stats = client.get('/api/analytics/stats', headers=auth_headers).json
    assert str(c_id) in stats['by_collection']
    assert stats['by_collection'][str(c_id)]['mastered'] == 1
    
    # 3. Soft delete collection
    client.patch(f'/api/collections/{c_id}', json={'is_deleted': True}, headers=auth_headers)
    
    # 4. Check stats (should be gone from active list)
    stats = client.get('/api/analytics/stats', headers=auth_headers).json
    assert str(c_id) not in stats['by_collection']
    
    # 5. Restore collection
    client.post(f'/api/collections/{c_id}/restore', headers=auth_headers)
    
    # 6. Check stats (should be back)
    stats = client.get('/api/analytics/stats', headers=auth_headers).json
    assert str(c_id) in stats['by_collection']
    assert stats['by_collection'][str(c_id)]['mastered'] == 1
