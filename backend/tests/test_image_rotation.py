import pytest
import json
from app.models.item import Item

def test_rotate_image_success(client, auth_headers):
    """Test successful image rotation via dedicated endpoint"""
    # 1. Create an item with multiple images
    data = {
        'title': 'Rotation Endpoint Test',
        'subject': 'MATHS',
        'difficulty': 3,
        'images': [
            {'url': 'http://example.com/img1.jpg', 'public_id': 'pid_1'},
            {'url': 'http://example.com/img2.jpg', 'public_id': 'pid_2'}
        ]
    }
    response = client.post('/api/items', json=data, headers=auth_headers)
    print(f"Create API Response: {response.data}")
    assert response.status_code == 201, f"Failed to create item: {response.data}"
    
    response_json = response.json
    assert 'id' in response_json, f"ID missing in response: {response_json}"
    item_id = response_json['id']

    # 2. Rotate the second image (index 1) to 90 degrees
    rotate_data = {
        'image_index': 1,
        'rotation': 90
    }
    response = client.patch(f'/api/items/{item_id}/rotate', json=rotate_data, headers=auth_headers)
    assert response.status_code == 200, f"Rotate failed: {response.data}"
    
    # Verify immediate response
    assert response.json['rotation'] == 90
    assert response.json['image_index'] == 1
    assert 'updated_at' in response.json

    # 3. Verify persistence
    response = client.get(f'/api/items/{item_id}', headers=auth_headers)
    images = response.json['images']
    assert images[1]['rotation'] == 90
    assert images[0].get('rotation', 0) == 0  # First image untouched

def test_rotate_image_invalid_angle(client, auth_headers):
    """Test validation for invalid rotation angles"""
    data = {'title': 'Invalid Angle Test', 'images': [{'url': 'u', 'public_id': 'p'}]}
    response = client.post('/api/items', json=data, headers=auth_headers)
    assert response.status_code == 201, f"Create item failed: {response.data}"
    item_id = response.json['id']

    # Try invalid angle
    response = client.patch(f'/api/items/{item_id}/rotate', json={
        'rotation': 45
    }, headers=auth_headers)
    
    assert response.status_code == 400
    assert 'Invalid rotation' in response.json['error']

def test_rotate_image_invalid_index(client, auth_headers):
    """Test validation for invalid image index"""
    data = {'title': 'Invalid Index Test', 'images': [{'url': 'u', 'public_id': 'p'}]}
    response = client.post('/api/items', json=data, headers=auth_headers)
    assert response.status_code == 201, f"Create item failed: {response.data}"
    item_id = response.json['id']

    # Try index out of bounds
    response = client.patch(f'/api/items/{item_id}/rotate', json={
        'image_index': 99,
        'rotation': 90
    }, headers=auth_headers)
    
    assert response.status_code == 400
    assert 'Invalid image index' in response.json['error']
