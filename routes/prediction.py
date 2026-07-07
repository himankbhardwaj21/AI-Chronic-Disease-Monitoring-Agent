"""
routes/prediction.py — Feature 2: Predictive Disease Progression
"""

from flask import Blueprint, render_template, jsonify
from models.patient import Patient
from models.health_record import HealthRecord
from models.medication import Medication
from services.extended_agent_service import ExtendedAgentService
from services.health_service import HealthService
from utils.formatters import format_health_summary
import json

prediction_bp = Blueprint("prediction", __name__)


@prediction_bp.route("/<int:patient_id>")
def prediction_page(patient_id: int):
    patient = Patient.query.get_or_404(patient_id)
    all_patients = Patient.query.filter_by(is_active=True).all()
    records = (
        HealthRecord.query.filter_by(patient_id=patient_id)
        .order_by(HealthRecord.recorded_at.asc())
        .limit(60).all()
    )
    records_dicts = [r.to_dict() for r in records]

    result = None
    if records:
        result = ExtendedAgentService.predict_progression(patient.to_dict(), records_dicts)
        if result.get("prediction_content"):
            result["prediction_html"] = format_health_summary(result["prediction_content"])

    chart_data = HealthService.get_chart_data(patient_id, days=30)
    medications = Medication.query.filter_by(patient_id=patient_id, is_active=True).all()
    from services.agent_service import AgentService
    risk = AgentService._calculate_risk_score(patient.to_dict(), records_dicts)

    return render_template(
        "features/prediction.html",
        patient=patient,
        all_patients=all_patients,
        result=result,
        risk=risk,
        chart_data=json.dumps(chart_data),
        medications=medications,
        record_count=len(records),
        active_page="prediction",
    )


@prediction_bp.route("/api/<int:patient_id>/refresh", methods=["POST"])
def refresh_prediction(patient_id: int):
    patient = Patient.query.get_or_404(patient_id)
    records = (
        HealthRecord.query.filter_by(patient_id=patient_id)
        .order_by(HealthRecord.recorded_at.asc())
        .limit(60).all()
    )
    if not records:
        return jsonify({"error": "No health records found"}), 400
    result = ExtendedAgentService.predict_progression(
        patient.to_dict(), [r.to_dict() for r in records]
    )
    if result.get("prediction_content"):
        result["prediction_html"] = format_health_summary(result["prediction_content"])
    return jsonify(result)
