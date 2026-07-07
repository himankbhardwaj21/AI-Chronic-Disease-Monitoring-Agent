"""
routes/health_data.py — Health record input and history
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app_factory import db
from models.patient import Patient
from models.health_record import HealthRecord
from models.alert import Alert
from services.health_service import HealthService
from utils.validators import validate_vitals

health_data_bp = Blueprint("health_data", __name__)


@health_data_bp.route("/input/<int:patient_id>", methods=["GET", "POST"])
def input_data(patient_id: int):
    """Health data input form."""
    patient = Patient.query.get_or_404(patient_id)
    all_patients = Patient.query.filter_by(is_active=True).all()

    if request.method == "POST":
        data = request.form.to_dict()
        errors = validate_vitals(data)
        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("health_data/input.html",
                                   patient=patient, all_patients=all_patients,
                                   active_page="health")

        result = HealthService.save_health_record(patient_id, data)

        # Auto-generate timeline events from this health record
        try:
            from models.health_record import HealthRecord
            from services.timeline_service import TimelineService
            new_record = HealthRecord.query.get(result["record_id"])
            prev_record = (
                HealthRecord.query
                .filter_by(patient_id=patient_id)
                .filter(HealthRecord.id != result["record_id"])
                .order_by(HealthRecord.recorded_at.desc())
                .first()
            )
            if new_record:
                TimelineService.generate_from_health_record(patient_id, new_record, prev_record)
        except Exception:
            pass  # Timeline is non-critical

        flash(
            f"Health data saved! Health Score: {result['health_score']}/100 | Risk: {result['risk_level']}",
            "success",
        )
        return redirect(url_for("dashboard.dashboard", patient_id=patient_id))

    return render_template(
        "health_data/input.html",
        patient=patient,
        all_patients=all_patients,
        active_page="health",
    )


@health_data_bp.route("/history/<int:patient_id>")
def history(patient_id: int):
    """View health record history."""
    patient = Patient.query.get_or_404(patient_id)
    all_patients = Patient.query.filter_by(is_active=True).all()
    page = request.args.get("page", 1, type=int)
    records = (
        HealthRecord.query
        .filter_by(patient_id=patient_id)
        .order_by(HealthRecord.recorded_at.desc())
        .paginate(page=page, per_page=15, error_out=False)
    )
    return render_template(
        "health_data/history.html",
        patient=patient,
        all_patients=all_patients,
        records=records,
        active_page="health",
    )


@health_data_bp.route("/record/<int:record_id>/delete", methods=["POST"])
def delete_record(record_id: int):
    """Delete a health record."""
    record = HealthRecord.query.get_or_404(record_id)
    patient_id = record.patient_id
    db.session.delete(record)
    db.session.commit()
    flash("Health record deleted.", "info")
    return redirect(url_for("health_data.history", patient_id=patient_id))


@health_data_bp.route("/api/chart/<int:patient_id>")
def chart_data_api(patient_id: int):
    """AJAX endpoint for chart data."""
    days = request.args.get("days", 14, type=int)
    data = HealthService.get_chart_data(patient_id, days=days)
    return jsonify(data)


@health_data_bp.route("/api/stats/<int:patient_id>")
def stats_api(patient_id: int):
    """AJAX endpoint for summary stats."""
    days = request.args.get("days", 7, type=int)
    data = HealthService.get_summary_stats(patient_id, days=days)
    return jsonify(data)
