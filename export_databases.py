
import os
import subprocess
from datetime import datetime

# Configuration
PG_USER = "postgres"
PG_PASS = "Kishuking2026$#"
EXPORT_DIR = "db_exports"

DATABASES = [
    "chinook", 
    "companydb", 
    "dvdrental", 
    "employees", 
    "happiness_index", 
    "lego", 
    "netflix", 
    "pagila", 
    "periodic_table",
    "sampledata",
    "postgres"
]

# Set environment variable for password
os.environ["PGPASSWORD"] = PG_PASS

def export_db(db_name):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{db_name}_{timestamp}.sql"
    filepath = os.path.join(EXPORT_DIR, filename)
    
    print(f"Exporting {db_name} to {filepath}...")
    
    # Using -Fc for custom format (compressed and flexible for pg_restore)
    # Or plain text if preferred. Let's use plain text (.sql) for readability as requested.
    cmd = f"pg_dump -U {PG_USER} -d {db_name} -F p -f \"{filepath}\""
    
    process = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if process.returncode == 0:
        print(f"Successfully exported {db_name}.")
        return True
    else:
        print(f"Failed to export {db_name}: {process.stderr}")
        return False

if __name__ == "__main__":
    if not os.path.exists(EXPORT_DIR):
        os.makedirs(EXPORT_DIR)
        print(f"Created directory: {EXPORT_DIR}")
        
    success_count = 0
    for db in DATABASES:
        if export_db(db):
            success_count += 1
            
    print(f"\nExport process completed. {success_count}/{len(DATABASES)} databases exported.")
    print(f"Files are located in the '{EXPORT_DIR}' folder.")
