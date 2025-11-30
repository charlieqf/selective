from app import create_app, db
from app.models.user import User
from app.models.collection import Collection
from app.models.item import Item
from config import Config

def migrate_collections():
    app = create_app()
    with app.app_context():
        print("Starting data migration...")
        
        users = User.query.all()
        print(f"Found {len(users)} users.")
        
        for user in users:
            print(f"Processing user: {user.username}")
            
            # 1. Create default collections if not exist
            collection_map = {} # name -> collection_id
            
            for subject_key, subject_info in Config.SUBJECTS.items():
                name = subject_info['name']
                
                # Check if exists (active)
                collection = Collection.query.filter_by(
                    user_id=user.id, 
                    name=name, 
                    is_deleted=False
                ).first()
                
                if not collection:
                    print(f"  Creating collection: {name}")
                    collection = Collection(
                        user_id=user.id,
                        name=name,
                        type='SUBJECT',
                        icon=subject_info['icon'],
                        color=subject_info['color']
                    )
                    db.session.add(collection)
                    db.session.flush() # Get ID
                else:
                    print(f"  Collection exists: {name}")
                    
                collection_map[name] = collection.id
            
            # 2. Migrate items
            items = Item.query.filter_by(author_id=user.id).all()
            print(f"  Found {len(items)} items.")
            
            updated_count = 0
            for item in items:
                if not item.collection_id and item.subject:
                    # Map subject to collection
                    # Note: item.subject might be 'MATHS' or 'Maths' depending on how it was stored.
                    # Config keys are uppercase 'MATHS', names are 'MATHS'.
                    # Let's try exact match first, then uppercase.
                    
                    target_collection_id = collection_map.get(item.subject)
                    if not target_collection_id:
                        target_collection_id = collection_map.get(item.subject.upper())
                        
                    if target_collection_id:
                        item.collection_id = target_collection_id
                        updated_count += 1
                    else:
                        print(f"  Warning: Could not map item {item.id} subject '{item.subject}' to collection.")
            
            print(f"  Updated {updated_count} items.")
            db.session.commit()
            
        print("Data migration completed.")

if __name__ == '__main__':
    migrate_collections()
