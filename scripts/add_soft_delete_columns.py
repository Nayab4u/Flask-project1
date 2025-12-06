from pathlib import Path
import sys
from sqlalchemy import text

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import create_app
from models import db

app = create_app()
with app.app_context():
    engine = db.get_engine()
    with engine.connect() as conn:
        cols = conn.execute(text("PRAGMA table_info(trips)")).fetchall()
        names = [r[1] for r in cols]
        if "deleted" not in names:
            conn.execute(text("ALTER TABLE trips ADD COLUMN deleted BOOLEAN DEFAULT 0"))
            print("Added column: trips.deleted")
        else:
            print("Column trips.deleted already exists")
        if "deleted_at" not in names:
            conn.execute(text("ALTER TABLE trips ADD COLUMN deleted_at DATETIME"))
            print("Added column: trips.deleted_at")
        else:
            print("Column trips.deleted_at already exists")