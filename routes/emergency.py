"""
routes/emergency.py — Feature 4: Smart Emergency Alert System
"""

from flask import Blueprint, render_template, request, jsonify
from models.patient import Patient
from models.health_record import HealthRecord
from models.alert import Alert
from services.extended_agent_service import ExtendedAgentService
from services.agent_service import AgentService
from utils.formatters import format_health_summary
from config import AGENT_INSTRUCTIONS
from app_factory import db
from datetime import datetime

emergency_bp = Blueprint("emergency", __name__)

# Emergency thresholds — override from AGENT_INSTRUCTIONS
EMERGENCY_THRESHOLDS = {
    "systolic_bp":         {"critical": 180, "warning": 160, "label": "Blood Pressure (Systolic)"},
    "diastolic_bp":        {"critical": 120, "warning": 100, "label": "Blood Pressure (Diastolic)"},
    "blood_glucose_high":  {"critical": 300, "warning": 250, "label": "Blood Glucose (High)"},
    "blood_glucose_low":   {"critical": 60,  "warning": 70,  "label": "Blood Glucose (Low)", "direction": "low"},
    "heart_rate_high":     {"critical": 130, "warning": 110, "label": "Heart Rate (High)"},
    "heart_rate_low":      {"critical": 40,  "warning": 50,  "label": "Heart Rate (Low)", "direction": "low"},
    "oxygen_saturation":   {"critical": 90,  "warning": 94,  "label": "Oxygen Saturation", "direction": "low"},
    "body_temperature":    {"critical": 39.5,"warning": 38.5, "label": "Body Temperature"},
}

SEVERITY_CONFIG = {
    "Critical":  {"color": "danger",  "badge": "bg-danger",  "icon": "bi-x-octagon-fill",      "label": "CRITICAL"},
    "Emergency": {"color": "danger",  "badge": "bg-danger",  "icon": "bi-heart-pulse-fill",     "label": "EMERGENCY"},
    "Warning":   {"color": "warning", "badge": "bg-warning text-dark", "icon": "bi-exclamation-triangle-fill", "label": "WARNING"},
    "Info":      {"color": "info",    "badge": "bg-info",    "icon": "bi-info-circle-fill",     "label": "INFO"},
}


def _detect_emergency_alerts(patient_id: int, record: dict) -> list:
    """Detect emergency-level conditions from a health record."""
    alerts = []
    thresh = AGENT_INSTRUCTIONS.get("alert_thresholds", {})

    checks = [
        ("systolic_bp",       record.get("systolic_bp"),       180, 160, "Blood Pressure Systolic",     "mmHg"),
        ("diastolic_bp",      record.get("diastolic_bp"),      120, 100, "Blood Pressure Diastolic",    "mmHg"),
        ("blood_glucose",     record.get("blood_glucose"),     300, 250, "Blood Glucose (High)",        "mg/dL"),
        ("heart_rate_high",   record.get("heart_rate"),        130, 110, "Heart Rate (High)",           "bpm"),
        ("body_temperature",  record.get("body_temperature"),  39.5, 38.5, "Body Temperature",          "°C"),
    ]
    for key, val, crit_thresh, warn_thresh, label, unit in checks:
        if val is None:
            continue
        val = float(val)
        if val >= crit_thresh:
            alerts.append({"metric": label, "value": f"{val} {unit}", "severity": "Critical"})
        elif val >= warn_thresh:
            alerts.append({"metric": label, "value": f"{val} {unit}", "severity": "Warning"})

    # Low value checks
    glucose = record.get("blood_glucose")
    if glucose is not None and float(glucose) < 60:
        alerts.append({"metric": "Blood Glucose (Low)", "value": f"{glucose} mg/dL", "severity": "Critical"})
    elif glucose is not None and float(glucose) < 70:
        alerts.append({"metric": "Blood Glucose (Low)", "value": f"{glucose} mg/dL", "severity": "Warning"})

    hr = record.get("heart_rate")
    if hr is not None and float(hr) < 40:
        alerts.append({"metric": "Heart Rate (Low)", "value": f"{hr} bpm", "severity": "Critical"})
    elif hr is not None and float(hr) < 50:
        alerts.append({"metric": "Heart Rate (Low)", "value": f"{hr} bpm", "severity": "Warning"})

    o2 = record.get("oxygen_saturation")
    if o2 is not None and float(o2) < 90:
        alerts.append({"metric": "Oxygen Saturation", "value": f"{o2}%", "severity": "Emergency"})
    elif o2 is not None and float(o2) < 94:
        alerts.append({"metric": "Oxygen Saturation", "value": f"{o2}%", "severity": "Warning"})

    return alerts


@emergency_bp.route("/<int:patient_id>")
def emergency_dashboard(patient_id: int):
    """Emergency Alert Dashboard."""
    patient = Patient.query.get_or_404(patient_id)
    all_patients = Patient.query.filter_by(is_active=True).all()

    # Active (unresolved) alerts
    active_alerts = (
        Alert.query.filter_by(patient_id=patient_id, is_resolved=False)
        .order_by(Alert.created_at.desc())
        .all()
    )

    # Latest record emergency check
    latest = (
        HealthRecord.query.filter_by(patient_id=patient_id)
        .order_by(HealthRecord.recorded_at.desc())
        .first()
    )
    live_checks = []
    if latest:
        live_checks = _detect_emergency_alerts(patient_id, latest.to_dict())

    # Categorise active alerts by severity
    severity_counts = {"Critical": 0, "Emergency": 0, "Warning": 0, "Info": 0}
    for a in active_alerts:
        if a.severity in severity_counts:
            severity_counts[a.severity] += 1

    return render_template(
        "features/emergency.html",
        patient=patient,
        all_patients=all_patients,
        active_alerts=active_alerts,
        live_checks=live_checks,
        severity_counts=severity_counts,
        severity_config=SEVERITY_CONFIG,
        latest=latest,
        active_page="emergency",
    )


@emergency_bp.route("/api/<int:patient_id>/analyze", methods=["POST"])
def analyze_alert(patient_id: int):
    """AJAX: get AI explanation for a specific emergency alert."""
    patient = Patient.query.get_or_404(patient_id)
    data = request.json or {}
    alert_data = {
        "metric":   data.get("metric", "vital sign"),
        "value":    data.get("value", "N/A"),
        "severity": data.get("severity", "Warning"),
    }
    result = ExtendedAgentService.analyze_emergency(patient.to_dict(), alert_data)
    result["explanation_html"] = format_health_summary(result.get("explanation", ""))
    return jsonify(result)


@emergency_bp.route("/api/<int:patient_id>/check", methods=["GET"])
def check_latest(patient_id: int):
    """AJAX: check latest record for emergency conditions."""
    latest = (
        HealthRecord.query.filter_by(patient_id=patient_id)
        .order_by(HealthRecord.recorded_at.desc()).first()
    )
    if not latest:
        return jsonify({"alerts": [], "status": "no_data"})
    checks = _detect_emergency_alerts(patient_id, latest.to_dict())
    return jsonify({"alerts": checks, "status": "ok"})


@emergency_bp.route("/api/<int:patient_id>/resolve/<int:alert_id>", methods=["POST"])
def resolve(patient_id: int, alert_id: int):
    alert = Alert.query.get_or_404(alert_id)
    alert.is_resolved = True
    alert.resolved_at = datetime.utcnow()
    db.session.commit()
    return jsonify({"status": "ok"})
