"""
extensions.py

Flask extension instances, created here (not in app.py) to avoid circular
imports between models.py, routes/, and app.py.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()

login_manager.login_view = "auth.login"
login_manager.login_message = "Please log in to access this page."