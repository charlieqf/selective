import pytest
import json
from app.models.item import Item

def test_rotate_first_image_success(client, auth_headers):
    """Test successful image rotation for the first image (index 0)"""
    # 1. Create an item with multiple images
    data = {
        'title': 'Rotation Index 0 Test',
        'subject': 'MATHS',
        'difficulty': 3,
        'images': [
            {'url': 'http://example.com/img1.jpg', 'public_id': 'pid_1'},
            {'url': 'http://example.com/img2.jpg', 'public_id': 'pid_2'}
        ]
    }
    response = client.post('/api/items', json=data, headers=auth_headers)
    assert response.status_code == 201
    item_id = response.json['id']

    # 2. Rotate the first image (index 0) to 90 degrees
    rotate_data = {
        'image_index': 0,
        'rotation': 90
    }
    response = client.patch(f'/api/items/{item_id}/rotate', json=rotate_data, headers=auth_headers)
    assert response.status_code == 200, f"Rotate failed: {response.data}"
    
    # Verify response
    assert response.json['rotation'] == 90
    assert response.json['image_index'] == 0

    # 3. Verify persistence
    response = client.get(f'/api/items/{item_id}', headers=auth_headers)
    images = response.json['images']
    assert images[0]['rotation'] == 90
    assert images[1].get('rotation', 0) == 0  # Second image untouched
