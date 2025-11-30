from app import create_app, db
from app.models.pending_upload import PendingUpload

def clean_legacy_uploads():
    app = create_app()
    with app.app_context():
        print("Cleaning legacy pending uploads...")
        # IDs identified in verification
        pids = [
            'selective-questions/dddmri8cesqzifqdfjky',
            'selective-questions/iktkzdjpalgl7xbuml1r'
        ]
        
        for pid in pids:
            pu = PendingUpload.query.get(pid)
            if pu:
                print(f"Deleting legacy pending upload: {pid}")
                db.session.delete(pu)
            else:
                print(f"Pending upload not found: {pid}")
                
        db.session.commit()
        print("Cleanup complete.")

if __name__ == '__main__':
    clean_legacy_uploads()
