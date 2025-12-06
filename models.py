from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import os

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)   # <-- ensure this exists
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    trips = db.relationship("Trip", backref="user", lazy=True)

    def set_password(self, pw):
        self.password_hash = generate_password_hash(pw)

    def check_password(self, pw):
        return check_password_hash(self.password_hash or "", pw)


class Trip(db.Model):
    __tablename__ = "trips"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(150), nullable=True)
    destination = db.Column(db.String(150), nullable=False)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    travelers = db.Column(db.Integer, default=1)
    budget_preference = db.Column(db.String(20), default="medium")
    total_budget = db.Column(db.Float, default=0.0)
    summary = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(30), default="draft")
    deleted = db.Column(db.Boolean, default=False)           # <-- soft-delete flag
    deleted_at = db.Column(db.DateTime, nullable=True)       # <-- timestamp when deleted
    activities = db.relationship("Activity", backref="trip", cascade="all, delete-orphan", lazy=True)


class Activity(db.Model):
    __tablename__ = "activities"
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey("trips.id"), nullable=False)
    activity_name = db.Column(db.String(200), nullable=False)
    cost = db.Column(db.Float, default=0.0)
    category = db.Column(db.String(80), nullable=True)

# ensure local database folder exists (non-critical)
os.makedirs(os.path.join(os.path.dirname(__file__), "database"), exist_ok=True)