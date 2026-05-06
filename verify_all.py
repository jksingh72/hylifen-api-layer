
import os
import subprocess

PG_USER = "postgres"
PG_PASS = "Kishuking2026$#"
TARGET_DB = "sampledata"
os.environ["PGPASSWORD"] = PG_PASS

SCHEMAS = [
    "chinook", "companydb", "dvdrental", "employees", "happiness_index", 
    "lego", "netflix", "pagila", "periodic_table", "titanic"
]

def run_query(query):
    process = subprocess.Popen(
        f"psql -U {PG_USER} -d {TARGET_DB} -t -c \"{query}\"",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding='utf-8'
    )
    stdout, stderr = process.communicate()
    return stdout.strip()

print(f"{'Schema':<18} | {'Tables':<8} | {'Status'}")
print("-" * 40)

for schema in SCHEMAS:
    # Count tables
    table_count = run_query(f"SELECT count(*) FROM pg_tables WHERE schemaname = '{schema}'")
    
    if table_count and int(table_count) > 0:
        # Check data in the first table found
        first_table = run_query(f"SELECT tablename FROM pg_tables WHERE schemaname = '{schema}' LIMIT 1")
        row_count = run_query(f"SELECT count(*) FROM {schema}.\"{first_table}\"")
        status = f"OK ({row_count} rows in {first_table})"
    else:
        status = "EMPTY OR MISSING"
        
    print(f"{schema:<18} | {table_count:<8} | {status}")
