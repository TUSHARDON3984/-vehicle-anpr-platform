"""
models.py

Database models:
- User: registered platform users, with email verification status
- Vehicle: the vehicle registry -- plate number mapped to owner details
- ScanLog: audit trail of every plate scan performed
"""

from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    has_face_setup = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Vehicle(db.Model):
    __tablename__ = "vehicles"

    id = db.Column(db.Integer, primary_key=True)
    plate_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    owner_name = db.Column(db.String(120), nullable=False)
    owner_contact = db.Column(db.String(50))
    owner_address = db.Column(db.String(255))
    vehicle_model = db.Column(db.String(120))
    vehicle_color = db.Column(db.String(50))
    registered_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ScanLog(db.Model):
    """Every plate scan attempt gets logged here -- an audit trail."""
    __tablename__ = "scan_logs"

    id = db.Column(db.Integer, primary_key=True)
    scanned_plate_text = db.Column(db.String(20))
    matched = db.Column(db.Boolean, default=False)
    scanned_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)