"""
app.py

Application entry point. Uses the Flask "application factory" pattern,
which keeps things organized and avoids circular imports.

Run with:
    python app.py
"""

import os
from flask import Flask

from config import Config
from extensions import db, login_manager, mail
from models import User


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ensure the instance/ and uploads/ folders exist
    os.makedirs(os.path.join(os.path.dirname(__file__), "instance"), exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from routes.auth import auth_bp
    from routes.main import main_bp
    from routes.face_auth import face_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(face_bp)

    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)