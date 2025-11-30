
import pytest
from unittest.mock import patch, MagicMock
from app.models.user import User
from app.models.item import Item
from app.models.collection import Collection
from app import db
import migrate_collections

def test_migration_logic(app, client):
    """Test that migration creates collections and links items"""
    
    # 1. Setup Data
    with app.app_context():
        # Create user
        user = User(username='migration_test', email='mig@test.com')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        user_id = user.id
        
        # Create items with legacy subject but NO collection_id
        i1 = Item(title="Math Q", subject="MATHS", difficulty=1, author_id=user_id)
        i2 = Item(title="Read Q", subject="READING", difficulty=2, author_id=user_id)
        i3 = Item(title="Unknown Q", subject="UNKNOWN", difficulty=1, author_id=user_id)
        db.session.add_all([i1, i2, i3])
        db.session.commit()
        
        i1_id = i1.id
        i2_id = i2.id
        i3_id = i3.id
        
        # Verify initial state
        assert Collection.query.filter_by(user_id=user_id).count() == 0
        assert Item.query.get(i1_id).collection_id is None

    # 2. Run Migration (Mocking create_app to use our test app)
    with patch('migrate_collections.create_app') as mock_create_app:
        mock_create_app.return_value = app
        
        # Run migration
        migrate_collections.migrate_collections()
        
    # 3. Verify Results
    with app.app_context():
        # Check collections created
        collections = Collection.query.filter_by(user_id=user_id).all()
        assert len(collections) >= 4 # MATHS, READING, WRITING, THINKING_SKILLS
        
        c_math = Collection.query.filter_by(user_id=user_id, name='MATHS').first()
        assert c_math is not None
        assert c_math.type == 'SUBJECT'
        
        c_read = Collection.query.filter_by(user_id=user_id, name='READING').first()
        assert c_read is not None
        
        # Check items linked
        i1_updated = Item.query.get(i1_id)
        assert i1_updated.collection_id == c_math.id
        
        i2_updated = Item.query.get(i2_id)
        assert i2_updated.collection_id == c_read.id
        
        # Check unknown subject not linked
        i3_updated = Item.query.get(i3_id)
        assert i3_updated.collection_id is None
