"""
Database Initialization Script for CloudDedup
Run this script to automatically create `clouddedup_db` and all 4 tables in MySQL.

Usage:
    python init_database.py
"""

import os
import pymysql
from dotenv import load_dotenv

load_dotenv(".env")

MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.environ.get("MYSQL_PORT", 3306))
MYSQL_USER = os.environ.get("MYSQL_USER", "root")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE", "clouddedup_db")

print(f"Connecting to MySQL on {MYSQL_HOST}:{MYSQL_PORT} as '{MYSQL_USER}'...")

try:
    # 1. Connect without selecting database to create the database if not exists
    conn = pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
    )
    with conn.cursor() as cur:
        cur.execute(f"CREATE DATABASE IF NOT EXISTS `{MYSQL_DATABASE}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        print(f"[OK] Database '{MYSQL_DATABASE}' created/verified successfully!")
    conn.close()

    # 2. Use Flask-SQLAlchemy application models to create all tables
    from app import create_app
    from app.extensions import db

    app = create_app("development")
    with app.app_context():
        db.create_all()
        print("[OK] All 4 tables created successfully in MySQL!")

    # 3. Verify created tables
    conn = pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE,
    )
    with conn.cursor() as cur:
        cur.execute("SHOW TABLES;")
        tables = [r[0] for r in cur.fetchall()]
        print(f"[OK] Verified tables in '{MYSQL_DATABASE}': {tables}")
    conn.close()

    print("\nSUCCESS: Database setup complete! You can now run: python app.py")

except Exception as e:
    print(f"\n[ERROR] Could not connect to MySQL: {e}")
    print("\nTroubleshooting steps:")
    print("1. Open XAMPP Control Panel.")
    print("2. Click 'Start' next to MySQL until it shows green PID and port 3306.")
    print("3. Then re-run: python init_database.py")
