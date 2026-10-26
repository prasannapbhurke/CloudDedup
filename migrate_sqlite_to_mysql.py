"""
Data Migration Script: SQLite -> MySQL (clouddedup_db)
Transfers all users, stored_files, file_references, and upload_events
from instance/clouddedup.db into the MySQL database.
"""
import os
import sqlite3
import pymysql
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SQLITE_DB = BASE_DIR / "instance" / "clouddedup.db"

MYSQL_HOST = os.environ.get("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = int(os.environ.get("MYSQL_PORT", 3306))
MYSQL_USER = os.environ.get("MYSQL_USER", "root")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE", "clouddedup_db")

def migrate():
    if not SQLITE_DB.exists():
        print(f"No SQLite database found at {SQLITE_DB}. Nothing to migrate.")
        return

    print(f"Connecting to SQLite: {SQLITE_DB}")
    conn_sq = sqlite3.connect(SQLITE_DB)
    conn_sq.row_factory = sqlite3.Row
    cur_sq = conn_sq.cursor()

    print(f"Connecting to MySQL: {MYSQL_USER}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}")
    conn_my = pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE,
        autocommit=False,
        charset="utf8mb4"
    )
    cur_my = conn_my.cursor()

    try:
        # Disable foreign key checks during migration
        cur_my.execute("SET FOREIGN_KEY_CHECKS = 0;")

        # 1. Users
        users = cur_sq.execute("SELECT * FROM users").fetchall()
        print(f"Migrating {len(users)} users...")
        for u in users:
            cur_my.execute("""
                INSERT INTO users (id, firebase_uid, name, email, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    name = VALUES(name),
                    email = VALUES(email),
                    updated_at = VALUES(updated_at)
            """, (u["id"], u["firebase_uid"], u["name"], u["email"], u["created_at"], u["updated_at"]))

        # 2. Stored Files
        stored_files = cur_sq.execute("SELECT * FROM stored_files").fetchall()
        print(f"Migrating {len(stored_files)} stored_files...")
        for sf in stored_files:
            cur_my.execute("""
                INSERT INTO stored_files (id, sha256_hash, file_size, storage_path, mime_type, reference_count, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    reference_count = VALUES(reference_count),
                    storage_path = VALUES(storage_path)
            """, (sf["id"], sf["sha256_hash"], sf["file_size"], sf["storage_path"], sf["mime_type"], sf["reference_count"], sf["created_at"]))

        # 3. File References
        file_refs = cur_sq.execute("SELECT * FROM file_references").fetchall()
        print(f"Migrating {len(file_refs)} file_references...")
        for fr in file_refs:
            cur_my.execute("""
                INSERT INTO file_references (id, user_id, stored_file_id, display_name, uploaded_at, is_duplicate)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    display_name = VALUES(display_name),
                    is_duplicate = VALUES(is_duplicate)
            """, (fr["id"], fr["user_id"], fr["stored_file_id"], fr["display_name"], fr["uploaded_at"], bool(fr["is_duplicate"])))

        # 4. Upload Events
        events = cur_sq.execute("SELECT * FROM upload_events").fetchall()
        print(f"Migrating {len(events)} upload_events...")
        for ev in events:
            cur_my.execute("""
                INSERT INTO upload_events (id, user_id, stored_file_id, original_filename, file_size, sha256_hash, event_type, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    original_filename = VALUES(original_filename),
                    file_size = VALUES(file_size)
            """, (ev["id"], ev["user_id"], ev["stored_file_id"], ev["original_filename"], ev["file_size"], ev["sha256_hash"], ev["event_type"], ev["created_at"]))

        cur_my.execute("SET FOREIGN_KEY_CHECKS = 1;")
        conn_my.commit()
        print("Data migration to MySQL completed and committed successfully!")

    except Exception as e:
        conn_my.rollback()
        print("Error during migration, rolled back:", e)
        raise e
    finally:
        cur_my.close()
        conn_my.close()
        cur_sq.close()
        conn_sq.close()

if __name__ == "__main__":
    migrate()
