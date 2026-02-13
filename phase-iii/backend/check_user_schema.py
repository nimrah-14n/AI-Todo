"""
Check the actual user table schema in the database.
"""
from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine, inspect
import os

# Connect to database
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

# Get inspector
inspector = inspect(engine)

# Check if user table exists
if 'user' in inspector.get_table_names():
    print("✓ User table exists")
    print("\nColumns in user table:")
    for column in inspector.get_columns('user'):
        print(f"  - {column['name']}: {column['type']} (nullable={column['nullable']})")

    print("\nPrimary keys:")
    pk = inspector.get_pk_constraint('user')
    print(f"  {pk}")

    print("\nForeign keys:")
    for fk in inspector.get_foreign_keys('user'):
        print(f"  {fk}")
else:
    print("✗ User table does not exist")
    print("\nAvailable tables:")
    for table in inspector.get_table_names():
        print(f"  - {table}")
