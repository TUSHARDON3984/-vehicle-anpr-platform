"""
routes/auth.py

Handles user registration, login, logout, and email verification.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer

from extensions import db, mail
from models import User

auth_bp = Blueprint("auth", __name__)


def get_serializer():
    from flask import current_app
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"])


def send_verification_email(user):
    serializer = get_serializer()
    token = serializer.dumps(user.email, salt="email-verification")
    verify_url = url_for("auth.verify_email", token=token, _external=True)

    msg = Message(
        subject="Verify your email - Vehicle Registry Platform",
        recipients=[user.email],
        body=(
            f"Hi {user.name},\n\n"
            f"Please verify your email by clicking the link below:\n{verify_url}\n\n"
            f"This link expires in 1 hour.\n\n"
            f"If you didn't create this account, you can ignore this email."
        ),
    )
    mail.send(msg)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not name or not email or not password:
            flash("All fields are required.", "danger")
            return redirect(url_for("auth.register"))

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("auth.register"))

        if User.query.filter_by(email=email).first():
            flash("An account with this email already exists.", "danger")
            return redirect(url_for("auth.register"))

        user = User(name=name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        try:
            send_verification_email(user)
            flash("Account created! Please check your email to verify your account.", "success")
        except Exception as e:
            flash(f"Account created, but verification email failed to send: {e}", "warning")

        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/verify-email/<token>")
def verify_email(token):
    serializer = get_serializer()
    try:
        email = serializer.loads(token, salt="email-verification", max_age=3600)
    except Exception:
        flash("The verification link is invalid or has expired.", "danger")
        return redirect(url_for("auth.login"))

    user = User.query.filter_by(email=email).first()
    if user is None:
        flash("User not found.", "danger")
        return redirect(url_for("auth.login"))

    user.is_verified = True
    db.session.commit()
    flash("Email verified successfully! You can now log in.", "success")
    return redirect(url_for("auth.login"))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()

        if user is None or not user.check_password(password):
            flash("Invalid email or password.", "danger")
            return redirect(url_for("auth.login"))

        if not user.is_verified:
            flash("Please verify your email before logging in.", "warning")
            return redirect(url_for("auth.login"))

        if user.has_face_setup:
            session["pending_user_id"] = user.id
            return redirect(url_for("face.verify"))

        login_user(user)
        return redirect(url_for("main.dashboard"))

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))