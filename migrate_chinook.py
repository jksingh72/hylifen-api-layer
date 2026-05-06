
import os
import subprocess

# Configuration
PG_USER = "postgres"
PG_PASS = "Kishuking2026$#"
SOURCE_DB = "chinook"
TARGET_DB = "sampledata"
TARGET_SCHEMA = "chinook"

# Set environment variable for password
os.environ["PGPASSWORD"] = PG_PASS

def run_command(cmd, input_text=None):
    process = subprocess.Popen(
        cmd,
        shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    stdout, stderr = process.communicate(input=input_text)
    if process.returncode != 0:
        print(f"Error executing: {cmd}")
        print(stderr)
        return None
    return stdout

print(f"Starting migration of {SOURCE_DB} to {TARGET_DB}.{TARGET_SCHEMA}...")

# 1. Create schema in target database
print(f"Creating schema {TARGET_SCHEMA} in {TARGET_DB}...")
run_command(f"psql -U {PG_USER} -d {TARGET_DB} -c \"CREATE SCHEMA IF NOT EXISTS {TARGET_SCHEMA}\"")

# 2. Dump source database (public schema only)
print(f"Dumping {SOURCE_DB}...")
# -n public: only public schema
# --no-owner: don't include ownership commands
# --no-privileges: don't include access control
dump_data = run_command(f"pg_dump -U {PG_USER} -d {SOURCE_DB} -n public --no-owner --no-privileges")

if dump_data:
    # 3. Replace 'public.' with 'chinook.'
    # We also need to handle cases where 'public' is referred to in search_path or create schema
    print(f"Remapping schema references...")
    modified_dump = dump_data.replace("public.", f"{TARGET_SCHEMA}.")
    # Handle 'SET search_path = public'
    modified_dump = modified_dump.replace("search_path = public", f"search_path = {TARGET_SCHEMA}")
    
    # 4. Restore into target database
    print(f"Restoring to {TARGET_DB}...")
    run_command(f"psql -U {PG_USER} -d {TARGET_DB}", input_text=modified_dump)
    print("Migration complete.")
else:
    print("Failed to dump data.")

