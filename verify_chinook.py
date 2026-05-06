
import os
import subprocess

PG_USER = "postgres"
PG_PASS = "Kishuking2026$#"
TARGET_DB = "sampledata"
os.environ["PGPASSWORD"] = PG_PASS

def run_query(query):
    process = subprocess.Popen(
        f"psql -U {PG_USER} -d {TARGET_DB} -t -c \"{query}\"",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    stdout, stderr = process.communicate()
    return stdout.strip()

print(f"Verifying chinook migration...")
album_count = run_query("SELECT count(*) FROM chinook.\"Album\"")
artist_count = run_query("SELECT count(*) FROM chinook.\"Artist\"")

print(f"Table 'Album' count: {album_count}")
print(f"Table 'Artist' count: {artist_count}")
