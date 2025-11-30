"""
Seed script to create test data for E2E tests
Run this before running Playwright tests to ensure data exists
"""
from app import create_app, db
from app.models.user import User
from app.models.item import Item
from werkzeug.security import generate_password_hash

def seed_test_data():
    app = create_app()
    
    with app.app_context():
        # Check if testuser exists
        user = User.query.filter_by(username='testuser').first()
        
        if not user:
            print("Creating testuser...")
            user = User(
                username='testuser',
                email='test@example.com',
                password_hash=generate_password_hash('password'),
                role='student'
            )
            db.session.add(user)
            db.session.commit()
            print("✓ testuser created")
        else:
            print("✓ testuser already exists")
        
        # Create collections if they don't exist
        from app.models.collection import Collection
        
        subjects = ['MATHS', 'READING', 'WRITING', 'THINKING_SKILLS']
        collections = {}
        
        for subject_name in subjects:
            collection = Collection.query.filter_by(user_id=user.id, name=subject_name, is_deleted=False).first()
            if not collection:
                print(f"Creating collection {subject_name}...")
                collection = Collection(
                    user_id=user.id,
                    name=subject_name,
                    type='SUBJECT'
                )
                db.session.add(collection)
                db.session.flush() # Get ID
            collections[subject_name] = collection
            
        db.session.commit()
        print("✓ Collections ready")

        # Create some test items if they don't exist
        item_count = Item.query.filter_by(author_id=user.id).count()
        
        if item_count < 5:
            print(f"Creating test items (current: {item_count})...")
            
            for i in range(5 - item_count):
                subject_name = subjects[i % len(subjects)]
                item = Item(
                    author_id=user.id,
                    subject=subject_name, # Keep legacy field for now
                    collection_id=collections[subject_name].id,
                    difficulty=((i % 5) + 1),
                    title=f'Test Question {i + item_count + 1}',
                    content_text=f'This is test question content {i + item_count + 1}',
                    images=[]
                )
                db.session.add(item)
            
            db.session.commit()
            print(f"✓ Created {5 - item_count} test items")
        else:
            print(f"✓ Already have {item_count} test items")
        
        print("\n✅ Test data ready!")
        print(f"   User: testuser / password")
        print(f"   Items: {Item.query.filter_by(author_id=user.id).count()}")

if __name__ == '__main__':
    seed_test_data()
