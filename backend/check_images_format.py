import os
import sys

# Add backend to path so we can import app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.item import Item
import json

# Force find the db file
backend_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(backend_dir, 'instance', 'selective.db')
if not os.path.exists(db_path):
    db_path = os.path.join(backend_dir, 'selective.db')

print(f"Using DB at: {db_path}")

app = create_app()
# Override DB URI to be absolute
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"

with app.app_context():
    items = Item.query.all()
    print(f"Total items: {len(items)}")
    for item in items:
        if item.images:
            images = item.images
            if isinstance(images, str):
                images = json.loads(images)
            
            for i, img in enumerate(images):
                if isinstance(img, dict):
                    if 'public_id' not in img:
                        print(f"Item {item.id} - Image {i} missing public_id: {img}")
                    else:
                        if i < 2: # Just for debug
                             print(f"Item {item.id} - Image {i} OK (has public_id)")
                else:
                    print(f"Item {item.id} - Image {i} is not a dict: {type(img)} - {img}")
