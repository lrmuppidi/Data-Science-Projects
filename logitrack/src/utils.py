import os
import sqlite3

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace("\\", "/")

RAW_DIR = ROOT + "/data/raw/"
CLEAN_DIR = ROOT + "/data/cleaned/"
REPORT_DIR = ROOT + "/reports/"
SCHEMA_FILE = ROOT + "/sql/schema.sql"
QUERIES_FILE = ROOT + "/sql/analysis_queries.sql"
DB_FILE = ROOT + "/logitrack.db"


def get_connection():
    """Open the SQLite database (the file is created if it does not exist)."""
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON")  
    return conn
