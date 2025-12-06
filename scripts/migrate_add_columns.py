import sys
from pathlib import Path

# ensure project root is on sys.path so "import app" works no matter where this is run from
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import create_app
from models import db
from sqlalchemy import text

app = create_app()
with app.app_context():
    engine = db.get_engine()

    # users table columns
    with engine.connect() as conn:
        cols = conn.execute(text("PRAGMA table_info(users)")).fetchall()
        names = [r[1] for r in cols]
        if "is_admin" not in names:
            try:
                conn.execute(text("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0"))
                print("Added column: is_admin")
            except Exception as e:
                print("Could not add is_admin:", e)
        else:
            print("Column is_admin already present")

        if "created_at" not in names:
            try:
                conn.execute(text("ALTER TABLE users ADD COLUMN created_at DATETIME"))
                print("Added column: created_at")
            except Exception as e:
                print("Could not add created_at:", e)
        else:
            print("Column created_at already present")

    # trips table columns
    with engine.connect() as conn:
        cols = conn.execute(text("PRAGMA table_info(trips)")).fetchall()
        trip_names = [r[1] for r in cols]
        if "status" not in trip_names:
            try:
                conn.execute(text("ALTER TABLE trips ADD COLUMN status VARCHAR(30) DEFAULT 'draft'"))
                print("Added column: trips.status")
            except Exception as e:
                print("Could not add trips.status:", e)
        else:
            print("Column trips.status already present")

    # fallback: create missing tables (won't alter existing columns)
    try:
        db.create_all()
        print("db.create_all() finished (created any missing tables).")
    except Exception as e:
        print("db.create_all() failed:", e)