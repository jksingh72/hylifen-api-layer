
import os
import subprocess

# Configuration
PG_USER = "postgres"
PG_PASS = "Kishuking2026$#"
KEEP_DATABASES = ["postgres", "sampledata", "template1", "postgres"] # Added template1 just in case, though template databases usually aren't returned by default queries

# Set environment variable for password
os.environ["PGPASSWORD"] = PG_PASS

def run_query(query):
    process = subprocess.Popen(
        f"psql -U {PG_USER} -t -c \"{query}\"",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding='utf-8'
    )
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        return None, stderr
    return stdout.strip(), None

def delete_db(db_name):
    print(f"Dropping database: {db_name}...")
    # Using WITH (FORCE) to close existing connections
    cmd = f"psql -U {PG_USER} -c \"DROP DATABASE IF EXISTS \\\"{db_name}\\\" WITH (FORCE);\""
    process = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if process.returncode == 0:
        print(f"Successfully dropped {db_name}.")
        return True
    else:
        print(f"Failed to drop {db_name}: {process.stderr}")
        return False

if __name__ == "__main__":
    # Get all databases
    query = "SELECT datname FROM pg_database WHERE datistemplate = false;"
    db_list_str, err = run_query(query)
    
    if err:
        print(f"Error fetching databases: {err}")
        exit(1)
        
    all_dbs = [db.strip() for db in db_list_str.split('\n') if db.strip()]
    
    dbs_to_delete = [db for db in all_dbs if db not in KEEP_DATABASES]
    
    if not dbs_to_delete:
        print("No databases to delete (other than the ones to keep).")
        exit(0)
        
    print(f"Found databases to delete: {', '.join(dbs_to_delete)}")
    print(f"Keeping: {', '.join(KEEP_DATABASES)}")
    
    # Final confirmation in logs
    confirm = input(f"Are you sure you want to delete these {len(dbs_to_delete)} databases? (yes/no): ")
    if confirm.lower() == 'yes':
        success_count = 0
        for db in dbs_to_delete:
            if delete_db(db):
                success_count += 1
        print(f"\nCleanup completed. {success_count}/{len(dbs_to_delete)} databases removed.")
    else:
        print("Operation cancelled.")
