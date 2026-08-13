import sqlalchemy
from sqlalchemy import create_engine, text

# Connect to the default 'postgres' database to list all other databases
db_url = "postgresql://postgres:Kishuking2026$#@localhost:5432/postgres"

try:
    engine = create_engine(db_url)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT datname FROM pg_database WHERE datistemplate = false;"))
        databases = [row[0] for row in result]
        print("Available databases:")
        for db in databases:
            print(f"- {db}")
except Exception as e:
    print(f"Error connecting to PostgreSQL: {e}")
