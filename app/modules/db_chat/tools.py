from langchain_core.tools import tool
from app.core.config import settings
from sqlalchemy import create_engine, text
import logging

logger = logging.getLogger(__name__)

# Base connection URL (without the database name)
# Splits at the last slash to get the server address
BASE_DB_URL = settings.DATABASE_URL.rsplit("/", 1)[0]
SYNC_BASE_URL = BASE_DB_URL.replace("postgresql+asyncpg://", "postgresql://")

def get_engine(db_name: str):
    return create_engine(f"{SYNC_BASE_URL}/{db_name}")

@tool
def server_list_databases() -> str:
    """
    SERVER LEVEL TOOL: Returns a list of all databases available on the PostgreSQL server.
    Use this as your first step to see what data is available.
    """
    try:
        # Use 'postgres' as the management database to list others
        engine = get_engine("postgres")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT datname FROM pg_database WHERE datistemplate = false;"))
            databases = [row[0] for row in result]
            return "Server Databases: " + ", ".join(databases)
    except Exception as e:
        return f"Error listing server databases: {e}"

@tool
def database_get_schema(database_name: str) -> str:
    """
    DATABASE LEVEL TOOL: Lists all tables and their column names in a specific database.
    Use this to understand the structure of a database before querying it.
    """
    try:
        engine = get_engine(database_name)
        with engine.connect() as conn:
            # Query to get schema, table, and column names, excluding system schemas
            query = """
                SELECT table_schema, table_name, column_name 
                FROM information_schema.columns 
                WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
                ORDER BY table_schema, table_name, ordinal_position
            """
            result = conn.execute(text(query))
            rows = result.fetchall()
            
            if not rows:
                return f"No user-defined tables found in database '{database_name}'."

            schema = {}
            for t_schema, table, column in rows:
                full_table_name = f"{t_schema}.{table}"
                if full_table_name not in schema:
                    schema[full_table_name] = []
                schema[full_table_name].append(column)
            
            output = [f"Schema for database '{database_name}':"]
            for table_path, cols in schema.items():
                output.append(f"- {table_path} ({', '.join(cols)})")
            return "\n".join(output)
    except Exception as e:
        return f"Error fetching schema for '{database_name}': {e}"

@tool
def database_run_query(database_name: str, sql_query: str) -> str:
    """
    QUERY TOOL: Executes a SQL SELECT query against a specific database.
    Ensure you have checked the schema first using database_get_schema.
    """
    try:
        engine = get_engine(database_name)
        with engine.connect() as conn:
            result = conn.execute(text(sql_query))
            if result.returns_rows:
                rows = result.fetchall()
                cols = result.keys()
                if not rows:
                    return f"Query in {database_name} returned 0 results."
                
                # Limit output to 20 rows to keep it concise
                output_rows = rows[:20]
                res_str = [f"Results from {database_name} (Showing {len(output_rows)}/{len(rows)}):"]
                res_str.append(" | ".join(cols))
                for row in output_rows:
                    res_str.append(" | ".join(map(str, row)))
                return "\n".join(res_str)
            else:
                conn.commit()
                return f"Success: Query executed in {database_name} (no rows returned)."
    except Exception as e:
        return f"SQL Error in '{database_name}': {e}"

def get_db_tools():
    """
    Returns the Server-Level and Database-Level tools.
    """
    return [server_list_databases, database_get_schema, database_run_query]
