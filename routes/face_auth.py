"""
routes/face_auth.py

Routes for setting up Face ID and verifying it during login.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import login_required, current_user, login_user

from extensions import db
from models import User
from face_auth.recognizer import save_face_images, train_model, verify_face

face_bp = Blueprint("face", __name__)


@face_bp.route("/face/setup", methods=["GET", "POST"])
@login_required
def setup():
    if request.method == "POST":
        images = request.json.get("images", [])

        if len(images) < 3:
            return jsonify({"success": False, "message": "Please capture at least 3 photos."}), 400

        saved_count = save_face_images(current_user.id, images)

        if saved_count < 3:
            return jsonify({
                "success": False,
                "message": f"Only detected a face in {saved_count} photo(s). "
                           f"Make sure your face is clearly visible and well-lit, then try again."
            }), 400

        train_model()
        current_user.has_face_setup = True
        db.session.commit()

        return jsonify({"success": True, "message": "Face ID set up successfully!"})

    return render_template("face_setup.html")


@face_bp.route("/face/verify", methods=["GET", "POST"])
def verify():
    pending_user_id = session.get("pending_user_id")

    if not pending_user_id:
        flash("No pending login to verify.", "warning")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        image = request.json.get("image")

        if not image:
            return jsonify({"success": False, "message": "No image received."}), 400

        is_match, confidence, message = verify_face(image, pending_user_id)

        if is_match:
            user = User.query.get(pending_user_id)
            session.pop("pending_user_id", None)
            login_user(user)
            return jsonify({"success": True, "message": message, "redirect": url_for("main.dashboard")})
        else:
            return jsonify({"success": False, "message": message}), 401

    user = User.query.get(pending_user_id)
    return render_template("face_verify.html", user_name=user.name if user else "")


@face_bp.route("/face/cancel")
def cancel():
    session.pop("pending_user_id", None)
    flash("Login cancelled.", "info")
    return redirect(url_for("auth.login"))