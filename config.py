"""
config.py

Central configuration for the app. Reads sensitive values (mail credentials,
secret key) from environment variables via a .env file, so they never get
hardcoded or committed to Git.
"""

import os
from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Flask secret key -- used to sign session cookies and email tokens
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-this")

    # SQLite database -- a free, file-based database, no server needed
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "instance", "anpr.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Mail settings (using free Gmail SMTP as an example)
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")        # your Gmail address
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")        # Gmail "App Password" (not your normal password)
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_USERNAME")

    # Where uploaded plate images get saved
    UPLOAD_FOLDER = os.path.join(basedir, "static", "uploads")
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

    # Path to the Tesseract OCR executable (Windows default install location)
    # Update this if you installed Tesseract somewhere else.
    TESSERACT_CMD = os.environ.get(
        "TESSERACT_CMD", r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )