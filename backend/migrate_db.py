"""
migrate_db.py
Add new columns to the existing incidents table without dropping any data.
Safe to run multiple times (uses ALTER TABLE ... ADD COLUMN IF NOT EXISTS pattern).
"""
import sqlite3, os

DB_PATH = os.path.join(os.path.dirname(__file__), "sentinel.db")
conn = sqlite3.connect(DB_PATH)
cur  = conn.cursor()

# Fetch existing columns
cur.execute("PRAGMA table_info(incidents)")
existing = {row[1] for row in cur.fetchall()}
print("Existing columns:", existing)

new_cols = {
    "probable_root_cause": "TEXT",
    "causal_chain":        "TEXT",
    "confidence_score":    "REAL",
    "remediation_action":  "TEXT",
    "agent_outputs_json":  "TEXT",
}

for col, dtype in new_cols.items():
    if col not in existing:
        cur.execute(f"ALTER TABLE incidents ADD COLUMN {col} {dtype}")
        print(f"  Added column: {col}")
    else:
        print(f"  Already exists: {col}")

conn.commit()
conn.close()
print("Migration complete.")
