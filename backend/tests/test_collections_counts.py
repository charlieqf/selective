import pytest


def test_collection_need_review_count(client, auth_headers):
    """Verify need_review_count uses needs_review flag"""
    # Create collection
    col_response = client.post('/api/collections', json={'name': 'Math Test'}, headers=auth_headers)
    assert col_response.status_code == 201
    col = col_response.json
    
    # Create items
    client.post('/api/items', json={
        'collection_id': col['id'], 
        'difficulty': 3
    }, headers=auth_headers)
    
    client.post('/api/items', json={
        'collection_id': col['id'], 
        'difficulty': 3
    }, headers=auth_headers)
    
    # Mark one for review using the new /review endpoint
    items_response = client.get(f'/api/items?collection_id={col["id"]}', headers=auth_headers)
    item_id = items_response.json['items'][0]['id']
    client.patch(f'/api/items/{item_id}/review', json={'needs_review': True}, headers=auth_headers)
    
    # Fetch collections and verify counts
    response = client.get('/api/collections', headers=auth_headers)
    assert response.status_code == 200
    
    math_col = next((c for c in response.json if c['name'] == 'Math Test'), None)
    assert math_col is not None
    assert math_col['need_review_count'] == 1
    assert math_col['total_count'] == 2


def test_collection_counts_empty(client, auth_headers):
    """Collection with no items should have zero counts"""
    col_response = client.post('/api/collections', json={'name': 'Empty Collection'}, headers=auth_headers)
    assert col_response.status_code == 201
    
    response = client.get('/api/collections', headers=auth_headers)
    assert response.status_code == 200
    
    empty_col = next((c for c in response.json if c['name'] == 'Empty Collection'), None)
    assert empty_col is not None
    assert empty_col['need_review_count'] == 0
    assert empty_col['total_count'] == 0


def test_need_review_count_independent_of_status(client, auth_headers):
    """need_review_count should count needs_review flag, not status"""
    # Create collection
    col_response = client.post('/api/collections', json={'name': 'Status Test'}, headers=auth_headers)
    col = col_response.json
    
    # Create an item
    client.post('/api/items', json={'collection_id': col['id'], 'difficulty': 3}, headers=auth_headers)
    items_response = client.get(f'/api/items?collection_id={col["id"]}', headers=auth_headers)
    item_id = items_response.json['items'][0]['id']
    
    # Set to MASTERED
    client.patch(f'/api/items/{item_id}/status', json={'status': 'MASTERED'}, headers=auth_headers)
    
    # Mark for review (status should stay MASTERED)
    client.patch(f'/api/items/{item_id}/review', json={'needs_review': True}, headers=auth_headers)
    
    # Verify count
    response = client.get('/api/collections', headers=auth_headers)
    test_col = next((c for c in response.json if c['name'] == 'Status Test'), None)
    assert test_col['need_review_count'] == 1  # Counted because needs_review=True
