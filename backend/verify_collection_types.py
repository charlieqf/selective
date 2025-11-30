from app import create_app, db
from app.models.collection import Collection

def verify_collection_types():
    app = create_app()
    with app.app_context():
        collections = Collection.query.all()
        print(f"Total collections: {len(collections)}")
        
        type_counts = {}
        for c in collections:
            type_val = c.type if hasattr(c, 'type') else 'NO_TYPE_FIELD'
            type_counts[type_val] = type_counts.get(type_val, 0) + 1
        
        print("\nCollection types:")
        for type_val, count in type_counts.items():
            print(f"  {type_val}: {count}")
        
        print("\nSample collections:")
        for c in collections[:5]:
            print(f"  ID: {c.id}, User: {c.user_id}, Name: {c.name}, Type: {c.type}")

if __name__ == '__main__':
    verify_collection_types()
