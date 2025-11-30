import pytest
from app.models.item import Item
from app.models.pending_upload import PendingUpload
from app import db
from datetime import datetime

def test_pending_upload_deletion(client, auth_headers, app):
    with app.app_context():
        # 1. Create a pending upload
        public_id = "test_upload_123"
        pu = PendingUpload(public_id=public_id, user_id=1, created_at=datetime.utcnow())
        db.session.add(pu)
        db.session.commit()
        
        assert PendingUpload.query.get(public_id) is not None
        
        # 2. Create an item referencing this upload
        data = {
            "title": "Test Item with Image",
            "subject": "MATHS",
            "difficulty": 3,
            "content_text": "Test content",
            "images": [{"public_id": public_id, "url": "http://example.com/img.png"}]
        }
        
        # 3. Call API to create item
    response = client.post('/api/items', json=data, headers=auth_headers)
    assert response.status_code == 201
    
    with app.app_context():
        # 4. Verify pending upload is gone
        assert PendingUpload.query.get(public_id) is None
        
        # 5. Verify item has image
        item_id = response.json['id']
        item = Item.query.get(item_id)
        assert len(item.get_images()) == 1
        assert item.get_images()[0]['public_id'] == public_id
