from app import create_app, db
from sqlalchemy import text, inspect
import json

def serialize(obj):
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    return str(obj)

def inspect_full_schema():
    app = create_app()
    with app.app_context():
        inspector = inspect(db.engine)
        table_names = inspector.get_table_names()
        
        output = []
        
        for table in table_names:
            output.append(f"=== TABLE: {table} ===")
            
            # Columns
            columns = inspector.get_columns(table)
            output.append("  Columns:")
            for col in columns:
                output.append(f"    - {col['name']} ({col['type']}) Nullable: {col['nullable']}")
            
            # PK
            pk = inspector.get_pk_constraint(table)
            output.append(f"  Primary Key: {pk.get('constrained_columns', [])}")
            
            # FKs
            fks = inspector.get_foreign_keys(table)
            output.append("  Foreign Keys:")
            for fk in fks:
                output.append(f"    - {fk['name']}: {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
                
            # Indexes
            indexes = inspector.get_indexes(table)
            output.append("  Indexes:")
            for idx in indexes:
                output.append(f"    - {idx['name']}: {idx['column_names']} Unique: {idx['unique']}")
                
            # Sample Data
            output.append("  Sample Data (First 3 rows):")
            try:
                rows = db.session.execute(text(f"SELECT * FROM {table} LIMIT 3")).fetchall()
                if not rows:
                    output.append("    (No data)")
                else:
                    # Use _mapping to get dictionary-like access
                    row_keys = rows[0]._mapping.keys()
                    output.append(f"    Columns: {list(row_keys)}")
                    for row in rows:
                        # Convert row to dict using _mapping
                        row_dict = {k: serialize(row._mapping[k]) for k in row_keys}
                        output.append(f"    {row_dict}")
            except Exception as e:
                output.append(f"    (Error fetching data: {e})")
                
            output.append("\n")
            
        with open("db_schema_dump.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(output))
            
        print("Schema dump written to db_schema_dump.txt")

if __name__ == '__main__':
    inspect_full_schema()
