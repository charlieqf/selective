from app import create_app, db
from app.models.item import Item
import json

app = create_app()
with app.app_context():
    items = Item.query.all()
    print(f"Total items: {len(items)}")
    for item in items:
        if item.images:
            has_string = any(not isinstance(img, dict) for img in item.images)
            missing_public_id = any(isinstance(img, dict) and 'public_id' not in img for img in item.images)
            if has_string or missing_public_id:
                print(f"Item {item.id} has issues: images={item.images}")
            else:
                # Print a few healthy ones for reference
                if item.id < 5:
                    print(f"Item {item.id} looks OK: images={item.images}")
