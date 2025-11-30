from app import create_app, db
from sqlalchemy import text
import sqlalchemy as sa

def fix_db():
    app = create_app()
    with app.app_context():
        print("Cleaning up database state...")
        try:
            # Inspect and drop FKs on answers that point to items or questions
            inspector = sa.inspect(db.engine)
            fks = inspector.get_foreign_keys('answers')
            for fk in fks:
                if fk['referred_table'] in ['items', 'questions']:
                    print(f"Dropping FK {fk['name']} on answers...")
                    db.session.execute(text(f"ALTER TABLE answers DROP FOREIGN KEY {fk['name']}"))
            
            # Drop items and collections
            db.session.execute(text("DROP TABLE IF EXISTS items"))
            db.session.execute(text("DROP TABLE IF EXISTS collections"))
            
            # Inspect pending_uploads constraints
            result = db.session.execute(text("SELECT CONSTRAINT_NAME, REFERENCED_TABLE_NAME FROM information_schema.KEY_COLUMN_USAGE WHERE TABLE_NAME = 'pending_uploads' AND REFERENCED_TABLE_NAME IS NOT NULL"))
            print("Constraints on pending_uploads:")
            for row in result:
                print(f"{row[0]} -> {row[1]}")
                
            # Try to drop fk_1 index to see error
            try:
                db.session.execute(text("DROP INDEX fk_1 ON pending_uploads"))
                print("Dropped index fk_1 on pending_uploads.")
            except Exception as e:
                print(f"Could not drop index fk_1: {e}")

            # Inspect answers columns
            result = db.session.execute(text("SHOW COLUMNS FROM answers"))
            print("Columns in answers:")
            for row in result:
                print(row[0])

            try:
                db.session.execute(text("ALTER TABLE answers DROP COLUMN item_id"))
                print("Dropped item_id from answers.")
            except Exception as e:
                print(f"Could not drop item_id (might not exist): {e}")
                
            db.session.commit()
            print("Cleanup completed.")
        except Exception as e:
            print(f"Error during cleanup: {e}")
            db.session.rollback()

if __name__ == '__main__':
    fix_db()
