"""
routes/dashboard.py — Main dashboard route
"""

from flask import Blueprint, render_template, redirect, url_for, jsonify
from models.patient import Patient
from models.health_record import HealthRecord
from models.alert import Alert
from models.medication import Medication
from services.health_service import HealthService
from services.agent_service import AgentService
from services.watsonx_service import WatsonxService
from utils.helpers import get_risk_color, get_severity_icon
import json

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
def index():
    """Root redirect to dashboard."""
    patients = Patient.query.filter_by(is_active=True).all()
    if not patients:
        return redirect(url_for("patients.create"))
    return redirect(url_for("dashboard.dashboard", patient_id=patients[0].id))


@dashboard_bp.route("/dashboard/<int:patient_id>")
def dashboard(patient_id: int):
    """Main dashboard view with all health metrics."""
    patient = Patient.query.get_or_404(patient_id)
    all_patients = Patient.query.filter_by(is_active=True).all()

    # Latest record
    latest = patient.latest_record

    # Summary stats
    stats_7d = HealthService.get_summary_stats(patient_id, days=7)
    stats_30d = HealthService.get_summary_stats(patient_id, days=30)

    # Chart data (14 days)
    chart_data = HealthService.get_chart_data(patient_id, days=14)

    # Active medications
    medications = Medication.query.filter_by(patient_id=patient_id, is_active=True).all()

    # Recent unread alerts
    alerts = (
        Alert.query
        .filter_by(patient_id=patient_id, is_resolved=False)
        .order_by(Alert.created_at.desc())
        .limit(10)
        .all()
    )

    # Risk calculation
    records = HealthRecord.query.filter_by(patient_id=patient_id).order_by(
        HealthRecord.recorded_at.desc()
    ).limit(7).all()
    records_dicts = [r.to_dict() for r in reversed(records)]
    risk = AgentService._calculate_risk_score(patient.to_dict(), records_dicts)

    # Wellness score
    wellness_score = None
    if latest:
        wellness_score = AgentService._calculate_wellness_score(latest.to_dict())

    # Unread alert count
    unread_count = Alert.query.filter_by(
        patient_id=patient_id, is_read=False, is_resolved=False
    ).count()

    # Watsonx status
    wx = WatsonxService()

    return render_template(
        "dashboard.html",
        patient=patient,
        all_patients=all_patients,
        latest=latest,
        stats_7d=stats_7d,
        stats_30d=stats_30d,
        chart_data=json.dumps(chart_data),
        medications=medications,
        alerts=alerts,
        risk=risk,
        wellness_score=wellness_score,
        unread_count=unread_count,
        watsonx_configured=wx.is_configured,
        get_risk_color=get_risk_color,
        get_severity_icon=get_severity_icon,
        active_page="dashboard",
    )


@dashboard_bp.route("/api/alerts/<int:patient_id>/read/<int:alert_id>", methods=["POST"])
def mark_alert_read(patient_id: int, alert_id: int):
    """Mark an alert as read."""
    from app_factory import db
    alert = Alert.query.get_or_404(alert_id)
    alert.is_read = True
    db.session.commit()
    return jsonify({"status": "ok"})


@dashboard_bp.route("/api/alerts/<int:patient_id>/resolve/<int:alert_id>", methods=["POST"])
def resolve_alert(patient_id: int, alert_id: int):
    """Resolve an alert."""
    from app_factory import db
    from datetime import datetime
    alert = Alert.query.get_or_404(alert_id)
    alert.is_resolved = True
    alert.resolved_at = datetime.utcnow()
    db.session.commit()
    return jsonify({"status": "ok"})


@dashboard_bp.route("/api/insights/<int:patient_id>")
def get_insights(patient_id: int):
    """AJAX endpoint: generate AI health insights."""
    patient = Patient.query.get_or_404(patient_id)
    records = (
        HealthRecord.query
        .filter_by(patient_id=patient_id)
        .order_by(HealthRecord.recorded_at.desc())
        .limit(10)
        .all()
    )
    records_dicts = [r.to_dict() for r in reversed(records)]
    result = AgentService.generate_insights(patient.to_dict(), records_dicts)
    return jsonify(result)
