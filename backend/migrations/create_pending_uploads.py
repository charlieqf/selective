"""
Database migration for PendingUpload model

Run this script to create the pending_uploads table:
$ flask db upgrade

Or manually create the table with:
"""

create_pending_uploads_table = """
CREATE TABLE IF NOT EXISTS pending_uploads (
    public_id VARCHAR(255) PRIMARY KEY,
    user_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_pending_uploads_created_at ON pending_uploads(created_at);
CREATE INDEX IF NOT EXISTS idx_pending_uploads_user_id ON pending_uploads(user_id);
"""

print("To create the pending_uploads table, run:")
print("1. flask db migrate -m 'Add pending_uploads table'")
print("2. flask db upgrade")
print("\nOr execute this SQL manually:")
print(create_pending_uploads_table)
