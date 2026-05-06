
import os
import subprocess

# Configuration
PG_USER = "postgres"
PG_PASS = "Kishuking2026$#"
TARGET_DB = "sampledata"

DATABASES = [
    "lego", "netflix", "titanic"
]

# Set environment variable for password
os.environ["PGPASSWORD"] = PG_PASS

def run_command(cmd, input_text=None):
    process = subprocess.Popen(
        cmd,
        shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding='utf-8'
    )
    stdout, stderr = process.communicate(input=input_text)
    if process.returncode != 0:
        return None, stderr
    return stdout, None

def migrate_db(db_name):
    print(f"\n>>> Migrating {db_name} to {TARGET_DB}.{db_name}...")
    
    # 1. Create schema
    run_command(f"psql -U {PG_USER} -d {TARGET_DB} -c \"CREATE SCHEMA IF NOT EXISTS {db_name}\"")
    
    # 2. Dump
    dump_data, err = run_command(f"pg_dump -U {PG_USER} -d {db_name} -n public --no-owner --no-privileges")
    
    if dump_data:
        # 3. Remap
        modified_dump = dump_data.replace("public.", f"{db_name}.")
        modified_dump = modified_dump.replace("search_path = public", f"search_path = {db_name}")
        
        # 4. Restore
        _, err = run_command(f"psql -U {PG_USER} -d {TARGET_DB}", input_text=modified_dump)
        if err:
            print(f"Restore error for {db_name}: {err}")
        else:
            print(f"Successfully migrated {db_name}.")
    else:
        print(f"Failed to dump {db_name}: {err}")

if __name__ == "__main__":
    for db in DATABASES:
        migrate_db(db)
    print("\nAll migrations completed.")
