import pytest


def test_update_status_success(client, auth_headers, seed_item):
    """Happy path: author can change status to any valid value"""
    item_id = seed_item['id']
    for status in ['ANSWERED', 'MASTERED', 'UNANSWERED']:
        response = client.patch(f'/api/items/{item_id}/status', 
            json={'status': status}, headers=auth_headers)
        assert response.status_code == 200
        assert response.json['status'] == status


def test_update_status_invalid_status(client, auth_headers, seed_item):
    """Invalid status value returns 400 - NEED_REVIEW is no longer valid"""
    response = client.patch(f'/api/items/{seed_item["id"]}/status', 
        json={'status': 'NEED_REVIEW'}, headers=auth_headers)
    assert response.status_code == 400
    assert 'Invalid status' in response.json['error']


def test_update_status_missing_body(client, auth_headers, seed_item):
    """Missing request body returns 400"""
    response = client.patch(f'/api/items/{seed_item["id"]}/status', 
        headers=auth_headers, content_type='application/json')
    assert response.status_code == 400


def test_update_status_empty_body(client, auth_headers, seed_item):
    """Empty JSON body returns 400"""
    response = client.patch(f'/api/items/{seed_item["id"]}/status', 
        json={}, headers=auth_headers)
    assert response.status_code == 400
    assert 'status field is required' in response.json['error']


def test_update_status_not_owner(client, other_user_headers, seed_item):
    """Non-owner gets 404 (not 403 to hide existence)"""
    response = client.patch(f'/api/items/{seed_item["id"]}/status', 
        json={'status': 'ANSWERED'}, headers=other_user_headers)
    assert response.status_code == 404


def test_update_status_nonexistent(client, auth_headers):
    """Non-existent item returns 404"""
    response = client.patch('/api/items/99999/status', 
        json={'status': 'ANSWERED'}, headers=auth_headers)
    assert response.status_code == 404


def test_toggle_review_flag(client, auth_headers, seed_item):
    """Test toggling needs_review flag"""
    item_id = seed_item['id']
    
    # Initially should be False
    assert seed_item.get('needs_review', False) == False
    
    # Mark for review
    response = client.patch(f'/api/items/{item_id}/review',
        json={'needs_review': True}, headers=auth_headers)
    assert response.status_code == 200
    assert response.json['needs_review'] == True
    assert response.json['status'] == seed_item['status']  # Status unchanged
    
    # Unmark
    response = client.patch(f'/api/items/{item_id}/review',
        json={'needs_review': False}, headers=auth_headers)
    assert response.status_code == 200
    assert response.json['needs_review'] == False


def test_toggle_review_preserves_status(client, auth_headers, seed_item):
    """Toggling review flag should not affect learning status"""
    item_id = seed_item['id']
    
    # Set to MASTERED
    client.patch(f'/api/items/{item_id}/status',
        json={'status': 'MASTERED'}, headers=auth_headers)
    
    # Mark for review
    response = client.patch(f'/api/items/{item_id}/review',
        json={'needs_review': True}, headers=auth_headers)
    assert response.json['status'] == 'MASTERED'  # Status preserved
    assert response.json['needs_review'] == True
    
    # Unmark
    response = client.patch(f'/api/items/{item_id}/review',
        json={'needs_review': False}, headers=auth_headers)
    assert response.json['status'] == 'MASTERED'  # Still MASTERED
    assert response.json['needs_review'] == False


def test_toggle_review_toggle_mode(client, auth_headers, seed_item):
    """Test toggle mode when no explicit value is given"""
    item_id = seed_item['id']
    
    # Send empty body to toggle (initially False -> True)
    response = client.patch(f'/api/items/{item_id}/review',
        json={}, headers=auth_headers)
    assert response.status_code == 200
    assert response.json['needs_review'] == True
    
    # Toggle again (True -> False)
    response = client.patch(f'/api/items/{item_id}/review',
        json={}, headers=auth_headers)
    assert response.json['needs_review'] == False


def test_filter_items_by_needs_review(client, auth_headers, seed_item):
    """Test filtering items by needs_review flag"""
    item_id = seed_item['id']
    
    # Mark for review
    client.patch(f'/api/items/{item_id}/review',
        json={'needs_review': True}, headers=auth_headers)
    
    # Filter by needs_review=true
    response = client.get('/api/items?needs_review=true', headers=auth_headers)
    assert response.status_code == 200
    items = response.json['items']
    assert len(items) >= 1
    assert all(item['needs_review'] == True for item in items)
