"""
Interactive Database Catalog Viewer for CloudDedup
Inspects all SQL tables and records directly in the terminal (supports MySQL and SQLite).

Usage:
    python view_db.py
"""

import os
import sqlite3
import pymysql
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

USE_SQLITE = os.environ.get("USE_SQLITE", "1") == "1"
DB_FILE = BASE_DIR / "instance" / "clouddedup.db"

MYSQL_HOST = os.environ.get("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = int(os.environ.get("MYSQL_PORT", 3306))
MYSQL_USER = os.environ.get("MYSQL_USER", "root")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE", "clouddedup_db")


def format_bytes(size):
    if size is None:
        size = 0
    size = float(size)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:,.1f} {unit}" if unit != 'B' else f"{size} B"
        size /= 1024.0
    return f"{size:,.1f} TB"


def print_table(title, rows, headers):
    print(f"\n{'=' * 85}")
    print(f" {title.upper()} ({len(rows)} records)")
    print(f"{'=' * 85}")
    if not rows:
        print("  (Table is currently empty)")
        return

    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, val in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(val) if val is not None else "NULL"))

    col_widths = [min(w, 40) for w in col_widths]
    header_str = " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    sep_str = "-+-".join("-" * col_widths[i] for i in range(len(headers)))
    print(header_str)
    print(sep_str)
    for row in rows:
        vals = []
        for i, val in enumerate(row):
            s = str(val) if val is not None else "NULL"
            if len(s) > 40:
                s = s[:37] + "..."
            vals.append(s.ljust(col_widths[i]))
        print(" | ".join(vals))


def main():
    if USE_SQLITE:
        if not DB_FILE.exists():
            print(f"[!] Database file not found at: {DB_FILE}")
            return
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        engine_label = f"Local SQLite ({DB_FILE.name})"
    else:
        try:
            conn = pymysql.connect(
                host=MYSQL_HOST,
                port=MYSQL_PORT,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                database=MYSQL_DATABASE,
                charset="utf8mb4"
            )
            cur = conn.cursor()
            engine_label = f"MySQL Server ({MYSQL_USER}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE})"
        except Exception as e:
            print(f"[!] Failed to connect to MySQL: {e}")
            return

    print("\n" + "#" * 85)
    print(f"  CLOUDDEDUP DATABASE INSPECTOR  --  Engine: {engine_label}")
    print("#" * 85)

    # 1. users Table
    cur.execute("SELECT id, name, email, firebase_uid, created_at FROM users ORDER BY id ASC;")
    users = cur.fetchall()
    print_table("1. Table: users", users, ["ID", "Name", "Email", "Firebase UID", "Created At"])

    # 2. stored_files Table
    cur.execute("SELECT id, sha256_hash, file_size, reference_count, storage_path, created_at FROM stored_files ORDER BY id ASC;")
    stored = cur.fetchall()
    stored_formatted = [
        (r[0], (str(r[1])[:16] + "..." if r[1] else ""), format_bytes(r[2]), r[3], r[4], r[5]) for r in stored
    ]
    print_table("2. Table: stored_files (Unique Physical Objects in Cloud)", stored_formatted, ["ID", "SHA-256 Hash", "Size", "Refs", "Storage Path", "Created At"])

    # 3. file_references Table
    cur.execute("""
        SELECT f.id, u.name, f.display_name, f.stored_file_id, 
               CASE WHEN f.is_duplicate = 1 THEN 'DUPLICATE' ELSE 'ORIGINAL' END,
               f.uploaded_at
        FROM file_references f
        LEFT JOIN users u ON f.user_id = u.id
        ORDER BY f.id ASC;
    """)
    file_refs = cur.fetchall()
    print_table("3. Table: file_references (User File Catalog)", file_refs, ["ID", "User", "Filename", "Stored ID", "Status", "Uploaded At"])

    # 4. upload_events Table
    cur.execute("""
        SELECT id, event_type, original_filename, file_size, sha256_hash, created_at
        FROM upload_events
        ORDER BY id DESC
        LIMIT 10;
    """)
    events = cur.fetchall()
    events_formatted = [
        (r[0], r[1], r[2], format_bytes(r[3]), (str(r[4])[:12] + "..." if r[4] else ""), r[5]) for r in events
    ]
    print_table("4. Table: upload_events (Recent Audit Log - Last 10)", events_formatted, ["ID", "Event Type", "Filename", "Size", "Hash", "Timestamp"])

    # Storage Statistics Calculation
    cur.execute("SELECT SUM(file_size) FROM stored_files;")
    row = cur.fetchone()
    physical_bytes = row[0] if (row and row[0] is not None) else 0

    cur.execute("""
        SELECT SUM(s.file_size) 
        FROM file_references f 
        JOIN stored_files s ON f.stored_file_id = s.id;
    """)
    row = cur.fetchone()
    logical_bytes = row[0] if (row and row[0] is not None) else 0

    saved_bytes = max(0, logical_bytes - physical_bytes)
    ratio = ((saved_bytes / logical_bytes) * 100) if logical_bytes > 0 else 0

    print("\n" + "=" * 85)
    print(" DEDUPLICATION METRICS SUMMARY")
    print("=" * 85)
    print(f" Logical Storage (Uploaded by Users): {format_bytes(logical_bytes)} ({logical_bytes:,} bytes)")
    print(f" Physical Storage (Actually Stored): {format_bytes(physical_bytes)} ({physical_bytes:,} bytes)")
    print(f" Space & Bandwidth Saved:           {format_bytes(saved_bytes)} ({saved_bytes:,} bytes)")
    print(f" Deduplication Efficiency:          {ratio:.2f}% Reduction")
    print("=" * 85 + "\n")

    conn.close()


if __name__ == "__main__":
    main()
