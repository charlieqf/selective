from app import create_app, db
from sqlalchemy import text
import sqlalchemy as sa

def clean_db():
    app = create_app()
    with app.app_context():
        print("Cleaning database for migration...")
        
        # 1. Drop answers first to remove FK dependencies on items
        db.session.execute(text("DROP TABLE IF EXISTS answers"))
        print("Dropped answers table.")

        # 2. Drop items and collections
        db.session.execute(text("DROP TABLE IF EXISTS items"))
        db.session.execute(text("DROP TABLE IF EXISTS collections"))
        print("Dropped items and collections.")

        # 3. Re-create answers table with question_id
        # We use raw SQL to avoid model definition conflicts
        db.session.execute(text("""
            CREATE TABLE answers (
                id INTEGER NOT NULL AUTO_INCREMENT,
                user_id INTEGER NOT NULL,
                question_id INTEGER,
                content TEXT,
                is_correct TINYINT,
                duration_seconds INTEGER,
                created_at DATETIME,
                PRIMARY KEY (id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """))
        print("Re-created answers table with question_id.")

        # 3. Clean up pending_uploads FKs
        # We want to drop the FKs so the index fk_1 can be dropped by migration
        inspector = sa.inspect(db.engine)
        fks = inspector.get_foreign_keys('pending_uploads')
        for fk in fks:
            print(f"Dropping FK {fk['name']} from pending_uploads...")
            db.session.execute(text(f"ALTER TABLE pending_uploads DROP FOREIGN KEY {fk['name']}"))
            
        # Drop index fk_1 explicitly
        try:
            db.session.execute(text("DROP INDEX fk_1 ON pending_uploads"))
            print("Dropped index fk_1 on pending_uploads.")
        except Exception as e:
            print(f"Could not drop index fk_1 (might not exist): {e}")
            
        # Strip questions constraints
        # The migration needs to drop index fk_1 on questions too
        try:
            db.session.execute(text("ALTER TABLE questions DROP FOREIGN KEY fk_2")) # Assuming fk_2 is the author FK
            print("Dropped FK fk_2 from questions.")
        except Exception as e:
             print(f"Could not drop FK fk_2 from questions: {e}")
             
        try:
            db.session.execute(text("DROP INDEX fk_1 ON questions"))
            print("Dropped index fk_1 on questions.")
        except Exception as e:
            print(f"Could not drop index fk_1 on questions: {e}")
        
        db.session.commit()
        print("Database ready for migration.")

if __name__ == '__main__':
    clean_db()
