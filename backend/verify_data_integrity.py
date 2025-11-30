from app import create_app, db
from app.models.collection import Collection
from app.models.item import Item
from app.models.pending_upload import PendingUpload
from app.models.user import User

def verify_data():
    app = create_app()
    with app.app_context():
        with open('verification_results.txt', 'w') as f:
            def log(msg):
                print(msg)
                f.write(msg + '\n')

            log("=== Verifying Collections ===")
            # Check user 30001 (test_learner)
            user_id = 30001
            user = User.query.get(user_id)
            if user:
                log(f"User {user_id} ({user.username}) exists.")
                collections = Collection.query.filter_by(user_id=user_id).all()
                log(f"User {user_id} has {len(collections)} collections:")
                for c in collections:
                    log(f"  - ID: {c.id}, Name: {c.name}")
            else:
                log(f"User {user_id} not found.")

            # Check Collection ID 7
            c7 = Collection.query.get(7)
            if c7:
                log(f"Collection 7 exists: Name={c7.name}, UserID={c7.user_id}")
            else:
                log("Collection 7 NOT found.")

            log("\n=== Verifying Pending Uploads ===")
            # Check item 1
            item1 = Item.query.get(1)
            if item1:
                log(f"Item 1 exists. Images: {len(item1.get_images())}")
                for img in item1.get_images():
                    pid = img.get('public_id')
                    if pid:
                        pu = PendingUpload.query.get(pid)
                        if pu:
                            log(f"  [WARNING] PendingUpload exists for active image: {pid}")
                        else:
                            log(f"  [OK] PendingUpload deleted for image: {pid}")
            else:
                log("Item 1 not found.")

if __name__ == '__main__':
    verify_data()
