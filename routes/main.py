"""
routes/main.py

Core application routes (all require login): dashboard, plate scan,
vehicle registration, vehicle list, scan history.
"""

import os
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from extensions import db
from models import Vehicle, ScanLog
from anpr.plate_recognition_yolo import recognize_plate

main_bp = Blueprint("main", __name__)


def allowed_file(filename):
    return "." in filename and \
        filename.rsplit(".", 1)[1].lower() in current_app.config["ALLOWED_EXTENSIONS"]


@main_bp.route("/")
@login_required
def dashboard():
    total_vehicles = Vehicle.query.count()
    total_scans = ScanLog.query.count()
    recent_scans = ScanLog.query.order_by(ScanLog.timestamp.desc()).limit(5).all()
    return render_template(
        "dashboard.html",
        total_vehicles=total_vehicles,
        total_scans=total_scans,
        recent_scans=recent_scans,
    )


@main_bp.route("/scan", methods=["GET", "POST"])
@login_required
def scan_plate():
    if request.method == "POST":
        if "plate_image" not in request.files:
            flash("No file selected.", "danger")
            return redirect(url_for("main.scan_plate"))

        file = request.files["plate_image"]
        if file.filename == "":
            flash("No file selected.", "danger")
            return redirect(url_for("main.scan_plate"))

        if not allowed_file(file.filename):
            flash("Only .png, .jpg, .jpeg files are allowed.", "danger")
            return redirect(url_for("main.scan_plate"))

        filename = secure_filename(file.filename)
        timestamp_prefix = datetime.now().strftime("%Y%m%d_%H%M%S_")
        filename = timestamp_prefix + filename
        filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        plate_text, crop_path = recognize_plate(filepath)

        matched_vehicle = None
        if plate_text:
            matched_vehicle = Vehicle.query.filter_by(plate_number=plate_text).first()

        log = ScanLog(
            scanned_plate_text=plate_text or "UNREADABLE",
            matched=matched_vehicle is not None,
            scanned_by=current_user.id,
        )
        db.session.add(log)
        db.session.commit()

        return render_template(
            "scan_result.html",
            plate_text=plate_text,
            vehicle=matched_vehicle,
            original_image=filename,
        )

    return render_template("scan.html")


@main_bp.route("/vehicles")
@login_required
def vehicle_list():
    vehicles = Vehicle.query.order_by(Vehicle.created_at.desc()).all()
    return render_template("vehicles.html", vehicles=vehicles)


@main_bp.route("/vehicles/register", methods=["GET", "POST"])
@login_required
def register_vehicle():
    if request.method == "POST":
        plate_number = request.form.get("plate_number", "").strip().upper().replace(" ", "")
        owner_name = request.form.get("owner_name", "").strip()
        owner_contact = request.form.get("owner_contact", "").strip()
        owner_address = request.form.get("owner_address", "").strip()
        vehicle_model = request.form.get("vehicle_model", "").strip()
        vehicle_color = request.form.get("vehicle_color", "").strip()

        if not plate_number or not owner_name:
            flash("Plate number and owner name are required.", "danger")
            return redirect(url_for("main.register_vehicle"))

        if Vehicle.query.filter_by(plate_number=plate_number).first():
            flash("A vehicle with this plate number is already registered.", "danger")
            return redirect(url_for("main.register_vehicle"))

        vehicle = Vehicle(
            plate_number=plate_number,
            owner_name=owner_name,
            owner_contact=owner_contact,
            owner_address=owner_address,
            vehicle_model=vehicle_model,
            vehicle_color=vehicle_color,
            registered_by=current_user.id,
        )
        db.session.add(vehicle)
        db.session.commit()
        flash(f"Vehicle {plate_number} registered successfully.", "success")
        return redirect(url_for("main.vehicle_list"))

    return render_template("register_vehicle.html")


@main_bp.route("/scan-history")
@login_required
def scan_history():
    logs = ScanLog.query.order_by(ScanLog.timestamp.desc()).limit(100).all()
    return render_template("scan_history.html", logs=logs)